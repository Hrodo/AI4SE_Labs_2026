"""Re-evaluate Task 2 predictions and generate the Task 4 analysis and figures."""

import argparse
import csv
import importlib.util
import itertools
import math
from pathlib import Path
from statistics import mean

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "Task_2" / "data"
MODELS = ("GPT-6.1 Sol", "GPT-5.6 Sol")
PROMPTS = ("STAR", "ICIO", "APE")
# Recorded whole-run times from Task 2/output.md. These are not new measurements.
TIMES = {("STAR", MODELS[0]): 119, ("STAR", MODELS[1]): 111,
         ("ICIO", MODELS[0]): 60, ("ICIO", MODELS[1]): 61,
         ("APE", MODELS[0]): 67, ("APE", MODELS[1]): 49}
METRICS = ("accuracy", "macro_f1", "balanced_f1")
NAMES = {"accuracy": "Accuracy", "macro_f1": "Average F1", "balanced_f1": "BR-F1"}


def load_metric():
    spec = importlib.util.spec_from_file_location("task3_metric", HERE.parent / "Task_3" / "metric.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mcnemar(b, c):
    """Two-sided exact binomial McNemar test of discordant outcomes."""
    n = b + c
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n) if n else 1.0


def permutation_p(differences):
    """Exact paired sign-flip test, two-sided absolute mean statistic.

    Tied pairs cannot affect the statistic; enumerate only nonzero differences.
    Refuse infeasible enumeration rather than silently change the test.
    """
    nonzero = np.asarray([d for d in differences if abs(d) > 1e-14])
    if len(nonzero) > 24:
        raise ValueError("More than 24 discordant F1 pairs; exact enumeration is too large")
    if not len(nonzero):
        return 1.0
    sums = np.array([0.0])
    for difference in nonzero:
        sums = np.concatenate((sums + difference, sums - difference))
    return float(np.mean(np.abs(sums) >= abs(nonzero.sum()) - 1e-12))


def holm(pvalues):
    """Holm step-down adjusted p-values, returned in original order."""
    order = sorted(range(len(pvalues)), key=pvalues.__getitem__)
    result, previous = [0.0] * len(pvalues), 0.0
    for rank, index in enumerate(order):
        previous = max(previous, min(1.0, (len(pvalues) - rank) * pvalues[index]))
        result[index] = previous
    return result


def paired_ci(differences, empty, balanced, seed, resamples):
    """Paired percentile bootstrap; BR-F1 preserves the two reference strata."""
    rng = np.random.default_rng(seed)
    differences = np.asarray(differences)
    if balanced:
        samples = []
        for mask in (empty, ~empty):
            values = differences[mask]
            samples.append(values[rng.integers(len(values), size=(resamples, len(values)))].mean(axis=1))
        estimates = (samples[0] + samples[1]) / 2
    else:
        estimates = differences[rng.integers(len(differences), size=(resamples, len(differences)))].mean(axis=1)
    return tuple(float(value) for value in np.quantile(estimates, [0.025, 0.975]))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def evaluate():
    metric = load_metric()
    labels = metric.read_csv(DATA / "restaurants_dataset.csv")
    connection = metric.load_database(DATA)
    groups, summaries, predictions = {}, [], {}
    try:
        for prompt, model, relative in metric.RUNS:
            key = (prompt, model)
            predictions[key] = metric.read_csv(DATA / relative)
            rows = metric.evaluate(connection, labels, predictions[key])
            groups[key] = rows
            empty = [r for r in rows if r["expected_count"] == 0]
            nonempty = [r for r in rows if r["expected_count"] > 0]
            summaries.append({
                "prompt": prompt, "model": model, "predictions_file": relative,
                "questions": len(rows), "correct": sum(r["exact_match"] for r in rows),
                "accuracy": mean(r["exact_match"] for r in rows),
                "macro_f1": mean(r["f1"] for r in rows),
                "empty_f1": mean(r["f1"] for r in empty),
                "nonempty_f1": mean(r["f1"] for r in nonempty),
                "balanced_f1": metric.balanced_f1(rows),
                "partial_credit": sum(0 < r["f1"] < 1 for r in rows),
                "zero_f1": sum(r["f1"] == 0 for r in rows),
                "execution_errors": sum(bool(r["execution_error"]) for r in rows),
                "recorded_time_seconds": TIMES[key],
            })
    finally:
        connection.close()
    # Catch stale Task 3 artifacts instead of reporting inconsistent experiments.
    saved = metric.read_csv(HERE.parent / "Task_3" / "metric_per_question.csv")
    current = {(p, m, r["question_index"]): r for (p, m), rows in groups.items() for r in rows}
    if len(saved) != len(current):
        raise ValueError("Task 3 question count differs from fresh evaluation")
    seen = set()
    for r in saved:
        key = (r["prompt"], r["model"], int(r["question_index"]))
        if key in seen:
            raise ValueError(f"Duplicate Task 3 record: {key}")
        seen.add(key)
        fresh = current[key]
        if (r["question"] != fresh["question"] or
                int(r["expected_count"]) != fresh["expected_count"] or
                r["predicted_count"] != str(fresh["predicted_count"]) or
                r["execution_error"] != fresh["execution_error"] or
                abs(float(r["f1"]) - fresh["f1"]) > 1e-12 or
                int(r["exact_match"]) != fresh["exact_match"]):
            raise ValueError(f"Task 3 metrics are stale at {key}; regenerate them first")
    return groups, summaries, predictions


