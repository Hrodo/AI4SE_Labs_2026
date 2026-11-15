"""Validate fitted embeddings, round trips, compatibility and safe rebuilds."""

import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import embed_chunks as embeddings


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=embeddings.HERE)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "chunks.jsonl"
        self.store = self.root / "embeddings.sqlite3"
        self.chunks = [
            {"id": "inventory", "path": "inventory.py", "symbol": "reserveStock",
             "kind": "function", "text": "def reserveStock(quantity):\n    '''Reserve inventory stock.'''\n",
             "start_line": 1, "end_line": 2},
            {"id": "pricing", "path": "pricing.py", "symbol": "calculate_discount",
             "kind": "function", "text": "def calculate_discount(price):\n    return price * 0.9\n",
             "start_line": 1, "end_line": 2},
        ]
        self.write_chunks(self.chunks)

    def write_chunks(self, chunks):
        self.source.write_text("".join(json.dumps(c) + "\n" for c in chunks), encoding="utf-8")

    def read_store(self):
        connection = embeddings.open_store(self.store)
        try:
            model = embeddings.load_model(connection)
            rows = connection.execute("SELECT id, chunk_json, embedding FROM chunks ORDER BY id").fetchall()
            return model, rows
        finally:
            connection.close()

    def test_code_identifier_tokenization(self):
        self.assertEqual(embeddings.tokenize("HTTPServer reserveStock calculate_discount"),
                         ["httpserver", "http", "server", "reservestock", "reserve", "stock",
                          "calculate_discount", "calculate", "discount"])
        self.assertIn("café", embeddings.tokenize("café"))

    def test_store_round_trip_normalization_and_reproducibility(self):
        summary = embeddings.build_store(self.source, self.store)
        model, rows = self.read_store()
        self.assertEqual(summary["chunks"], 2)
        self.assertEqual(model["dimensions"], 512)
        for identifier, chunk_json, blob in rows:
            chunk = json.loads(chunk_json)
            self.assertEqual(chunk, next(c for c in self.chunks if c["id"] == identifier))
            vector = embeddings.unpack_embedding(blob)
            self.assertEqual(list(vector), embeddings.embed_chunk(chunk, model))
            self.assertAlmostEqual(sum(v * v for v in vector), 1.0)
            self.assertTrue(all(math.isfinite(v) for v in vector))
        embeddings.build_store(self.source, self.store)
        self.assertEqual(self.read_store(), (model, rows))

    def test_query_uses_same_space_and_prefers_relevant_code(self):
        embeddings.build_store(self.source, self.store)
        model, rows = self.read_store()
        for query, expected in [("reserve inventory stock", "inventory"),
                                ("calculate discount price", "pricing")]:
            vector = embeddings.embed_text(query, model)
            scores = {identifier: sum(a * b for a, b in zip(vector, embeddings.unpack_embedding(blob)))
                      for identifier, _, blob in rows}
            self.assertEqual(max(scores, key=scores.get), expected)
        self.assertEqual(embeddings.embed_text("123 !!!", model), [0.0] * 512)

    def test_idf_counts_documents_not_occurrences(self):
        self.chunks[0]["text"] = "unique " * 50
        self.write_chunks(self.chunks)
        embeddings.build_store(self.source, self.store)
        model, _ = self.read_store()
        bucket = next(iter(embeddings.bucket_counts("unique", 512)))
        documents = sum(bucket in embeddings.bucket_counts(embeddings.chunk_text(c), 512)
                        for c in self.chunks)
        self.assertAlmostEqual(model["idf"][bucket], 1 + math.log(3 / (1 + documents)))

    def test_bad_inputs_preserve_existing_store(self):
        embeddings.build_store(self.source, self.store)
        original = self.store.read_bytes()
        for contents in ["", "{broken", "[]\n", '{"id":"missing"}\n',
                         json.dumps(self.chunks[0]) + "\n" + json.dumps(self.chunks[0])]:
            with self.subTest(contents=contents):
                self.source.write_text(contents, encoding="utf-8")
                with self.assertRaises(ValueError):
                    embeddings.build_store(self.source, self.store)
                self.assertEqual(self.store.read_bytes(), original)

    def test_failed_replace_cleans_temporary_file(self):
        embeddings.build_store(self.source, self.store)
        original = self.store.read_bytes()
        with patch.object(embeddings.os, "replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                embeddings.build_store(self.source, self.store)
        self.assertEqual(self.store.read_bytes(), original)
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_missing_store_is_not_created_and_source_is_not_overwritten(self):
        with self.assertRaises(embeddings.sqlite3.OperationalError):
            embeddings.open_store(self.store)
        self.assertFalse(self.store.exists())
        with self.assertRaises(ValueError):
            embeddings.build_store(self.source, self.source)

    def test_incompatible_model_is_rejected(self):
        embeddings.build_store(self.source, self.store)
        connection = embeddings.sqlite3.connect(self.store)
        try:
            model = embeddings.load_model(connection)
            model["name"] = "another-model"
            connection.execute("UPDATE metadata SET value = ? WHERE key = 'model'", (json.dumps(model),))
            connection.commit()
            with self.assertRaises(ValueError):
                embeddings.load_model(connection)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
