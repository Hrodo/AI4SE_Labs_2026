"""Evaluate Task 2 SQL predictions with balanced multiset result F1.

Run with Python 3 (standard library only): python path/to/Task_3/metric.py
"""

import argparse
import csv
import importlib.util
import json
import sqlite3
from collections import Counter
from pathlib import Path
from statistics import mean


HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE.parent / "Task_2" / "data"
RUNS = [
    (prompt.upper(), model, relative_path)
    for prompt in ("star", "icio", "ape")
    for model, relative_path in (
        ("GPT-6.1 Sol", f"restaurants_dataset_predictions_{prompt}.csv"),
        ("GPT-5.6 Sol", f"restaurants_dataset_predictions_{prompt}_old_model.csv"),
    )
]


def result_f1(expected, predicted):
    """Compare unordered multisets of complete rows, including duplicates.

    Both empty scores 1; one empty scores 0. Column order and values matter.
    """
    expected_counts = Counter(tuple(row) for row in expected)
    predicted_counts = Counter(tuple(row) for row in predicted)
    matched = sum((expected_counts & predicted_counts).values())
    denominator = len(expected) + len(predicted)
    return 2 * matched / denominator if denominator else 1.0


def balanced_f1(records):
    """Give equal weight to empty and nonempty reference-answer strata.

    If only one stratum exists, use its mean. Refuse an empty evaluation.
    """
    if not records:
        raise ValueError("Cannot evaluate an empty dataset")
    strata = [
        [row["f1"] for row in records if (row["expected_count"] == 0) == empty]
        for empty in (True, False)
    ]
    return mean(mean(scores) for scores in strata if scores)


def load_database(data_dir):
    """Reuse Task 2's schema/data parser without modifying its evaluator."""
    spec = importlib.util.spec_from_file_location(
        "task2_evaluator", data_dir / "evaluate_retrieval_predictions.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SCHEMA_PATH = data_dir / "restaurants-schema.csv"
    module.DATABASE_PATH = data_dir / "restaurants-db.txt"
    connection = module.load_database()
    connection.commit()
    connection.execute("PRAGMA query_only = ON")
    # Prevent prediction SQL from changing the database or connection settings.
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION,
               sqlite3.SQLITE_RECURSIVE}
    connection.set_authorizer(
        lambda action, *_args: sqlite3.SQLITE_OK
        if action in allowed else sqlite3.SQLITE_DENY
    )
    return connection


def execute_prediction(connection, sql):
    """Execute read-only SQL with a per-query SQLite instruction budget."""
    calls = 0

    def progress():
        nonlocal calls
        calls += 1
        return int(calls > 5000)  # Approximately five million VM instructions.

    connection.set_progress_handler(progress, 1000)
    try:
        cursor = connection.execute(sql)
        if cursor.description is None:
            raise sqlite3.OperationalError("Prediction did not return rows")
        return cursor.fetchall()
    finally:
        connection.set_progress_handler(None, 0)


def read_csv(path):
    csv.field_size_limit(1_000_000_000)
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def evaluate(connection, labels, predictions):
    if len(labels) != len(predictions):
        raise ValueError("Prediction count must equal label count")
    records = []
    for index, (label, prediction) in enumerate(zip(labels, predictions), start=1):
        # Sequence matching preserves repeated question occurrences.
        if label["question"] != prediction["question"]:
            raise ValueError(f"Question mismatch at prediction {index}")
        expected = json.loads(label["result"])
        if not isinstance(expected, list) or any(
            not isinstance(row, list) or len(row) != 2 for row in expected
        ):
            raise ValueError(f"Invalid expected result at question {index}")
        error = ""
        try:
            predicted = execute_prediction(connection, prediction["predicted_sql"])
        except sqlite3.Error as exc:
            predicted = []
            error = str(exc)
        exact = not error and Counter(map(tuple, expected)) == Counter(map(tuple, predicted))
        records.append({
            "question_index": index,
            "question": label["question"],
            "expected_count": len(expected),
            "predicted_count": "" if error else len(predicted),
            "f1": 0.0 if error else result_f1(expected, predicted),
            "exact_match": int(exact),
            "execution_error": error,
        })
    return records


