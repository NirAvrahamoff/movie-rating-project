"""Feature engineering shared by the modeling notebook and the CineScore web app.

Every feature here is known before a film is released: title, release year, runtime,
genres, language and country. Columns that accumulate after release (number of votes,
box office) and the target itself are never used.
"""
import ast
import re

import numpy as np
import pandas as pd

REFERENCE_YEAR = 2025  # last full year in the training data

# The 20 most common genres in the training data. Rarer genres are counted in num_genres only.
GENRES = [
    "Drama", "Comedy", "Romance", "Action", "Documentary", "Crime", "Thriller", "Horror",
    "Adventure", "Mystery", "Family", "Fantasy", "Biography", "History", "Sci-Fi", "Music",
    "Musical", "War", "Animation", "Sport",
]
LANGUAGES = ["English", "Hindi", "French", "Spanish", "Italian", "Japanese", "Tamil", "German"]
COUNTRIES = ["United States", "India", "United Kingdom", "France", "Italy", "Japan", "Canada"]

# Genre pairs whose combination behaves differently from each genre alone.
GENRE_PAIRS = [("Drama", "Romance"), ("Comedy", "Drama"), ("Horror", "Thriller"),
               ("Action", "Adventure"), ("Crime", "Drama"), ("Biography", "Documentary")]

SEQUEL_RE = re.compile(r"(?:\s(?:2|3|4|5|6|II|III|IV|V)$|\s(?:2|3|4|5|II|III|IV):|\bPart\s|\bChapter\s)")

NUMERIC = ["runtimeMinutes", "movie_age", "num_genres", "title_words", "documentary_runtime"]
BINARY = ([f"genre_{g}" for g in GENRES] + [f"pair_{a}_{b}" for a, b in GENRE_PAIRS]
          + ["is_sequel", "has_subtitle"])
CATEGORICAL = ["Language", "Country", "film_industry"]
FEATURES = NUMERIC + BINARY + CATEGORICAL


def parse_genres(value) -> list:
    """Genres arrive either as 'Drama,Comedy' or as "['Drama', 'Comedy']"."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    text = str(value).strip()
    if text.startswith("["):
        try:
            return [str(g).strip() for g in ast.literal_eval(text)]
        except (ValueError, SyntaxError):
            return []
    return [g.strip() for g in text.split(",") if g.strip()]


def film_industry(language, country) -> str:
    if country == "United States":
        return "Hollywood"
    if country == "India":
        return "Bollywood" if language == "Hindi" else "Indian_Other"
    if country in ("France", "Italy", "Spain", "Germany"):
        return "European"
    if country in ("Japan", "South Korea"):
        return "East_Asian"
    if language == "English":
        return "English_Other"
    return "Other"


def _clean_category(series: pd.Series, allowed: list) -> pd.Series:
    s = series.replace("Not Found", np.nan)
    return s.where(s.isna() | s.isin(allowed), "Other")


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Turn raw rows (dataset schema) into the model's feature matrix, in FEATURES order.

    The function is row-wise and stateless, so it gives the same result on one film
    in the web app as on the full dataset. Anything learned from data (imputation,
    scaling, encoding) happens inside the sklearn Pipeline, on training folds only.
    """
    out = pd.DataFrame(index=df.index)

    year = pd.to_numeric(df.get("startYear"), errors="coerce")
    year = year.where(year >= 1900)                  # 0 and other placeholders become missing
    year = year.clip(upper=REFERENCE_YEAR)           # an upcoming film is treated as brand new
    runtime = pd.to_numeric(df.get("runtimeMinutes"), errors="coerce")
    runtime = runtime.where((runtime >= 1) & (runtime <= 300))
    out["runtimeMinutes"] = runtime
    out["movie_age"] = REFERENCE_YEAR - year

    genre_lists = df["genres"].apply(parse_genres)
    out["num_genres"] = genre_lists.apply(len)
    for g in GENRES:
        out[f"genre_{g}"] = genre_lists.apply(lambda gl, g=g: int(g in gl))
    for a, b in GENRE_PAIRS:
        out[f"pair_{a}_{b}"] = out[f"genre_{a}"] * out[f"genre_{b}"]
    out["documentary_runtime"] = out["genre_Documentary"] * runtime.fillna(0)

    title = df.get("primaryTitle", pd.Series("", index=df.index)).fillna("").astype(str)
    out["title_words"] = title.str.split().str.len()
    out["is_sequel"] = title.str.contains(SEQUEL_RE).astype(int)
    out["has_subtitle"] = title.str.contains(":").astype(int)

    raw_lang = df.get("Language").replace("Not Found", np.nan)
    raw_country = df.get("Country").replace("Not Found", np.nan)
    out["film_industry"] = [film_industry(l, c) for l, c in zip(raw_lang, raw_country)]
    out["Language"] = _clean_category(raw_lang, LANGUAGES)
    out["Country"] = _clean_category(raw_country, COUNTRIES)
    return out[FEATURES]
