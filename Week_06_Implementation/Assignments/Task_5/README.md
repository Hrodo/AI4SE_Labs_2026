# Task 5

Run from the main repository root with Python 3.10 or newer. No packages need installing.

```powershell
python Week_06_Implementation/Assignments/Task_5/solve_tasks.py --dry-run
python Week_06_Implementation/Assignments/Task_5/solve_tasks.py
```

The second command reads `OPENAI_API_KEY` or securely prompts for the key in an
interactive terminal. The key is not saved. The default model is `gpt-6-luna`;
`--model` accepts only the models permitted by the assignment.

The script reads all ten entries in `../missing_code.json`, retrieves five chunks
per entry with Task 4, and sends the task, target module, and chunks to the OpenAI
Responses API. Retrieval continues to use the existing local hashed TF-IDF model;
the LLM generates source code, not embeddings.

Each response must contain exactly the requested method with its original
signature. Returned decorators may be omitted or must exactly match the original.
Its body replaces the existing body; decorators and other methods are
preserved. All ten responses are generated and syntax-checked before files are
modified. This checks syntax and scope of the replacement, not behavioral correctness.

Every invocation creates a unique `run-*` directory here containing the prompts.
A real run additionally saves generated methods, response IDs/token usage,
original files under `backups/`, and the playground test output (`tests.txt`) and
report (`report.md`). Copy the completed report into the assignment submission.
Run directories are ignored by Git, so explicitly copy any desired evidence.

After writing the methods, the script runs `python -m unittest discover -s tests -v`
in `Task_1/AI4SE_Playground/playground`. Failed tests leave the generated code in
place for inspection and return a nonzero exit code. There are no automatic
generation retries or test-driven repair calls. To undo a run, copy the files
from that run's `backups/` into the checkout using their relative paths.

For one textual task, `solve_task(task_text, file=..., class_name=..., method=...,
api_key=...)` retrieves, generates, backs up, and writes a method. This helper does
not run tests; the command-line batch runner does.

Run the offline pipeline checks with:

```powershell
python -m unittest discover -s Week_06_Implementation/Assignments/Task_5 -p "test_*.py" -v
```

The dry run makes no API calls and does not edit playground files. Actual generation
requires API access and incurs usage charges. Re-running a real run generates all
ten methods again. `--repo`, `--tasks`, and `--store` override the default paths.
