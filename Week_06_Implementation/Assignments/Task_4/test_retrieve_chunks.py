"""Exercise retrieval against small, real Task 3 embedding stores."""

import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import retrieve_chunks as retrieval
from embed_chunks import build_store, embed_chunk, load_model, open_store


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(dir=retrieval.HERE)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.store = self.root / "store.sqlite3"
        self.chunks = [
            {"id": "inventory", "path": "inventory.py", "symbol": "reserve_stock",
             "text": "def reserve_stock(quantity): # reserve inventory stock\n    pass",
             "start_line": 1, "end_line": 2},
            {"id": "pricing", "path": "pricing.py", "symbol": "calculate_discount",
             "text": "def calculate_discount(price): return price * 0.9",
             "start_line": 1, "end_line": 1},
        ]
        source = self.root / "chunks.jsonl"
        source.write_text("\n".join(json.dumps(c) for c in self.chunks), encoding="utf-8")
        build_store(source, self.store)
        connection = open_store(self.store)
        try:
            self.model = load_model(connection)
        finally:
            connection.close()

    def test_text_ranking_and_preserved_metadata(self):
        for text, expected in [("reserve inventory stock", self.chunks[0]),
                               ("calculate discount price", self.chunks[1])]:
            with self.subTest(text=text):
                results = retrieval.search(text, n=1, store=self.store)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["chunk"], expected)
                self.assertEqual(results[0]["id"], expected["id"])
                self.assertGreater(results[0]["score"], 0)

    def test_embedding_input_cosine_and_result_limit(self):
        vector = embed_chunk(self.chunks[1], self.model)
        results = retrieval.retrieve(vector, n=10, store=self.store)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "pricing")
        self.assertAlmostEqual(results[0]["score"], 1.0)
        self.assertGreater(results[0]["score"], results[1]["score"])
        scaled = retrieval.retrieve([v * 7 for v in vector], n=10, store=self.store)
        self.assertEqual([r["id"] for r in scaled], [r["id"] for r in results])
        for original, changed in zip(results, scaled):
            self.assertAlmostEqual(original["score"], changed["score"])

    def test_ties_use_id_and_store_is_unchanged(self):
        connection = sqlite3.connect(self.store)
        try:
            blob = connection.execute("SELECT embedding FROM chunks LIMIT 1").fetchone()[0]
            connection.execute("UPDATE chunks SET embedding = ?", (blob,))
            connection.commit()
        finally:
            connection.close()
        original = self.store.read_bytes()
        results = retrieval.search("inventory", n=2, store=self.store)
        self.assertEqual([r["id"] for r in results], ["inventory", "pricing"])
        self.assertEqual(results[0]["score"], results[1]["score"])
        self.assertEqual(self.store.read_bytes(), original)

    def test_invalid_queries_and_limits(self):
        invalid = [[], [0.0] * 512, [float("nan")] * 512,
                   [float("inf")] * 512, ["1"] * 512, [True] * 512, None]
        for vector in invalid:
            with self.subTest(vector=str(vector)[:30]), self.assertRaises(ValueError):
                retrieval.retrieve(vector, store=self.store)
        for n in [0, -1, 1.5, True]:
            with self.subTest(n=n), self.assertRaises(ValueError):
                retrieval.search("inventory", n=n, store=self.store)
        with self.assertRaises(ValueError):
            retrieval.search("123 !!!", store=self.store)

    def test_missing_store_is_not_created(self):
        missing = self.root / "missing.sqlite3"
        with self.assertRaises(sqlite3.OperationalError):
            retrieval.search("inventory", store=missing)
        self.assertFalse(missing.exists())

    def test_cli_text_embedding_and_error(self):
        base = [sys.executable, str(retrieval.HERE / "retrieve_chunks.py"),
                "--store", str(self.store), "-n", "1"]
        result = subprocess.run(base + ["--text", "reserve inventory stock"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)[0]["id"], "inventory")
        query = self.root / "query.json"
        vector = embed_chunk(self.chunks[1], self.model)
        for payload in [vector, {"model": self.model["name"], "dimensions": 512,
                                 "embedding": vector}]:
            query.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(base + ["--embedding-json", str(query)],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)[0]["id"], "pricing")
        result = subprocess.run(base + ["--text", "!!!"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("zero vector", result.stderr)


if __name__ == "__main__":
    unittest.main()
