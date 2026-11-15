"""Offline checks for file patching, retrieval integration, and API handling."""

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import solve_tasks as solver


TASK = {"file": "module.py", "class": "Example", "method": "value",
        "docstring": "Return the value."}
SOURCE = ('# Unicode: č\r\nclass Example:\r\n    @property\r\n'
          '    def value(self) -> int:\r\n        pass\r\n\r\n'
          '    def other(self):\r\n        return 7\r\n')


class SolverTests(unittest.TestCase):
    def test_preserves_decorator_other_method_and_newlines(self):
        updated = solver.replace_method(SOURCE, TASK,
                                        '```python\ndef value(self) -> int:\n    return 42\n```')
        namespace = {}
        exec(updated, namespace)
        instance = namespace["Example"]()
        self.assertEqual(instance.value, 42)
        self.assertEqual(instance.other(), 7)
        self.assertTrue(updated.startswith('# Unicode: č\r\n'))
        self.assertIn('    @property\r\n    def value(self) -> int:', updated)
        self.assertNotIn('\n', updated.replace('\r\n', ''))

    def test_rejects_wrong_signature_extra_code_and_placeholders(self):
        for code in ('def other(self) -> int: return 1',
                     'def value(self, x) -> int: return 1',
                     'def value(self) -> str: return "x"',
                     'def value(self) -> int: return 1\nx = 2',
                     '@staticmethod\ndef value(self) -> int: return 1',
                     'def value(self) -> int: pass',
                     'def value(self) -> int: ...'):
            with self.subTest(code=code), self.assertRaises(ValueError):
                solver.replace_method(SOURCE, TASK, code)

    def test_accepts_matching_decorators_without_duplicating_them(self):
        code = ('@property\ndef value(self) -> int:\n'
                '    """Return the value."""\n    return 42')
        updated = solver.replace_method(SOURCE, TASK, code)
        self.assertEqual(updated.count('@property'), 1)
        namespace = {}
        exec(updated, namespace)
        self.assertEqual(namespace['Example']().value, 42)

    def test_rejects_added_or_reordered_decorators(self):
        with self.assertRaisesRegex(ValueError, 'decorators'):
            solver.replace_method(SOURCE, TASK,
                                 '@property\n@staticmethod\ndef value(self) -> int: return 42')
        plain = SOURCE.replace('    @property\r\n', '')
        with self.assertRaisesRegex(ValueError, 'decorators'):
            solver.replace_method(plain, TASK,
                                 '@property\ndef value(self) -> int: return 42')

    def test_handles_inline_and_multiline_signatures(self):
        source = 'class Example:\n    def value(\n        self,\n    ) -> int:\n        pass\n'
        updated = solver.replace_method(source, TASK, 'def value(self) -> int: return 42')
        self.assertIn('def value(\n        self,\n    ) -> int:', updated)
        compile(updated, '<test>', 'exec')

    def test_prevents_target_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ('../outside.py', 'module.txt'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    solver.target_path(Path(directory), name)

    def test_real_retrieval_for_every_assignment(self):
        tasks = json.loads(solver.DEFAULT_TASKS.read_text())
        self.assertEqual(len(tasks), 10)
        for task in tasks:
            with self.subTest(method=task['method']):
                _, _, prompt, chunks = solver.prepare_task(task, solver.DEFAULT_REPO,
                                                           solver.DEFAULT_STORE)
                self.assertEqual(len(chunks), 5)
                self.assertEqual(json.loads(prompt)['retrieved_chunks'], chunks)

    def test_api_extracts_text_after_reasoning_and_rejects_incomplete(self):
        payload = {'status': 'completed', 'output': [
            {'type': 'reasoning'}, {'type': 'message', 'content': [
                {'type': 'output_text', 'text': 'def value(self) -> int: return 42'}]}]}
        with patch.object(solver.urllib.request, 'urlopen',
                          return_value=io.BytesIO(json.dumps(payload).encode())) as call:
            code, _ = solver.generate_code('task', 'test-secret')
            self.assertIn('return 42', code)
            request = call.call_args.args[0]
            self.assertEqual(json.loads(request.data)['model'], 'gpt-6-luna')
            self.assertFalse(json.loads(request.data)['store'])
        payload['status'] = 'incomplete'
        with patch.object(solver.urllib.request, 'urlopen',
                          return_value=io.BytesIO(json.dumps(payload).encode())):
            with self.assertRaises(ValueError):
                solver.generate_code('task', 'test-secret')

    def test_failed_second_generation_leaves_all_source_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'module.py'
            target.write_bytes(SOURCE.encode())
            second = dict(TASK, method='other')
            tasks_file = root / 'tasks.json'
            tasks_file.write_text(json.dumps([TASK, second]))
            chunks = [{'id': str(i)} for i in range(5)]
            with patch.object(solver, 'HERE', root), \
                 patch.object(solver, 'search', return_value=chunks), \
                 patch.dict(solver.os.environ, {'OPENAI_API_KEY': 'test-secret'}), \
                 patch.object(solver, 'generate_code', side_effect=[
                     ('def value(self) -> int: return 42', {}), RuntimeError('failed')]), \
                 patch.object(solver.sys, 'argv', ['solve_tasks', '--repo', str(root),
                                                   '--tasks', str(tasks_file)]), \
                 patch('sys.stdout', new_callable=io.StringIO), \
                 patch('sys.stderr', new_callable=io.StringIO):
                self.assertEqual(solver.main(), 1)
            self.assertEqual(target.read_bytes(), SOURCE.encode())

    def test_batch_updates_two_methods_in_same_file_and_reports_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / 'playground'
            package.mkdir()
            target = package / 'module.py'
            target.write_bytes(SOURCE.encode())
            tests = package / 'tests'
            tests.mkdir()
            (tests / 'test_example.py').write_text(
                'import unittest\nfrom module import Example\n'
                'class Tests(unittest.TestCase):\n'
                '    def test_values(self):\n'
                '        self.assertEqual(Example().value, 42)\n'
                '        self.assertEqual(Example().other(), 8)\n')
            first = dict(TASK, file='playground/module.py')
            second = dict(first, method='other')
            tasks_file = root / 'tasks.json'
            tasks_file.write_text(json.dumps([first, second]))
            chunks = [{'id': str(i)} for i in range(5)]
            with patch.object(solver, 'HERE', root), \
                 patch.object(solver, 'search', return_value=chunks), \
                 patch.dict(solver.os.environ, {'OPENAI_API_KEY': 'test-secret'}), \
                 patch.object(solver, 'generate_code', side_effect=[
                     ('def value(self) -> int: return 42', {}),
                     ('def other(self): return 8', {})]), \
                 patch.object(solver.sys, 'argv', ['solve_tasks', '--repo', str(root),
                                                   '--tasks', str(tasks_file)]), \
                 patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(solver.main(), 0)
            output = next(root.glob('run-*'))
            self.assertEqual((output / 'backups/playground/module.py').read_bytes(),
                             SOURCE.encode())
            report = (output / 'report.md').read_text()
            self.assertIn('Ran 1 test', report)
            self.assertIn('Result: OK (exit code 0)', report)


if __name__ == '__main__':
    unittest.main()
