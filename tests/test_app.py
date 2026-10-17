import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "app")]

from features import FEATURES, prepare_data  # noqa: E402
import api  # noqa: E402

FILM = {"primaryTitle": "Predict Me If You Can", "startYear": 2027, "runtimeMinutes": 122,
        "genres": ["Documentary", "Action", "Crime"], "language": "English", "country": "United States"}


@pytest.fixture
def client():
    return api.app.test_client()


def test_prepare_data_returns_feature_columns_for_one_film():
    row = pd.DataFrame([{"primaryTitle": "Alien 3", "startYear": 1992, "runtimeMinutes": 114,
                         "genres": "['Horror', 'Sci-Fi']", "Language": "English", "Country": "United States"}])
    out = prepare_data(row)
    assert list(out.columns) == FEATURES
    assert out.loc[0, "is_sequel"] == 1 and out.loc[0, "genre_Sci-Fi"] == 1 and out.loc[0, "movie_age"] == 33


def test_future_year_is_treated_as_new_not_missing():
    row = pd.DataFrame([{"primaryTitle": "X", "startYear": 2030, "runtimeMinutes": 90, "genres": "Drama",
                         "Language": None, "Country": None}])
    assert prepare_data(row).loc[0, "movie_age"] == 0


def test_page_loads_with_all_genres(client):
    html = client.get("/").get_data(as_text=True)
    assert "Sci-Fi" in html and "Documentary" in html


def test_prediction_is_a_valid_rating(client):
    data = client.post("/predict", json=FILM).get_json()
    assert data["success"] and 1.0 <= data["rating"] <= 10.0


@pytest.mark.parametrize("change", [{"primaryTitle": " "}, {"startYear": 1800}, {"runtimeMinutes": 0}, {"genres": []}])
def test_invalid_input_is_rejected(client, change):
    assert client.post("/predict", json={**FILM, **change}).status_code == 400
