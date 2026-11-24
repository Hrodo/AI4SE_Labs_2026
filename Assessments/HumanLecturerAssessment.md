# Assessment by human lecturer

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: Breakdown below

## Task 1
- Awarded: 1b
- Commentary: nice choices; for alternatives look up think tags, CoT, few-shot prompting

## Task 2
- Awarded: 1b
- Commentary: great that you compared several models and even repeated the experiments 6x (where are they stored tho? or were the responses identical across all runs?) - that considerably improves relevance of your findings; a violin plot of individual inference times might have been nice; notice that all model x prompt combinations handle prediction on line 67 correctly (force empty result set) except STAR with the older model

## Task 3
- Awarded: 1b
- Commentary: F1 is a good idea for classification/retrieval tasks; appreciate the nuance in different F1 variations here; but since we are already considering different F1 variations, it might be more interesting to observe both empty-set F1 and non-empty-set F1 rather than crunching it into an average -> because although the BR-F1 may be a little more informative than F1, but based on that, will you know whether to focus in improving your results with empty result set cases or the non-empty cases?

## Task 4
- Awarded: 2b
- Commentary: nice comparison and usage of statistical tests; heatmap is an interesting visualisation idea here; in most scenarios, it is good to consider using parametric tests first as long as the requirements for them are met (e.g. data normality, which you discover by using normality statistical tests)