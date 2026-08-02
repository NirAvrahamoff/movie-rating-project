"""
api.py — CineScore Flask application.

Loads the trained Random Forest pipeline at startup and exposes two routes:
  GET  /          → serve the prediction form (index.html)
  POST /predict   → accept JSON form data, validate, predict, return rating
"""
import os
import joblib
from flask import Flask, render_template, request, jsonify
from assets_data_prep import prepare_features

app = Flask(__name__)

# ── Model loading (once at startup) ─────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')

try:
    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded — {model.n_features_in_} features expected.")
except Exception as exc:
    model = None
    print(f"[WARNING] Could not load model.pkl: {exc}")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _bad(message: str):
    """Return a 400 JSON error response."""
    return jsonify({'success': False, 'error': message}), 400


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if not request.is_json:
        return _bad('Content-Type must be application/json.')

    fd = request.get_json(silent=True) or {}

    # ── Layer 2: server-side validation ─────────────────────────────────────
    # The same rules are enforced on the frontend (Layer 1) so this layer
    # catches tampered requests and non-browser clients.

    # Rule 1 — Film title must not be blank
    title = fd.get('primaryTitle', '').strip()
    if not title:
        return _bad('Film title is required.')

    # Rule 2 — Release year: 1900–2050
    # prepare_data() clips values > 2025 to NaN internally (imputed by the
    # Pipeline's SimpleImputer), so years in 2026-2050 produce valid predictions.
    try:
        year = int(fd['startYear'])
    except (KeyError, TypeError, ValueError):
        return _bad('Release year must be a valid integer.')
    if not (1900 <= year <= 2050):
        return _bad('Release year must be between 1900 and 2050.')

    # Rule 3 — Runtime: 1–500 minutes
    try:
        runtime = int(fd['runtimeMinutes'])
    except (KeyError, TypeError, ValueError):
        return _bad('Runtime must be a valid integer.')
    if not (1 <= runtime <= 500):
        return _bad('Runtime must be between 1 and 500 minutes.')

    # Rule 4 — At least one genre must be selected
    genres = fd.get('genres', [])
    if not isinstance(genres, list) or len(genres) == 0:
        return _bad('At least one genre must be selected.')

    # ── Model inference ──────────────────────────────────────────────────────
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Ensure model.pkl is present in the project root.',
        }), 503

    try:
        features = prepare_features(fd)          # dict → 20-column DataFrame
        raw      = float(model.predict(features)[0])
        rating   = round(max(1.0, min(10.0, raw)), 1)   # clamp to [1.0, 10.0]

        return jsonify({'success': True, 'rating': rating, 'predicted_rating': rating, 'title': title})

    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)