def comparisons(groups, seed, resamples):
    contrasts = [("prompt", (a, m), (b, m)) for m in MODELS for a, b in itertools.combinations(PROMPTS, 2)]
    contrasts += [("model", (p, MODELS[0]), (p, MODELS[1])) for p in PROMPTS]
    results, cache = [], {}
    for kind, a, b in contrasts:
        left, right = groups[a], groups[b]
        empty = np.array([r["expected_count"] == 0 for r in left])
        a_only = sum(x["exact_match"] and not y["exact_match"] for x, y in zip(left, right))
        b_only = sum(y["exact_match"] and not x["exact_match"] for x, y in zip(left, right))
        for name in METRICS:
            field = "exact_match" if name == "accuracy" else "f1"
            diff = np.array([x[field] - y[field] for x, y in zip(left, right)])
            balanced = name == "balanced_f1"
            weights = np.where(empty, 1 / (2 * empty.sum()), 1 / (2 * (~empty).sum())) if balanced else np.full(len(diff), 1 / len(diff))
            cache_key = (name, tuple(diff), tuple(empty))
            if cache_key not in cache:
                pvalue = mcnemar(a_only, b_only) if name == "accuracy" else permutation_p(diff * weights)
                cache[cache_key] = (pvalue, paired_ci(diff, empty, balanced, seed, resamples))
            pvalue, (low, high) = cache[cache_key]
            results.append({
                "comparison_type": kind, "run_a": " / ".join(a), "run_b": " / ".join(b),
                "metric": name, "difference_pp": float(diff @ weights * 100),
                "ci95_low_pp": low * 100, "ci95_high_pp": high * 100,
                "a_only_correct": a_only, "b_only_correct": b_only,
                "nonzero_pairs": int(np.count_nonzero(np.abs(diff) > 1e-14)),
                "raw_p": pvalue,
            })
    for row, adjusted in zip(results, holm([r["raw_p"] for r in results])):
        row["holm_p"] = adjusted
        row["significant_005"] = adjusted < 0.05
    return results


