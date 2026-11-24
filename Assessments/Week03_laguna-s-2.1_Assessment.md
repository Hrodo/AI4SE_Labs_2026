# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: Strong, complete work across all four tasks. Task 1 selects three legitimate prompting frameworks (STAR, ICIO, APE) from frompting.com and formulates well-structured prompts for SQL generation. Task 2 produces six prediction files with metadata, a thorough comparison report, and measured inference times. Task 3 introduces an original balanced-result-F1 metric with clean implementation, unit tests, and a report. Task 4 delivers a rigorous statistical analysis (exact McNemar, permutation tests, Holm correction, bootstrap CIs) with three generated figures, an explanation of prompt/model/coding-agent factors, and reproducible scripts. The three figure files could not be viewed (this model does not support image input), so they are judged from the accompanying text and the code that generates them, which is consistent. The only minor inconsistency is a reference to experiment_metadata.csv in Task 2 which is not present, but the actual deliverables (predictions, report, visualization script) are complete.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Three frameworks (STAR, ICIO, APE) were chosen from https://frompting.com/frameworks, excluding ROSES and zero-shot as required. Each prompt is tailored to the SQL-generation problem, and each choice is explained with the expected outcome. Deliverables include output.md and output.txt containing the formulated prompts and a report of the rationale and source. Fully meets all requirements.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: Six prediction CSV files (3 frameworks × 2 models) are stored in Task_2/data with filenames identifying the prompt and model, each with the correct question,predicted_sql header and 155 rows. output.md is a thorough report containing a results table, accuracy and inference-time comparison, visualization (task2_comparison.png), prediction-file inspection, and conclusions with limitations. Inference times are measured and reported. The report mentions experiment_metadata.csv which is absent, but all core deliverables and data are present.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: Proposes balanced result F1 (BR-F1), an original adaptation that stratifies questions by empty vs nonempty expected answers and averages F1 across the two strata. The metric is well-defended, complements (not replaces) accuracy, and is implemented in metric.py with read-only safeguards and a progress handler. Unit tests (test_metric.py) verify scoring conventions and execution behavior. The metric is calculated for all six Task 2 prediction sets, and output.md reports the comparison with tables and interpretation.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: Delivers a detailed analysis via analyze.py, which re-evaluates predictions, applies exact McNemar tests (accuracy) and exact paired permutation tests (F1, BR-F1) with Holm correction, computes 95% bootstrap confidence intervals, and generates three figures (metric_comparison.png, inference_time.png, error_heatmap.png). output.md provides a results table, all figures, a statistical-significance section (27 comparisons, none significant after correction), and an explanation of differences considering prompt wording, model version, and coding-agent factors. Unit tests (test_analysis.py) verify the statistical functions. Fully comprehensive and reproducible.
