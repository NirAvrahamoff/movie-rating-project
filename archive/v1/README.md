# First version (2026 course submission)

The original notebooks, READMEs and app code as submitted for grading, kept for comparison. Paths inside them point to the old folder layout, so they will not run from here.

| Folder | Contents |
|---|---|
| `part2-model/` | `ML_Project.ipynb`, the graded modeling notebook, with its original outputs |
| `part3-web-app/` | The original Flask server and feature code |
| `part1-data-collection/`, `part2-model/`, `part3-web-app/` | The original READMEs |

The data collection notebook did not change apart from file paths, so it lives in `notebooks/01_data_collection.ipynb`.

## What the review found and what changed

| Review point | Current version |
|---|---|
| Titles, years and genres in the error and fairness analysis belonged to other films, because the index was reset after filtering and then used to look rows up in the unfiltered table | The original index is kept through the split, every lookup is by index, and an assertion checks the alignment |
| Error analysis blamed IMDb for a 9.5 rating of The Ant Bully that was really another film's | Every film in the analysis carries its IMDb ID; The Ant Bully is rated 5.8 and predicted 6.1 |
| Claims about errors were not tested quantitatively | Error by number of votes, the share of low-vote films among the largest errors, and the genre mix of the worst predictions are all measured |
| `is_english` duplicated the `Language = English` dummy | Removed |
| Little creativity in feature engineering | Ten more genres, six genre pairs and three title features; an ablation measures what each group adds |
| Binary and one-hot columns were not standardised, so Elastic Net coefficients were not comparable | Every column is standardised for the linear model; permutation importance on test data is added |
| Little discussion of feature importance | Explains why the models rank features differently and why the documentary interaction is negative |
