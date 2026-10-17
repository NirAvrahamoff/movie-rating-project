# Data

## movies_dataset_part1–3.csv.xz (133,884 films)

The modeling dataset, split by rows into three xz-compressed parts to stay under GitHub's upload limit. It combines the course's IMDb extract with enrichment from Wikipedia and the OMDb API. To load it:

```python
from pathlib import Path
import pandas as pd
parts = sorted(Path("data").glob("movies_dataset_part*.csv.xz"))
raw = pd.concat([pd.read_csv(p, low_memory=False) for p in parts], ignore_index=True)
```

| Column | Description | Used in the model |
|---|---|---|
| `tconst` | IMDb ID (`https://www.imdb.com/title/<tconst>/`) | No, used to trace predictions back to films |
| `primaryTitle` | Title | Yes, for the title features |
| `startYear` | Release year | Yes |
| `genres` | Up to three IMDb genres | Yes |
| `lead_actors_ids` | IMDb IDs of lead actors | No |
| `runtimeMinutes` | Runtime | Yes |
| `averageRating` | IMDb rating, 1 to 10 (target) | Target |
| `Language`, `Country` | From OMDb or Wikipedia; missing for about 60% of films | Yes |
| `numVotes` | Number of IMDb votes | No: it accumulates after release. Used only to analyse errors |
| `budget`, `BoxOffice` | From Wikipedia, mixed currencies; missing for about 87% | No |
| `plot` | Short plot summary | No |

## qr_movies_5000.csv and qr_movies_5000_raw.csv

Our own contribution to the course dataset, built in [01_data_collection.ipynb](../notebooks/01_data_collection.ipynb): the 5,000 most-voted films whose titles start with Q or R, enriched by scraping Wikipedia and calling the OMDb API. The raw file is before cleaning the financial columns; the other is after converting them to USD millions.

IMDb data comes from the [IMDb non-commercial datasets](https://developer.imdb.com/non-commercial-datasets/) and is used here for non-commercial, educational purposes.
