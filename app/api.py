"""CineScore: a Flask app that predicts a film's IMDb rating from details known before release.

The saved model is a full scikit-learn Pipeline (preprocessing + model). Form values are
turned into features by src/features.py, the same function used in training.
"""
import sys
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "src"))
from features import COUNTRIES, GENRES, LANGUAGES, prepare_data  # noqa: E402

app = Flask(__name__)
MODEL_PATH = ROOT / "model.joblib"

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:  # the page still loads and explains the problem
    model = None
    print(f"[WARNING] Could not load {MODEL_PATH.name}: {exc}")


def bad(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


@app.get("/")
def index():
    return render_template("index.html", genres=GENRES, languages=LANGUAGES, countries=COUNTRIES)


@app.post("/predict")
def predict():
    fd = request.get_json(silent=True)
    if not isinstance(fd, dict):
        return bad("Request body must be JSON.")

    # Server-side validation mirrors the checks in main.js, for requests that bypass the form.
    title = str(fd.get("primaryTitle", "")).strip()[:200]
    if not title:
        return bad("Film title is required.")
    try:
        year, runtime = int(fd.get("startYear")), int(fd.get("runtimeMinutes"))
    except (TypeError, ValueError):
        return bad("Release year and runtime must be whole numbers.")
    if not 1900 <= year <= 2050:
        return bad("Release year must be between 1900 and 2050.")
    if not 1 <= runtime <= 300:
        return bad("Runtime must be between 1 and 300 minutes.")
    genres = fd.get("genres")
    if not isinstance(genres, list) or not genres:
        return bad("Select at least one genre.")
    genres = [g for g in genres if g in GENRES]
    if not genres:
        return bad("Unknown genre.")
    language = fd.get("language") if fd.get("language") in LANGUAGES + ["Other"] else "Other"
    country = fd.get("country") if fd.get("country") in COUNTRIES + ["Other"] else "Other"

    if model is None:
        return bad("The model is not available right now.", 503)

    row = pd.DataFrame([{"primaryTitle": title, "startYear": year, "runtimeMinutes": runtime,
                         "genres": ",".join(genres), "Language": language, "Country": country}])
    rating = round(min(10.0, max(1.0, float(model.predict(prepare_data(row))[0]))), 1)
    return jsonify({"success": True, "rating": rating, "predicted_rating": rating, "title": title})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