def figures(output, summaries, groups):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    colors = ("#2563eb", "#ea580c")
    lookup = {(r["prompt"], r["model"]): r for r in summaries}
    x = np.arange(3)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
    for axis, metric in zip(axes, METRICS):
        for j, model in enumerate(MODELS):
            values = [lookup[p, model][metric] * 100 for p in PROMPTS]
            bars = axis.bar(x + (j - .5) * .36, values, width=.36, color=colors[j], label=model)
            axis.bar_label(bars, labels=[f"{v:.2f}" for v in values], fontsize=8, padding=3)
        axis.set(xticks=x, xticklabels=PROMPTS, ylim=(0, 110), yticks=np.arange(0, 101, 20), title=NAMES[metric], ylabel="Score (%)")
        axis.grid(axis="y", alpha=.2)
        axis.set_axisbelow(True)
    axes[0].legend(loc="lower left")
    fig.savefig(output / "metric_comparison.png", dpi=180)
    plt.close(fig)
    fig, axis = plt.subplots(figsize=(8, 4), layout="constrained")
    for j, model in enumerate(MODELS):
        values = [lookup[p, model]["recorded_time_seconds"] for p in PROMPTS]
        bars = axis.bar(x + (j - .5) * .36, values, width=.36, color=colors[j], label=model)
        axis.bar_label(bars, padding=3)
    axis.set(xticks=x, xticklabels=PROMPTS, ylim=(0, 140), ylabel="Whole-run time (seconds)", title="Recorded time: one observation per run")
    axis.legend()
    fig.savefig(output / "inference_time.png", dpi=180)
    plt.close(fig)
    indices = [i for i in range(len(next(iter(groups.values())))) if any(rows[i]["exact_match"] == 0 for rows in groups.values())]
    values = np.array([[rows[i]["f1"] for i in indices] for rows in groups.values()])
    fig, axis = plt.subplots(figsize=(14, 4), layout="constrained")
    image = axis.imshow(values, vmin=0, vmax=1, cmap="RdYlGn", aspect="auto")
    axis.set(xticks=np.arange(len(indices)), xticklabels=[i + 1 for i in indices],
             yticks=np.arange(len(groups)), yticklabels=[" / ".join(key) for key in groups],
             xlabel="Question index (only questions with at least one failure)", title="Per-question result F1: shared and distinct failures")
    fig.colorbar(image, ax=axis, label="F1")
    fig.savefig(output / "error_heatmap.png", dpi=180)
    plt.close(fig)


