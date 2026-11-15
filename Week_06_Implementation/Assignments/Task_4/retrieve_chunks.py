"""Retrieve the top n code chunks by cosine similarity using Task 3's store."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sqlite3
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Task_3"))
from embed_chunks import (DEFAULT_STORE, DIMENSIONS, MODEL, embed_text, load_model,
                         open_store, unpack_embedding)


def _retrieve(connection, model, query_embedding, n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(query_embedding, (list, tuple)):
        raise ValueError("query embedding must be a list or tuple of numbers")
    if len(query_embedding) != model["dimensions"]:
        raise ValueError(f"query embedding must have {model['dimensions']} dimensions")
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) for v in query_embedding):
        raise ValueError("query embedding must contain finite numbers")
    # Scale first to avoid overflow even for very large finite components.
    scale = max(abs(v) for v in query_embedding)
    if not scale:
        raise ValueError("query embedding must not be a zero vector")
    query = [v / scale for v in query_embedding]
    norm = math.hypot(*query)
    query = [v / norm for v in query]

    results = []
    for identifier, chunk_json, blob in connection.execute(
            "SELECT id, chunk_json, embedding FROM chunks"):
        vector = unpack_embedding(blob, model["dimensions"])
        if (any(not math.isfinite(v) for v in vector)
                or not math.isclose(math.hypot(*vector), 1.0, rel_tol=1e-9)):
            raise ValueError(f"invalid stored embedding for {identifier}")
        score = math.fsum(a * b for a, b in zip(query, vector))
        results.append({"id": identifier, "score": max(-1.0, min(1.0, score)),
                        "chunk": json.loads(chunk_json)})
    results.sort(key=lambda result: (-result["score"], result["id"]))
    return results[:n]


def retrieve(query_embedding, n=5, store=DEFAULT_STORE):
    """Return up to n {id, score, chunk} records, highest score first.

    The vector must come from the same fitted model/corpus as the store.
    Nonzero query vectors are normalized before scoring; ties use chunk ID.
    """
    connection = open_store(Path(store))
    try:
        return _retrieve(connection, load_model(connection), query_embedding, n)
    finally:
        connection.close()


def search(text, n=5, store=DEFAULT_STORE):
    """Embed a task with the saved IDF weights and retrieve its top n chunks."""
    if not isinstance(text, str):
        raise ValueError("query text must be a string")
    connection = open_store(Path(store))
    try:
        model = load_model(connection)
        return _retrieve(connection, model, embed_text(text, model), n)
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("-n", type=int, default=5, help="number of chunks (default: 5)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="task description to embed and match")
    group.add_argument("--embedding-json", type=Path,
                       help="JSON vector or JSON object emitted by Task 3's embed command")
    args = parser.parse_args()
    try:
        if args.embedding_json is None:
            results = search(args.text, args.n, args.store)
        else:
            payload = json.loads(args.embedding_json.read_text(encoding="utf-8-sig"))
            if isinstance(payload, dict):
                if payload.get("model") != MODEL or payload.get("dimensions") != DIMENSIONS:
                    raise ValueError("unsupported query embedding model or dimensions")
                payload = payload.get("embedding")
            results = retrieve(payload, args.n, args.store)
        print(json.dumps(results, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, sqlite3.Error, struct.error) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
