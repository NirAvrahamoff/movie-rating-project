import ast
import numpy as np
import pandas as pd

# Cell 3: prepare_data — Cleaning + Feature Engineering

TOP_GENRES = [
    'Drama','Comedy','Documentary','Romance','Action',
    'Crime','Thriller','Horror','Adventure','Family'
]
TOP_LANGS = ['English','Hindi','French','Spanish','Italian',
             'Japanese','Tamil','German']
TOP_COUNTRIES = ['United States','India','United Kingdom',
                 'France','Italy','Japan','Canada']


def _parse_genres(genre_str: str) -> list:
    """Parse genres from 'Drama,Comedy' or "['Drama','Comedy']" formats."""
    if pd.isna(genre_str): return []
    g = str(genre_str).strip()
    if g.startswith('['):
        try: return ast.literal_eval(g)
        except: return []
    return [x.strip() for x in g.split(',') if x.strip()]


def _get_film_industry(lang, country) -> str:
    """Map Language + Country → film industry label."""
    if pd.isna(country): country = None
    if pd.isna(lang):    lang    = None
    if country == 'United States':                      return 'Hollywood'
    if country == 'India' and lang == 'Hindi':          return 'Bollywood'
    if country == 'India':                              return 'Indian_Other'
    if country in ['France','Italy','Spain','Germany']: return 'European'
    if country in ['Japan','South Korea']:              return 'East_Asian'
    if lang == 'English':                               return 'English_Other'
    return 'Other'


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw movies_dataset DataFrame into a model-ready feature matrix.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input matching movies_dataset.csv structure.

    Returns
    -------
    pd.DataFrame
        Processed feature matrix — no target column, no leakage columns.

    Data Leakage Prevention
    -----------------------
    Excluded (unavailable before film release):
        averageRating, numVotes, BoxOffice, budget,
        plot, lead_actors_ids, tconst, primaryTitle
    All scaling/imputation performed ONLY on training folds
    inside the sklearn Pipeline — never on the full dataset.
    """
    out = df.copy()

    # 0. Drop temporary EDA columns created outside this function
    TEMP_COLS = ['rt_bin', 'ng', 'rt_cat', '_rt_bin']
    out = out.drop(columns=[c for c in TEMP_COLS if c in out.columns])

    # 1. Drop leakage & irrelevant columns
    DROP_COLS = ['averageRating','numVotes','BoxOffice','budget',
                 'plot','lead_actors_ids','tconst','primaryTitle']
    out = out.drop(columns=[c for c in DROP_COLS if c in out.columns])

    # 2. startYear — clip anomalies
    out['startYear'] = pd.to_numeric(out['startYear'], errors='coerce')
    out.loc[out['startYear'] < 1900, 'startYear'] = np.nan
    out.loc[out['startYear'] > 2025, 'startYear'] = np.nan

    # 3. runtimeMinutes
    out['runtimeMinutes'] = pd.to_numeric(out['runtimeMinutes'], errors='coerce')
    out.loc[out['runtimeMinutes'] > 300, 'runtimeMinutes'] = np.nan
    out.loc[out['runtimeMinutes'] < 1,   'runtimeMinutes'] = np.nan

    # 4. Language & Country — normalise sentinel values
    out['Language'] = out['Language'].replace('Not Found', np.nan)
    out['Country']  = out['Country'].replace('Not Found', np.nan)

    # 5. FE-5: film_industry (before collapsing Language/Country)
    out['film_industry'] = out.apply(
        lambda r: _get_film_industry(r.get('Language'), r.get('Country')), axis=1)

    # 6. Genres — multi-hot encode top 10
    genre_lists = out['genres'].apply(_parse_genres)
    for genre in TOP_GENRES:
        out[f'genre_{genre}'] = genre_lists.apply(lambda gl: int(genre in gl))
    out = out.drop(columns=['genres'])

    # 7. Language — top-N + Other
    out['Language'] = out['Language'].apply(
        lambda x: x if x in TOP_LANGS else ('Other' if pd.notna(x) else np.nan))

    # 8. Country — top-N + Other
    out['Country'] = out['Country'].apply(
        lambda x: x if x in TOP_COUNTRIES else ('Other' if pd.notna(x) else np.nan))

    # FE-1: movie_age
    out['movie_age'] = 2025 - out['startYear']

    # FE-2: num_genres
    out['num_genres'] = genre_lists.apply(len)

    # FE-3: is_english
    out['is_english'] = (out['Language'] == 'English').astype(int)

    # FE-4: runtime_bin  (0=Short / 1=Medium / 2=Long)
    def _runtime_bin(r):
        if pd.isna(r): return np.nan
        if r < 80:     return 0
        if r <= 120:   return 1
        return 2
    out['runtime_bin'] = out['runtimeMinutes'].apply(_runtime_bin)

    # FE-6: documentary_runtime — INTERACTION TERM
    # Documentaries tend to be longer AND rated higher.
    # Their product isolates a high-signal segment.
    out['documentary_runtime'] = (
        out['genre_Documentary'] * out['runtimeMinutes'].fillna(0)
    )

    return out


# ── Inference bridge ──────────────────────────────────────────────────────────
# Exact column order the trained Pipeline expects (from model.feature_names_in_)
FEATURE_COLUMNS = [
    'startYear', 'runtimeMinutes', 'Language', 'Country', 'film_industry',
    'genre_Drama', 'genre_Comedy', 'genre_Documentary', 'genre_Romance',
    'genre_Action', 'genre_Crime', 'genre_Thriller', 'genre_Horror',
    'genre_Adventure', 'genre_Family',
    'movie_age', 'num_genres', 'is_english', 'runtime_bin', 'documentary_runtime',
]


def prepare_features(form_data: dict) -> pd.DataFrame:
    """Convert an HTML form submission dict → model-ready 20-column DataFrame.

    Builds a minimal raw row that mirrors the movies_dataset.csv schema, delegates
    all feature engineering to prepare_data() (identical to training time), then
    returns columns in the exact order the Pipeline's ColumnTransformer expects.
    """
    genres = form_data.get('genres', [])
    if isinstance(genres, str):
        genres = [genres]

    # Construct the minimal raw DataFrame prepare_data() requires.
    # DROP_COLS / TEMP_COLS use `if c in out.columns`, so absent columns are safe.
    raw = pd.DataFrame([{
        'startYear':      form_data.get('startYear', 2024),
        'runtimeMinutes': form_data.get('runtimeMinutes', 100),
        'Language':       form_data.get('language', 'English'),   # form sends lowercase
        'Country':        form_data.get('country', 'United States'),
        'genres':         ','.join(genres),                        # _parse_genres handles CSV
    }])

    processed = prepare_data(raw)
    return processed[FEATURE_COLUMNS]
