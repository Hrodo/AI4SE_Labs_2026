"""Regression checks for source coverage, syntax boundaries, and safe output."""

import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import chunk_repository as chunker


class ChunkSourceTests(unittest.TestCase):
    def assert_coverage(self, source, target=100, maximum=180, overlap=20):
        spans, failed = chunker.chunk_source(source, target, maximum, overlap)
        covered = bytearray(len(source))
        previous = -1
        for span in spans:
            self.assertGreater(span.start, previous)
            previous = span.start
            self.assertLessEqual(span.end - span.start, maximum)
            self.assertGreater(span.end, span.start)
            covered[span.start:span.end] = b"\1" * (span.end - span.start)
        self.assertTrue(all(covered[i] for i, char in enumerate(source) if not char.isspace()))
        return spans, failed

    def test_small_file_and_empty_source(self):
        source = '# café\nvalue = "☃"\n'
        self.assertEqual(chunker.chunk_source(source), ([chunker.Span(0, len(source), "file")], False))
        self.assertEqual(chunker.chunk_source(" \n\t"), ([], False))

    def test_decorated_async_function_preserves_comments_and_source(self):
        source = ('"""Module documentation."""\nimport os\n' + '# padding\n' * 10
                  + '# function explanation\n@decorate\nasync def work():\n    return "á"\n'
                  + '\nAFTER = 42\n' + '# trailing\n' * 15)
        spans, failed = self.assert_coverage(source, 60, 180, 15)
        self.assertFalse(failed)
        span = next(span for span in spans if span.symbol == "work")
        self.assertEqual(span.kind, "function")
        self.assertIn('# function explanation\n@decorate\nasync def work()', source[span.start:span.end])

    def test_oversized_class_keeps_header_attributes_and_method_context(self):
        source = ('class Inventory:\n    """Ledger."""\n    limit = 42\n\n'
                  '    # reservation\n    @decorator\n    def reserve(self):\n'
                  + '        value = 1\n' * 30
                  + '\n    async def release(self):\n        return 42\n'
                  + '\n    other = "preserve this"\n')
        spans, failed = self.assert_coverage(source)
        self.assertFalse(failed)
        methods = [span for span in spans if span.symbol == "Inventory.reserve"]
        self.assertTrue(methods)
        self.assertTrue(all(span.kind == "window" for span in methods))
        self.assertTrue(source[methods[0].start:].startswith('    # reservation\n    @decorator'))
        self.assertTrue(any(span.symbol == "Inventory.release" and span.kind == "method" for span in spans))
        self.assertTrue(any(span.symbol == "Inventory" and 'limit = 42' in source[span.start:span.end] for span in spans))

    def test_complete_function_can_exceed_target_without_splitting(self):
        function = 'def work():\n' + '    value = 1\n' * 10
        spans, failed = self.assert_coverage(function, 80, 200, 10)
        self.assertFalse(failed)
        self.assertEqual(spans, [chunker.Span(0, len(function), "function", "work")])

    def test_parse_failure_long_line_and_overlap(self):
        source = 'broken = (\n' + 'x' * 1000 + '\n' + 'trailing text\n' * 30
        spans, failed = self.assert_coverage(source)
        self.assertTrue(failed)
        self.assertTrue(all(span.kind == "window" for span in spans))
        overlaps = [left.end - right.start for left, right in zip(spans, spans[1:])]
        self.assertTrue(any(size > 0 for size in overlaps))
        self.assertTrue(all(0 <= size <= 20 for size in overlaps))

    def test_random_line_lengths_and_extreme_sizes_terminate_with_coverage(self):
        rng = random.Random(42)
        for _ in range(100):
            source = 'invalid (\n' + ''.join('x' * rng.randrange(1, 300) + '\n' for _ in range(20))
            target = rng.randrange(1, 100)
            maximum = target + rng.randrange(0, 100)
            overlap = rng.randrange(target)
            self.assert_coverage(source, target, maximum, overlap)

    def test_invalid_sizes(self):
        for settings in [(0, 10, 0), (20, 10, 1), (10, 20, 10), (10, 20, -1)]:
            with self.assertRaises(ValueError):
                chunker.chunk_source("x", *settings)


class RepositoryTests(unittest.TestCase):
    def test_encoding_discovery_metadata_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tests').mkdir()
            (root / 'a.py').write_bytes(b'# coding: latin-1\r\nname = "caf\xe9"\r\n')
            (root / 'tests' / 'test_a.py').write_text('assert True\n', encoding='utf-8')
            (root / 'empty.py').write_text('', encoding='utf-8')
            (root / '.env').write_text('NOT_SOURCE', encoding='utf-8')
            for name in ['.git', '.venv', '__pycache__', 'build', 'custom_env']:
                (root / name).mkdir()
                (root / name / 'skip.py').write_text('must_skip = True\n', encoding='utf-8')
            (root / 'custom_env' / 'pyvenv.cfg').write_text('home = python', encoding='utf-8')
            output = root / 'chunks.jsonl'
            summary = chunker.chunk_repository(root, output)
            before = output.read_bytes()
            self.assertFalse(before.startswith(b'\xef\xbb\xbf'))
            records = [json.loads(line) for line in before.decode('utf-8').splitlines()]
            self.assertEqual([item['path'] for item in records], ['a.py', 'tests/test_a.py'])
            self.assertIn('café', records[0]['text'])
            self.assertNotIn('\r', records[0]['text'])
            self.assertEqual(summary['processed_files'], 2)
            self.assertEqual(summary['empty_files_skipped'], 1)
            for record in records:
                source = chunker.read_source(root / record['path'])
                self.assertEqual(record['text'], source[record['start_offset']:record['end_offset']])
                self.assertEqual(record['char_count'], len(record['text']))
                self.assertEqual(record['start_line'], source[:record['start_offset']].count('\n') + 1)
                self.assertEqual(record['end_line'], source[:record['end_offset'] - 1].count('\n') + 1)
                self.assertEqual(len(record['id']), 64)
            chunker.chunk_repository(root, output)
            self.assertEqual(output.read_bytes(), before)

    def test_failed_read_leaves_existing_output_and_no_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'a.py').write_text('x = 1\n', encoding='utf-8')
            (root / 'b.py').write_bytes(b'\xff\xff')
            output = root / 'chunks.jsonl'
            output.write_bytes(b'previous dataset\n')
            with self.assertRaisesRegex(ValueError, 'b.py'):
                chunker.chunk_repository(root, output)
            self.assertEqual(output.read_bytes(), b'previous dataset\n')
            self.assertEqual(list(root.glob('*.tmp')), [])

    def test_failed_replace_leaves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'chunks.jsonl'
            output.write_text('previous', encoding='utf-8')
            with patch.object(chunker.os, 'replace', side_effect=OSError('cannot replace')):
                with self.assertRaises(OSError):
                    chunker.chunk_repository(root, output)
            self.assertEqual(output.read_text(encoding='utf-8'), 'previous')
            self.assertEqual(list(root.glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
