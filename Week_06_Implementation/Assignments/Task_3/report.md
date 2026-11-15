# Task 3 implementation report

Implemented `embed_chunks.py` to read Task 2's `chunks.jsonl` and store each
chunk with its embedding in `embeddings.sqlite3`. It runs offline using only
Python's standard library.

## Design choices

Each chunk becomes a **512-dimensional hashed TF-IDF vector**. TF-IDF gives more
weight to terms that distinguish a chunk from the rest of the repository.
Hashing maps those terms to a fixed-size vector and produces repeatable results.
This approach needs no API keys, model downloads, or additional packages.

The input includes the chunk's file path, symbol name, kind, and full source
text. Identifiers such as `reserveStock` and `reserve_stock` are also split into
individual words to help match natural-language queries. No source is truncated.

**SQLite** stores the original chunks, their vectors, and the fitted TF-IDF
weights in one file. It preserves chunk IDs and source locations from Task 2
and prevents duplicate IDs. JSONL remains the input format; SQLite is the
embedding storage format.

Vectors are normalized to unit length, so Task 4 can compare them using dot
products to obtain cosine similarity. Queries must use the saved TF-IDF weights.
If the chunk dataset changes, rebuild the store to keep all vectors consistent.
With only 132 chunks, scanning all vectors is practical; no vector index is needed.

The main limitation is that these embeddings match shared words rather than
meaning. Synonyms may not match, and hashing can map unrelated words to the same
vector position. A pretrained embedding model could improve semantic matching.

## Usage

Run from the repository root:

```powershell
python Week_06_Implementation/Assignments/Task_3/embed_chunks.py build
python Week_06_Implementation/Assignments/Task_3/embed_chunks.py embed --text "reserve inventory stock"
python -m unittest discover -s Week_06_Implementation/Assignments/Task_3 -p "test_*.py" -v
```

The `build` command creates the database. The `embed` command prints a vector
using the stored weights. Use `--chunk-json chunk.json` instead of `--text` to
embed a single Task 2 chunk object.

## Results

The generated database contains **132 chunks**, each with a **512-dimensional
embedding**. All stored chunks match the input, all vectors reproduce using the
saved model, and the database integrity check passed.

All **8 regression tests passed**, covering tokenization, vector storage,
reproducibility, query compatibility, invalid inputs, and safe rebuilds.
The tests ran outside the Windows sandbox because it blocked temporary-directory
access. Query checks confirm basic matching, not overall semantic search quality.
