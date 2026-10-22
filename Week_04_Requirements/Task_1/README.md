# Week 04 — Task 1

Python LangGraph network that converts a directory of software descriptions into
a consolidated, traceable requirements document. Three separate LLM nodes use
three distinct models from the assignment's allowed list.

## Setup and run (PowerShell)

From the repository root:

```powershell
cd Week_04_Requirements/Task_1
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
```

Edit `.env` locally and set `OPENAI_API_KEY` to the key supplied by the course.
If the course uses a proxy, also set its `OPENAI_BASE_URL`. Environment variables
take precedence over `.env`. The key file and virtual environment are ignored by
the repository. Do not commit credentials.

```powershell
.\.venv\Scripts\python.exe refine.py data/corpus --output-dir output
```

The default models are `gpt-4.1-nano` for extraction, `gpt-5-mini` for refinement,
and `gpt-4o-mini` for review. Override with `--extract-model`, `--refine-model`,
and `--review-model`; all three must be distinct and allowed by the assignment.
Model access and structured-output support must be available at your endpoint.

Another corpus can be supplied as the positional input directory. Supported UTF-8
files are `.txt`, `.md`, and `.eml`, discovered recursively. Email headers and full
inline conversations are preserved. This loader handles the provided plain-text
emails; it does not decode MIME attachments, HTML-only mail, PDFs, or Office files.
Keep outputs outside the input directory.

## Output

- `output/requirements.md`: the single human-readable requirements document,
  including priorities, sources, blacklist, questions, and verbatim evidence ledger.
- `output/requirements.json`: the corresponding structured artifact with unique
  requirement IDs, source filenames, candidates, review history, and API usage.
- `output/candidates.json`: all extracted candidates, including review discoveries.
- `output/draft_N.json`: each refinement pass, for inspection.
- `output/review_history.json`: all review feedback, grouped by pass and source chunk.
- `output/graph.mmd`: the actual compiled graph as a Mermaid diagram.
- `output/.cache/`: content-addressed successful structured API responses. Repeating
  the same requests reuses these results; changed prompts, data, models, schemas,
  or endpoint produce different cache keys. This is response reuse, not a LangGraph
  checkpoint or a guarantee of deterministic model output.

Exit code `0` means the final review approved the document. Exit code `2` means a
document was generated but still needs review after `--max-iterations` passes
(default: 3). Exit code `1` means execution failed. Inspect the generated document's
open questions even when the review approves it: approval does not resolve every
stakeholder decision or guarantee semantic correctness.

Successful calls are cached so an interrupted run can reuse completed work. To
request fresh responses, use a new output directory. API exceptions are reported
by type rather than dumping request bodies. The program sends corpus content to
the configured API endpoint and writes evidence/output locally.

If a model paraphrases an evidence quote, the workflow requests a corrected response
up to twice. Whitespace and added sentence-ending periods are normalized for matching, then the exact original source passage is stored. Words, decimal values, and other punctuation must match.
If evidence is still invalid after three attempts, it retains the candidate and
source filename with an empty quote and `quote_verified=false`. It flags affected
requirements and exports the document as `needs_review` (exit code 2); it never
presents the model's paraphrase as a verified quote. Exact quotations are an extra
quality check, while source-document tracing is preserved as the assignment requires.
An older cached invalid response can be repaired or flagged on rerun; you do not
need to delete the cache. `graph.mmd` is written before extraction begins;
`requirements.md` is written only when refinement and review reach export.

If a structured response is truncated (`LengthFinishReasonError`), the API adapter
retries with an explicit larger completion budget. Requests use 16,384 then 32,768
output tokens, or 8,192 then 16,384 for `gpt-4o-mini`. These are maximum budgets,
not a request to fill that many tokens. Existing complete cached responses remain
reusable. Truncated responses are never cached as successful results.

If extraction still exceeds the response limit, it automatically splits the input
chunk into smaller overlapping parts and extracts/reviews those parts. Splitting
is bounded to four levels and stops for chunks of 2,000 characters or less. If
the endpoint still truncates, the error identifies the stage and source; choose
another permitted model for that stage. Global refinement and review retry with
the larger budget but do not split the complete draft. Source/chunk names are
printed during extraction so the location of a failure is visible.

## Offline checks

No API key or network is needed after dependencies have been installed:

```powershell
.\.venv\Scripts\python.exe refine.py data/corpus --inspect
.\.venv\Scripts\python.exe -m unittest -v test_refine.py
```

`--inspect` validates file loading and prints a source manifest without calling a
model or writing a generated specification. Tests execute the real LangGraph with
scripted responses and temporary synthetic inputs; they do not generate a real
corpus submission. The saved [validation.json](validation.json) records the offline
checks performed during implementation.

See [report.md](report.md) for design decisions and assignment-spec coverage.
The implementation and offline checks are complete. A complete live API run and the actual
corpus requirements document remain pending, as requested.
