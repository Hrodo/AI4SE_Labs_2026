# Task 2: Chunking design and architecture

## Scope

Task 2 prepares the repository cloned in Task 1 for retrieval-augmented code generation. A Python script will read the repository, split its source into useful chunks, and save their text and metadata. Embedding generation and similarity search belong to Tasks 3 and 4.

This document describes the planned implementation; it does not claim that the chunking script or dataset already exists.

## Storage choice: JSONL

Use `chunks.jsonl`, with one JSON object per line, encoded as UTF-8 without a byte-order mark. Newlines inside source text are escaped by the JSON serializer.

The assignments allow a simple workflow: create the chunks once, generate their embeddings once, and reuse the resulting dataset for retrieval. They do not require continuous indexing or updating chunks after Task 5 modifies the source. JSONL fits this workflow because it is easy to inspect, portable, and writable incrementally using Python's standard `json` module.

SQLite would offer convenient indexed lookups and updates, but those features are unnecessary for this small, static dataset. Neither format automatically provides vector similarity search. Later tasks can load the records into memory and compare embeddings using a NumPy matrix.

## Input and file selection

- Default repository root: `../Task_1/AI4SE_Playground`, resolved relative to the chunking script rather than the current working directory.
- Include Python source files and tests. Tests provide examples of expected behavior that can help with coding tasks.
- Skip empty files, `.git`, virtual environments, caches, build outputs, and generated chunk files. Restricting input to `.py` files also excludes `.env` files and binary assets.
- Traverse files in sorted repository-relative path order so repeated runs on unchanged input produce the same output.
- Read Python files using `tokenize.open` to respect Python source encoding declarations, and normalize line endings to `\n` before chunking.

## Chunking method

Use syntax-aware splitting with a size-based fallback. Never combine content from different files into one chunk.

1. Keep a file as one chunk if it fits within the target size.
2. Parse larger files with Python's built-in `ast` module and identify top-level functions, asynchronous functions, and classes.
3. Preserve a function or class as one unit when it fits within the maximum size. Keep decorators and leading comments with their definitions.
4. Split oversized classes at method boundaries. Keep the class header, class docstring, and class-level statements as source chunks too; store the enclosing class name in each method chunk's metadata.
5. Preserve source outside definitions, including imports, constants, module docstrings, and intervening comments. Group adjacent small source units up to the target size where practical.
6. Split any remaining oversized unit into line-based windows. If one line alone exceeds the maximum size, split that line by characters.
7. If parsing fails, use the same line-based fallback for the entire file and report the fallback in the script's summary.

Use AST positions to slice the original source text instead of regenerating code from the AST. This preserves comments, indentation, and formatting. Account for decorators explicitly because a definition's starting position may exclude them.

All nonempty source content must be represented in the output. Overlap may duplicate content, but splitting must not silently discard it. Metadata identifies the enclosing symbol when an individual chunk lacks the full surrounding class or module context.

## Size and overlap

- Target size: **2,000 characters** of source text.
- Maximum size: **4,000 characters** of source text.
- Overlap: **up to 200 characters**, preferably whole trailing lines, only between fallback windows from the same oversized unit.
- No overlap between complete structural units or different files.

The target encourages focused chunks, while the higher maximum avoids splitting a moderately sized function just to meet the target. Small final chunks are acceptable. Fallback splitting must always advance, including when an individual line is unusually long.

Character counting avoids a tokenizer dependency in Task 2. These limits are initial engineering choices, not measured optimal values or exact token limits. Task 3 must still check the chosen embedding model's token limit. Retrieval quality can be evaluated in later tasks before changing these defaults.

## Record format

Each record contains:

| Field | Meaning |
| --- | --- |
| `id` | Deterministic SHA-256 identifier derived from relative path, source offsets, and chunk text |
| `path` | Repository-relative path using `/` separators |
| `language` | `python` |
| `symbol` | Qualified symbol such as `Inventory.reserve`, or `null` for mixed/module content |
| `kind` | `file`, `function`, `class`, `method`, `module`, or `window` |
| `start_line`, `end_line` | One-based, inclusive source line range |
| `start_offset`, `end_offset` | Zero-based, half-open character range in the normalized source file |
| `text` | Original source slice with normalized line endings |
| `char_count` | Length of `text` in characters |

Offsets distinguish fallback chunks that share a source line. For every record, `text` must equal `normalized_source[start_offset:end_offset]`. IDs are reproducible for identical input and settings; they are not guaranteed to remain unchanged after edits move code.

## Processing architecture

```text
Repository root
    -> discover and filter Python files
    -> read and normalize source
    -> identify syntax boundaries
    -> group small units / split oversized units
    -> attach metadata and deterministic IDs
    -> validate records
    -> write chunks.jsonl
```

Planned files in `Task_2/`:

- `chunk_repository.py`: command-line entry point and chunking implementation, using only the Python standard library.
- `chunks.jsonl`: generated chunk dataset.
- `setup.md`: this design document.
- `report.md`: implementation results, actual chunk statistics, and any deviations from this design.

The script should accept repository root, output path, target size, maximum size, and overlap as command-line options. It should stream records to a temporary output file and replace the destination only after successful completion. Unexpected read failures should fail the run with the affected path instead of silently producing an incomplete dataset.

## Validation and later tasks

Validate JSON serialization, unique IDs, source ranges, maximum chunk size, and coverage of nonempty source content. Report processed files, chunk count, size distribution, and files requiring fallback splitting.

Task 3 will read `chunks.jsonl`, generate embeddings, and write a separate `embedded_chunks.jsonl` dataset linked by chunk ID. Record the embedding model and dimensions with that dataset. Tasks 4 and 5 can load it once and perform similarity matching in memory. Keeping the Task 2 output separate allows embedding experiments without repeating chunking.

Treat the initial chunks as a snapshot of the repository before Task 5's code changes. If later work deliberately refreshes that snapshot, regenerate affected chunks and embeddings together so stored text and vectors remain consistent.