def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def write_report(path, summaries, details):
    empty_count = summaries[0]["empty_questions"]
    nonempty_count = summaries[0]["nonempty_questions"]
    lines = [
        "# Task 3: Balanced result F1",
        "",
        "## What the metric measures",
        "",
        "The original **accuracy** metric counts a query as correct only when it "
        "returns exactly the expected rows. **Result F1** also gives credit for "
        "partly correct answers and penalizes missing or extra restaurants.",
        "",
        "For example, if three restaurants are expected and the query returns "
        "two correct restaurants with no extras, its F1 is **80%**. Accuracy "
        "counts that query as incorrect.",
        "",
        "For each query:",
        "",
        "**F1 = 2 × matching rows / (expected rows + returned rows)**",
        "",
        "Each row contains a house number and restaurant name. Their values "
        "and column order must match; row order does not matter. Repeated rows "
        "are counted separately. If both answers are empty, F1 is 100%; if only "
        "one is empty, it is 0%. A query that fails to execute gets 0%.",
        "",
        "The proposed metric is **balanced result F1 (BR-F1)**. First calculate "
        "the average F1 for questions expecting no restaurants, then for questions "
        "expecting some restaurants. Average these two scores:",
        "",
        "**BR-F1 = (empty-answer average F1 + nonempty-answer average F1) / 2**",
        "",
        f"There are **{empty_count} empty answers** and **{nonempty_count} nonempty "
        "answers** in this dataset. Balancing gives each group equal weight, "
        "even though their sizes differ. F1 is an existing metric; balancing "
        "these two groups is the adaptation proposed here.",
        "",
        "BR-F1 **complements accuracy**: accuracy measures fully correct answers, "
        "while F1 shows how much of an answer is correct.",
        "",
        "## Results and comparison",
        "",
        "The six existing Task 2 prediction files were evaluated against the "
        "provided database and expected answers. No new model responses were generated. "
        "Average F1 below gives every question equal weight; BR-F1 gives the two "
        "answer groups equal weight.",
        "",
        "| Prompt | Model | Accuracy | Average F1 | BR-F1 |",
        "|---|---|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['prompt']} | {row['model']} | {row['accuracy']:.2%} | "
            f"{row['macro_f1']:.2%} | {row['balanced_f1']:.2%} |"
        )
    lines.append("")
    for model in ("GPT-6.1 Sol", "GPT-5.6 Sol"):
        group = [row for row in summaries if row["model"] == model]
        best = max(row["balanced_f1"] for row in group)
        winners = ", ".join(row["prompt"] for row in group
                            if abs(row["balanced_f1"] - best) < 1e-12)
        lines.extend([
            f"For **{model}**, {winners} achieved the highest BR-F1: **{best:.2%}**.",
            "",
        ])
    if all(row["empty_f1"] == 1 for row in summaries):
        lines.extend([
            "All runs answered the empty-answer questions correctly. Differences "
            "therefore come from questions expecting restaurants. Giving the "
            "perfectly answered empty group half the weight makes BR-F1 higher "
            "than average F1 here.",
            "",
        ])
    partial = sum(0 < row["f1"] < 1 for row in details)
    errors = sum(row["execution_errors"] for row in summaries)
    lines.extend([
        f"Across all six runs, **{partial} predictions received partial credit** "
        f"and **{errors} queries failed to execute**. F1 shows that some answers "
        "marked incorrect by accuracy still contain useful results.",
        "",
        "## Limits",
        "",
        "A query can return the right rows by chance on this database. The scores "
        "also depend on the expected answers being correct. Equal group weighting "
        "is a chosen preference, and the metric does not measure speed or SQL "
        "readability. One run per prompt and model is too little to establish "
        "reliable performance differences.",
        "",
        "## Run the calculation",
        "",
        "From the repository root, using Python 3 (no extra packages needed):",
        "",
        "```powershell",
        "python Week_03_Prompting/Assignments/Task_3/metric.py",
        "```",
        "",
        "The script writes `metric_summary.csv` (scores for each run), "
        "`metric_per_question.csv` (scores for each question), and this report. "
        "CSV scores range from 0 to 1; the report shows percentages.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    labels = read_csv(args.data_dir / "restaurants_dataset.csv")
    summaries, details = [], []
    connection = load_database(args.data_dir)
    try:
        for prompt, model, relative_path in RUNS:
            records = evaluate(connection, labels, read_csv(args.data_dir / relative_path))
            empty = [row["f1"] for row in records if row["expected_count"] == 0]
            nonempty = [row["f1"] for row in records if row["expected_count"] > 0]
            summaries.append({
                "prompt": prompt, "model": model, "predictions_file": relative_path,
                "questions": len(records), "empty_questions": len(empty),
                "nonempty_questions": len(nonempty),
                "accuracy": mean(row["exact_match"] for row in records),
                "macro_f1": mean(row["f1"] for row in records),
                "empty_f1": mean(empty) if empty else "",
                "nonempty_f1": mean(nonempty) if nonempty else "",
                "balanced_f1": balanced_f1(records),
                "execution_errors": sum(bool(row["execution_error"]) for row in records),
            })
            details.extend({"prompt": prompt, "model": model, **row} for row in records)
    finally:
        connection.close()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "metric_summary.csv", summaries)
    write_csv(args.output_dir / "metric_per_question.csv", details)
    write_report(args.output_dir / "output.md", summaries, details)
    for row in summaries:
        print(f"{row['prompt']:4} {row['model']:11} BR-F1={row['balanced_f1']:.4%} "
              f"accuracy={row['accuracy']:.4%} errors={row['execution_errors']}")


if __name__ == "__main__":
    main()
