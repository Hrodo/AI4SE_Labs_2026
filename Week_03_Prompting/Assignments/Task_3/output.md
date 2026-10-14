# Task 3: Balanced result F1

## What the metric measures

The original **accuracy** metric counts a query as correct only when it returns exactly the expected rows. **Result F1** also gives credit for partly correct answers and penalizes missing or extra restaurants.

For example, if three restaurants are expected and the query returns two correct restaurants with no extras, its F1 is **80%**. Accuracy counts that query as incorrect.

For each query:

**F1 = 2 × matching rows / (expected rows + returned rows)**

Each row contains a house number and restaurant name. Their values and column order must match; row order does not matter. Repeated rows are counted separately. If both answers are empty, F1 is 100%; if only one is empty, it is 0%. A query that fails to execute gets 0%.

The proposed metric is **balanced result F1 (BR-F1)**. First calculate the average F1 for questions expecting no restaurants, then for questions expecting some restaurants. Average these two scores:

**BR-F1 = (empty-answer average F1 + nonempty-answer average F1) / 2**

There are **43 empty answers** and **112 nonempty answers** in this dataset. Balancing gives each group equal weight, even though their sizes differ. F1 is an existing metric; balancing these two groups is the adaptation proposed here.

BR-F1 **complements accuracy**: accuracy measures fully correct answers, while F1 shows how much of an answer is correct.

## Results and comparison

The six existing Task 2 prediction files were evaluated against the provided database and expected answers. No new model responses were generated. Average F1 below gives every question equal weight; BR-F1 gives the two answer groups equal weight.

| Prompt | Model | Accuracy | Average F1 | BR-F1 |
|---|---|---:|---:|---:|
| STAR | GPT-6.1 Sol | 94.84% | 98.51% | 98.97% |
| STAR | GPT-5.6 Sol | 89.68% | 96.36% | 97.48% |
| ICIO | GPT-6.1 Sol | 94.84% | 98.51% | 98.97% |
| ICIO | GPT-5.6 Sol | 94.84% | 98.51% | 98.97% |
| APE | GPT-6.1 Sol | 94.84% | 98.51% | 98.97% |
| APE | GPT-5.6 Sol | 94.84% | 98.51% | 98.97% |

For **GPT-6.1 Sol**, STAR, ICIO, APE achieved the highest BR-F1: **98.97%**.

For **GPT-5.6 Sol**, ICIO, APE achieved the highest BR-F1: **98.97%**.

All runs answered the empty-answer questions correctly. Differences therefore come from questions expecting restaurants. Giving the perfectly answered empty group half the weight makes BR-F1 higher than average F1 here.

Across all six runs, **44 predictions received partial credit** and **0 queries failed to execute**. F1 shows that some answers marked incorrect by accuracy still contain useful results.

## Limits

A query can return the right rows by chance on this database. The scores also depend on the expected answers being correct. Equal group weighting is a chosen preference, and the metric does not measure speed or SQL readability. One run per prompt and model is too little to establish reliable performance differences.

## Run the calculation

From the repository root, using Python 3 (no extra packages needed):

```powershell
python Week_03_Prompting/Assignments/Task_3/metric.py
```

The script writes `metric_summary.csv` (scores for each run), `metric_per_question.csv` (scores for each question), and this report. CSV scores range from 0 to 1; the report shows percentages.