def report(output, summaries, groups, comparisons, predictions, seed, resamples):
    def table(headers, rows):
        return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)] + ["| " + " | ".join(map(str, row)) + " |" for row in rows])

    summary_table = table(["Prompt", "Model", "Correct / 155", "Accuracy", "Average F1", "BR-F1", "Time (s)"], [
        [r["prompt"], r["model"], f'{r["correct"]}/155', *(f'{r[m]:.2%}' for m in METRICS), r["recorded_time_seconds"]] for r in summaries])
    selected = [r for r in comparisons if r["comparison_type"] == "model" and r["run_a"].startswith("STAR")]
    tests_table = table(["Metric", "Difference (pp)", "Raw p", "Adjusted p"], [
        [NAMES[r["metric"]], f'{r["difference_pp"]:+.3f}', f'{r["raw_p"]:.4f}', f'{r["holm_p"]:.4f}'] for r in selected])
    significance = "None of the 27 tests found a significant difference after correction." if not any(r["significant_005"] for r in comparisons) else "Some tests found significant differences after correction; see the full results CSV."
    document = f"""# Task 4: Comparing the prompts

## Setup and metrics

I compared the STAR, ICIO, and APE prompts from [Task_1/output.txt](../Task_1/output.txt) using GPT-6.1 Sol and GPT-5.6 Sol. Each run answered the same 155 restaurant questions by generating SQL. I reused the Task 2 predictions, ran them against the database, and checked all 930 question scores against Task 3.

All six prediction files are now in [Task_2/data](../Task_2/data/). Files named `restaurants_dataset_predictions_{{star,icio,ape}}.csv` use GPT-6.1; files ending in `_old_model.csv` use GPT-5.6.

- **Accuracy:** how often the returned rows exactly match the expected answer.
- **Average F1:** gives partial credit when some returned rows are correct. Extra or missing rows lower the score.
- **BR-F1:** averages F1 for empty answers and nonempty answers, giving each group half the weight.

## Results

{summary_table}

![Scores for each prompt and model](metric_comparison.png)

Five runs have the same scores on every question. STAR with GPT-5.6 answers eight fewer questions correctly. Compared with the other runs, it loses 5.16 percentage points of accuracy, 2.16 points of average F1, and 1.49 points of BR-F1.

All runs answer the 43 empty-answer questions correctly. The differences come from the 112 questions expecting restaurants. BR-F1 is higher than average F1 because it gives more weight to the perfectly answered empty group. No SQL query fails to execute, so the errors concern what the queries return.

![Recorded time for each run](inference_time.png)

At the highest scores, ICIO is fastest on GPT-6.1 (60 seconds), and APE is fastest on GPT-5.6 (49 seconds). STAR is slowest on both. These are whole-run times from Task 2, including possible agent tool work. With only one measurement per run, the speed differences cannot be tested reliably.

## Statistical significance

Because every run answers the same questions, I compared results question by question. I used the exact McNemar test for accuracy and an exact paired permutation test for F1 and BR-F1. These test whether the observed differences provide evidence against equal performance.

I tested each prompt pair within each model and each model pair within each prompt: nine comparisons across three metrics, or 27 tests. Holm correction accounts for testing several differences. A corrected p-value below 0.05 counts as significant.

The table shows STAR GPT-6.1 minus STAR GPT-5.6. Differences are in percentage points (pp).

{tests_table}

The other nonzero comparisons are STAR versus ICIO or APE on GPT-5.6. They have the same p-values because ICIO and APE have identical scores. Every remaining comparison has zero difference and p = 1. {significance} This means there is not enough evidence to claim a reliable difference; it does not prove the prompts are equally good.

Full test results and 95% confidence intervals are in [statistical_comparisons.csv](statistical_comparisons.csv). The intervals use {resamples:,} paired bootstrap samples with seed {seed}. The F1 intervals narrowly exclude zero, but the exact tests do not reach significance. The methods differ; the decision above follows the corrected exact tests.

## Why the results differ

![F1 for questions where at least one run was incorrect](error_heatmap.png)

**Prompt:** All three prompts ask for SQLite SELECT queries, the same two output columns, and a CSV that preserves the questions and their order. This shared task may explain the similar scores. STAR explicitly asks the agent to identify joins and filters and verify each query. ICIO gives the most detailed output-format requirements. APE states the action, purpose, and expected file more briefly. These differences could affect how the agent works, but one run per combination cannot show which wording caused an error.

**Model:** STAR GPT-5.6 misses cuisine filters in questions 47-50. For question 47, it returns 11 restaurants instead of the expected one, giving F1 of 16.67%. It also often uses `LOCATION.CITY_NAME` where the newer STAR queries use `RESTAURANT.CITY_NAME`. This changes city and region results. The older STAR run gets six questions right that the newer run misses, but loses fourteen others, leaving eight fewer correct answers overall. ICIO and APE show no score difference between models.

**Coding agent:** The agent reads files, uses the schema, and writes the CSV. Its tool choices, checks, and session history may affect quality and time. There are no action logs to measure these effects separately. Missing filters and different joins are visible in the SQL; their exact cause is uncertain.

**Dataset:** Question 66 asks "What is the lifes greates illusion?" but expects 2,696 restaurant rows. Five runs return nothing; older STAR returns 9,538 rows and gets partial credit. This unusual reference answer should be checked. It was kept unchanged for this comparison.

## Limits and practical choice

There is only one run per prompt and model, and many questions follow similar patterns. These tests describe the saved answers, not variation across repeated generations. More independent runs are needed to judge whether the differences repeat.

Based on the recorded scores and times, ICIO is the best observed choice for GPT-6.1 and APE for GPT-5.6. The timing uncertainty and lack of repeated runs limit this recommendation.

To regenerate the report and graphs from the repository root:

```powershell
python -m pip install -r Week_03_Prompting/Assignments/Task_4/requirements.txt
python Week_03_Prompting/Assignments/Task_4/analyze.py
```

The supporting files are [analysis_summary.csv](analysis_summary.csv), [statistical_comparisons.csv](statistical_comparisons.csv), and [error_details.csv](error_details.csv).
"""
    (output / "output.md").write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--resamples", type=int, default=10000)
    args = parser.parse_args()
    if args.resamples < 100:
        parser.error("--resamples must be at least 100")
    groups, summaries, predictions = evaluate()
    tests = comparisons(groups, args.seed, args.resamples)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "analysis_summary.csv", summaries)
    write_csv(args.output_dir / "statistical_comparisons.csv", tests)
    details = [{"prompt": p, "model": m, **r} for (p, m), rows in groups.items() for r in rows if not r["exact_match"]]
    write_csv(args.output_dir / "error_details.csv", details)
    figures(args.output_dir, summaries, groups)
    report(args.output_dir, summaries, groups, tests, predictions, args.seed, args.resamples)
    print(f"Verified {sum(len(r) for r in groups.values())} question scores against Task 3.")
    print(f"Generated report, 3 CSVs, and 3 figures in {args.output_dir}")
    print(f"Significant comparisons after Holm correction: {sum(r['significant_005'] for r in tests)}/{len(tests)}")


if __name__ == "__main__":
    main()
