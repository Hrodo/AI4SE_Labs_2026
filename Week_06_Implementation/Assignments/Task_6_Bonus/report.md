# Task 6: Repository-aware source code generation

The current pipeline retrieves five similar code chunks and sends them, the task,
and the target module to an LLM. I would improve how it selects context and add
a feedback loop to check the generated code.

## Suggested improvements

**Combine search methods.** Embedding matching should be one part of retrieval.
Our current hashed TF-IDF embeddings mainly match shared words. I would combine
exact lookup of files and symbols, keyword search, and semantic embeddings that
aim to find related concepts expressed in different words. Then I would rank the
combined results and remove duplicates.

**Choose the number of chunks dynamically.** Five chunks may be too many for a
simple method or too few for a method with several dependencies. Always include
the target and its essential definitions, then add relevant chunks while space
remains in the model's context. Stop when additional chunks add little value.

**Extend the existing structural chunking.** Our chunker already uses Python's
syntax tree to preserve functions and methods. I would also link each method to
its class, imports, and related definitions so missing context can be fetched.
Large methods should be split at statement boundaries, with sizes measured in
tokens rather than only characters.

## Proposed pipeline

1. Index the repository's source, symbols, and tests. Refresh changed files so
   retrieved code stays up to date.
2. Use the file, class, and method from `missing_code.json` to read the target,
   its surrounding code, and relevant tests directly.
3. Search for additional definitions and examples using the combined search
   methods. Remove duplicates and select context within a token budget.
4. Ask the LLM for a small patch to the target method and check its syntax and
   changed scope.
5. Run focused tests, then the full suite. Use failures for a limited number of
   repair attempts, fetching more context when needed.


