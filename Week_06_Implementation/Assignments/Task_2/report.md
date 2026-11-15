# Task 2 implementation report

Implemented `chunk_repository.py` and generated `chunks.jsonl` from the Task 1
`AI4SE_Playground` snapshot. The implementation uses only Python's standard
library and follows the architecture in `setup.md`.

## Design decisions

The target is **2,000 characters**, with a **4,000-character maximum**. This
encourages focused retrieval while allowing a moderately sized function or class
to stay intact. These are character limits, not embedding token limits; Task 3
must check its embedding model's limit.

Small files remain whole. Larger files are split using AST source positions,
including decorators and contiguous leading comments. Oversized classes split at
method boundaries; their headers, docstrings, attributes, and intervening source
remain represented. Method records retain qualified names such as
`InventoryLedger.reserve`. Adjacent small units can share a chunk up to the
target; mixed content has a null symbol. Methods remain separate so their
qualified names are retained.

Oversized units and files that fail parsing use line-based windows, with character
splitting for unusually long lines. Overlap is at most **200 characters**, only
within a unit's fallback windows, preferring complete trailing lines. Every
non-whitespace source character is covered. Whitespace-only gaps and files do not
need separate records.

JSONL provides a portable, inspectable snapshot for Tasks 3 and 4 without database
dependencies. Every record contains the source text, repository-relative path,
kind, symbol, line and character ranges, character count, and a deterministic
SHA-256 ID. Python encoding declarations are respected and line endings are
normalized to LF. Source is sliced rather than regenerated or executed.

Traversal includes tests and excludes version-control data, environments, caches,
and build outputs. As an additional precaution, symbolic links are skipped and
custom virtual environments are detected through `pyvenv.cfg`. Output is UTF-8
without a BOM and is replaced atomically only after validation succeeds.

## Actual results

Generated with Python 3.13.12 using the default settings:

| Measurement | Result |
| --- | ---: |
| Nonempty Python files processed | 26 |
| Empty Python files skipped | 1 |
| Chunks | 132 |
| Total characters stored in chunk text | 159,509 |
| Smallest chunk | 49 characters |
| Largest chunk | 3,871 characters |
| Mean chunk size | 1,208.40 characters |
| Median chunk size | 1,150 characters |
| Chunks at or below the 2,000-character target | 109 |
| Chunks above target and within maximum | 23 |
| Files requiring fallback windows | 0 |
| Files with parsing failures | 0 |

The dataset contains 4 file, 58 module/mixed, 30 class, 1 function, and 39 method
records, with 132 unique IDs. No fallback overlap was needed for this snapshot.
There were no material deviations from the planned chunking design. The test file
is an additional deliverable.

## Reproduction and validation

From the parent repository root:

```powershell
python Week_06_Implementation/Assignments/Task_2/chunk_repository.py
python -m unittest discover -s Week_06_Implementation/Assignments/Task_2 -p "test_*.py" -v
```

Default input and output paths resolve relative to the script, independently of
the caller's working directory. Overrides are available through `--repo-root`,
`--output`, `--target-size`, `--max-size`, and `--overlap`. Sizes must satisfy
`0 <= overlap < target_size <= max_size`. Explicit relative paths resolve against
the caller's working directory. The command prints a JSON summary of statistics
and fallback file paths.

Generation validates JSON round-trips, unique IDs, source slices, inclusive line
ranges, the maximum size, and coverage before replacing the destination. All
**10 regression tests passed**, including 100 seeded cases with varied line
lengths and sizes, syntax errors, long lines, class/method metadata, decorators,
async functions, source encodings, directory exclusions, repeat-run byte
equality, and preservation of existing output on read or replacement failures.
The first sandboxed test run could not access Windows temporary directories;
the approved rerun outside the sandbox passed.

The dataset is ready for embedding generation in Task 3. Embeddings and similarity
search are outside this task's scope.
