# Movie Dataset Mining

> Data Mining course project — building a dataset of 5,000 movies with titles starting with **Q or R**, combining IMDb, Wikipedia scraping, and the OMDb API.

## Repository Structure

```
movie-dataset-mining/
│
├── Data_Mining_Project.ipynb  # Main notebook — full data collection pipeline    
├── dataset.csv                # Final cleaned dataset (5,000 movies, 13 columns)
├── dataset_raw.csv            # Raw data before financial cleaning
├── report.pdf                 # Full project report
└── README.md                  # This file
```

---

## Dataset Overview

The final dataset contains **5,000 movies** collected from three sources:

| Field | Type | Source |
|-------|------|--------|
| `tconst` | string | IMDb |
| `primaryTitle` | string | IMDb |
| `startYear` | int | IMDb |
| `genres` | list | IMDb |
| `lead_actors_ids` | list | IMDb |
| `runtimeMinutes` | int | IMDb |
| `averageRating` | float | IMDb |
| `numVotes` | int | IMDb |
| `Language` | string | OMDb / Wikipedia |
| `Country` | string | OMDb / Wikipedia |
| `budget` | float (USD millions) | Wikipedia |
| `BoxOffice` | float (USD millions) | Wikipedia |
| `plot` | string | OMDb / Wikipedia |

---

## How It Works

<div align="center">
<img src="https://raw.githubusercontent.com/NirAvrahamoff/movie-dataset-mining/f235dbdd664a70f89231b2a36ee4c4092eb62854/pipeline.png" width="900">
</div>

The data collection pipeline runs in 4 steps:

1. **Load** — Download IMDb public datasets (`title.basics`, `title.ratings`, `title.principals`)
2. **Filter** — Keep only movies starting with Q or R, released by 2024, between 60–300 minutes. Sort by `numVotes` and take the top 5,000
3. **Enrich** — For the first 1,000 movies: OMDb API for `Language`/`Country`/`plot`, Wikipedia for `budget`/`BoxOffice`. For movies 1,001–5,000: Wikipedia only
4. **Clean** — Standardize all financial values to USD millions, fix data types, export to CSV

---

## How to Run

### Requirements
- Python 3.8+
- Jupyter Notebook
  
- Libraries:
```bash
pip install pandas requests beautifulsoup4 python-dotenv
```

### Steps

1. Clone the repository:
```bash
git clone https://github.com/NirAvrahamoff/movie-dataset-mining.git
```

2. Open the notebook:
```bash
jupyter notebook Data_Mining_Project.ipynb
```

3. Create a `.env` file in the project folder:
 ```
OMDB_API_KEY=your_key_here
```
> You can get a free key at https://www.omdbapi.com/


4. Run all cells in order.

> ⚠️ **Note:** The full pipeline takes several hours to run due to web scraping. The final `dataset.csv` is already included in the repository so you don't need to re-run everything.

---

## Missing Values Summary

| Column | Missing % |
|--------|-----------|
| `tconst` | 0.00% |
| `primaryTitle` | 0.00% |
| `startYear` | 0.00% |
| `genres` | 0.16% |
| `lead_actors_ids` | 6.96% |
| `runtimeMinutes` | 0.00% |
| `averageRating` | 0.00% |
| `numVotes` | 0.00% |
| `Language` | 44.08% |
| `Country` | 43.64% |
| `budget` | 83.58% |
| `BoxOffice` | 79.28% |
| `plot` | 51.88% |

---

## Notes

- The OMDb API key is stored in a `.env` file (not included in the repository). Create one with your own key from https://www.omdbapi.com/
- `budget` and `BoxOffice` high missingness is expected — most films do not publicly disclose financial data.
- `Language` and `Country` missingness is due to movies without a dedicated Wikipedia page or with non-standard URL formats.
