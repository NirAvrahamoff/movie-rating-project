# CineScore — Movie Rating Predictor

A Flask web app that predicts IMDb-style movie ratings (1–10) using a trained Random Forest model.

---

## Preview

### Landing Page
![CineScore Hero](CineScore%20Hero.png)

### Prediction Form
![Film Details Form](Film%20Details%20Form.png)
---

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py
```

Open: http://localhost:5000

### ⚠️ Important: Port Configuration

By default, the app runs on **port 5000**.

**Mac users:** macOS uses port 5000 for AirPlay Receiver, which can cause 
a `403 Forbidden` error. If this happens:

- **Option 1:** Use `http://127.0.0.1:5000` instead of `http://localhost:5000`
- **Option 2:** Disable AirPlay Receiver:
  `System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off`

**Windows/Linux users:** No special configuration needed.

---

## How it works

Fill in the form with your film's details — title, year, runtime, genres, language, and country — then click **Predict Rating**.

![CineScore Preview](The%20Great%20Nir.png)

---

## Input Fields

| Field | Type | Range |
|---|---|---|
| Title | Text | Required |
| Release Year | Number | 1900–2050 |
| Runtime | Number (minutes) | 1–500 |
| Genres | Multi-select | At least one required |
| Language | Dropdown | English, Hindi, French, Spanish, Italian, Japanese, Tamil, German, Other |
| Country | Dropdown | United States, India, United Kingdom, France, Italy, Japan, Canada, Other |

---

## Files

| File | Description |
|---|---|
| `api.py` | Flask server |
| `assets_data_prep.py` | Feature engineering |
| `trained_model.pkl` | Trained model (place in project root) |
| `requirements.txt` | Dependencies |

