# Task 4 report

Implemented `retrieve_chunks.py` to find the n most relevant code chunks in
Task 3's `embeddings.sqlite3`. It accepts either text or a query embedding and
returns matching chunks with similarity scores and their original metadata.

## Design decisions

- **Cosine similarity:** the query is normalized and compared with each stored
  vector using a dot product. Text queries use Task 3's saved IDF weights so
  queries and chunks use the same embedding model.
- **Scan all chunks:** with only 132 chunks, checking every vector is simple
  and fast enough. Results are sorted by descending score, with chunk ID used
  to break ties. If n exceeds the number of chunks, all chunks are returned.
- **Reuse existing storage:** the SQLite store is opened read-only. No extra
  packages, API keys, or network access are needed.
- **Validate inputs:** invalid n values, incorrect dimensions, nonfinite values,
  and zero query vectors are rejected. Input embeddings must use the same fitted
  Task 3 model as the store.

Matching depends on shared words and identifiers. Synonyms may be missed, and
hash collisions can produce unrelated matches. Test code can also appear among
results.

## Usage

Run from the repository root:

```powershell
python Week_06_Implementation/Assignments/Task_4/retrieve_chunks.py --text "reserve inventory stock" -n 5
python Week_06_Implementation/Assignments/Task_4/retrieve_chunks.py --embedding-json query.json -n 5
```

`query.json` can contain a vector array or the JSON object produced by Task 3's
`embed` command. Python callers can use `search(text, n=5)` or
`retrieve(query_embedding, n=5)`.

## Validation

All **6 tests passed** on Python 3.13. They check ranking, cosine scores, result
limits, ties, metadata preservation, invalid inputs, read-only access, and CLI
behavior. A query for `reserve inventory stock` against the real store returned
inventory tests as the top two matches.

Run the tests with:

```powershell
python -m unittest discover -s Week_06_Implementation/Assignments/Task_4 -p "test_*.py" -v
```
