"""Build a local hashed TF-IDF embedding store from Task 2's chunks.

No third-party packages, API keys, network access, or model downloads are needed.
Vectors are lexical embeddings, not pretrained semantic embeddings.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import struct
import tempfile


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE.parent / "Task_2" / "chunks.jsonl"
DEFAULT_STORE = HERE / "embeddings.sqlite3"
DIMENSIONS = 512
MODEL = "hashed-tfidf-code-v1"


def tokenize(text: str) -> list[str]:
    """Retain identifiers and expose snake_case and camelCase components."""
    tokens = []
    for word in re.findall(r"[^\W\d]\w*", text, flags=re.UNICODE):
        full = word.lower()
        tokens.append(full)
        separated = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
        separated = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", separated)
        parts = [part.lower() for part in separated.split("_") if part]
        if len(parts) > 1:
            tokens.extend(parts)
    return tokens


def chunk_text(chunk: dict) -> str:
    """Use the same representation for fitting and subsequent chunk embedding."""
    if not isinstance(chunk, dict):
        raise ValueError("a chunk must be a JSON object")
    for field in ("id", "path", "text"):
        if not isinstance(chunk.get(field), str) or not chunk[field].strip():
            raise ValueError(f"chunk requires a nonempty string {field!r}")
    for field in ("symbol", "kind"):
        if chunk.get(field) is not None and not isinstance(chunk[field], str):
            raise ValueError(f"chunk {field!r} must be a string or null")
    return "\n".join([chunk["path"], chunk.get("symbol") or "",
                       chunk.get("kind") or "", chunk["text"]])


def bucket_counts(text: str, dimensions: int) -> Counter:
    counts = Counter()
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        counts[int.from_bytes(digest[:8], "big") % dimensions] += 1
    return counts


def embed_text(text: str, model: dict) -> list[float]:
    """Embed a query or representation with the store's fitted IDF weights.

    An empty/tokenless query yields a zero vector. Query matching can explicitly
    reject that vector rather than assign arbitrary results.
    """
    vector = [0.0] * model["dimensions"]
    for bucket, count in bucket_counts(text, len(vector)).items():
        vector[bucket] = (1.0 + math.log(count)) * model["idf"][bucket]
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def embed_chunk(chunk: dict, model: dict) -> list[float]:
    return embed_text(chunk_text(chunk), model)


def load_model(connection: sqlite3.Connection) -> dict:
    row = connection.execute("SELECT value FROM metadata WHERE key = 'model'").fetchone()
    if row is None:
        raise ValueError("store has no embedding model")
    model = json.loads(row[0])
    if model.get("name") != MODEL or model.get("dimensions") != DIMENSIONS:
        raise ValueError("unsupported embedding model or dimensions")
    weights = model.get("idf")
    if (not isinstance(weights, list) or len(weights) != DIMENSIONS
            or any(not isinstance(w, (int, float)) or not math.isfinite(w) or w < 1
                   for w in weights)):
        raise ValueError("invalid IDF weights")
    return model


def unpack_embedding(blob: bytes, dimensions: int = DIMENSIONS) -> tuple[float, ...]:
    """Decode SQLite vectors; dot products equal cosine similarity after normalization."""
    return struct.unpack(f"<{dimensions}d", blob)


def open_store(path: Path) -> sqlite3.Connection:
    """Read-only access prevents accidentally creating a missing store."""
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def build_store(source: Path, destination: Path) -> dict:
    if source.resolve() == destination.resolve():
        raise ValueError("input and output paths must differ")
    source_bytes = source.read_bytes()
    chunks = []
    seen = set()
    frequencies = Counter()
    for number, line in enumerate(source_bytes.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            chunk = json.loads(line)
            representation = chunk_text(chunk)
            if chunk["id"] in seen:
                raise ValueError(f"duplicate chunk ID: {chunk['id']}")
            counts = bucket_counts(representation, DIMENSIONS)
            if not counts:
                raise ValueError("chunk representation has no tokens")
        except (ValueError, TypeError) as error:
            raise ValueError(f"invalid chunk on line {number}: {error}") from error
        seen.add(chunk["id"])
        frequencies.update(counts.keys())
        chunks.append(chunk)
    if not chunks:
        raise ValueError("input contains no chunks")
    model = {
        "name": MODEL,
        "dimensions": DIMENSIONS,
        "chunk_count": len(chunks),
        "idf": [1.0 + math.log((1 + len(chunks)) / (1 + frequencies[i]))
                for i in range(DIMENSIONS)],
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "representation": "path + symbol + kind + source text, newline separated",
        "vector_encoding": "512 little-endian IEEE-754 float64 values, L2 normalized",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=destination.name + ".", suffix=".tmp",
                                            dir=destination.parent)
    os.close(descriptor)
    try:
        connection = sqlite3.connect(temporary)
        try:
            with connection:
                connection.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
                connection.execute("""CREATE TABLE chunks (
                    id TEXT PRIMARY KEY, chunk_json TEXT NOT NULL,
                    embedding BLOB NOT NULL CHECK(length(embedding) = 4096))""")
                connection.execute("INSERT INTO metadata VALUES ('model', ?)",
                                   (json.dumps(model, ensure_ascii=False, allow_nan=False),))
                for chunk in chunks:
                    vector = embed_chunk(chunk, model)
                    if not math.isclose(sum(v * v for v in vector), 1.0, abs_tol=1e-12):
                        raise ValueError(f"invalid embedding for {chunk['id']}")
                    connection.execute("INSERT INTO chunks VALUES (?, ?, ?)",
                                       (chunk["id"], json.dumps(chunk, ensure_ascii=False),
                                        struct.pack(f"<{DIMENSIONS}d", *vector)))
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("SQLite integrity check failed")
        finally:
            connection.close()
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"chunks": len(chunks), "dimensions": DIMENSIONS, "model": MODEL,
            "source_sha256": model["source_sha256"], "store": str(destination)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="fit IDF and store every chunk with its vector")
    build.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    build.add_argument("--store", type=Path, default=DEFAULT_STORE)
    embed = subparsers.add_parser("embed", help="embed text or one chunk using the fitted store")
    embed.add_argument("--store", type=Path, default=DEFAULT_STORE)
    group = embed.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="a problem description or query")
    group.add_argument("--chunk-json", type=Path, help="file containing a single chunk JSON object")
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build_store(args.input, args.store)
        else:
            connection = open_store(args.store)
            try:
                model = load_model(connection)
            finally:
                connection.close()
            if args.chunk_json is not None:
                vector = embed_chunk(json.loads(args.chunk_json.read_text(encoding="utf-8-sig")), model)
            else:
                vector = embed_text(args.text, model)
            result = {"model": MODEL, "dimensions": DIMENSIONS, "embedding": vector}
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    main()
