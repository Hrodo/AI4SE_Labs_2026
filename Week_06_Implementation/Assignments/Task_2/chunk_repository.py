"""Create a deterministic, source-preserving JSONL snapshot for code retrieval."""

from __future__ import annotations

import argparse
import ast
from bisect import bisect_right
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import statistics
import tempfile
import tokenize


HERE = Path(__file__).resolve().parent
SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "ENV", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".cache", ".tox", ".nox", ".eggs",
    "build", "dist", "htmlcov", "node_modules", "__pypackages__",
}
DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    symbol: str | None = None


def check_sizes(target: int, maximum: int, overlap: int) -> None:
    if not 0 <= overlap < target <= maximum:
        raise ValueError("sizes must satisfy 0 <= overlap < target <= maximum")


def discover_python_files(root: Path):
    """Prune generated directories and custom virtual environments, then sort globally."""
    def fail(error):
        raise error

    paths = []
    for directory, subdirs, files in os.walk(root, onerror=fail, followlinks=False):
        parent = Path(directory)
        subdirs[:] = [
            name for name in subdirs
            if name not in SKIP_DIRS and not name.endswith(".egg-info")
            and not (parent / name).is_symlink()
            and not (parent / name / "pyvenv.cfg").exists()
        ]
        paths.extend(parent / name for name in files
                     if name.endswith(".py") and not (parent / name).is_symlink())
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def read_source(path: Path) -> str:
    try:
        with tokenize.open(path) as handle:
            return handle.read().replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, UnicodeError, SyntaxError, LookupError) as error:
        raise ValueError(f"cannot read {path}: {error}") from error


def line_starts(source: str) -> list[int]:
    return [0] + [index + 1 for index, char in enumerate(source) if char == "\n"]


def definition_span(node, lines: list[str], starts: list[int], floor: int,
                    kind: str, symbol: str) -> Span:
    first = min([node.lineno] + [item.lineno for item in node.decorator_list]) - 1
    # AST locations omit decorators and comments; keep contiguous leading comments.
    while first > 0 and starts[first - 1] >= floor and lines[first - 1].lstrip().startswith("#"):
        first -= 1
    end = starts[node.end_lineno] if node.end_lineno < len(starts) else sum(map(len, lines))
    return Span(starts[first], end, kind, symbol)


def partition(start: int, end: int, definitions: list[Span], symbol=None) -> list[Span]:
    result = []
    cursor = start
    for span in definitions:
        if cursor < span.start:
            result.append(Span(cursor, span.start, "module", symbol))
        result.append(span)
        cursor = span.end
    if cursor < end:
        result.append(Span(cursor, end, "module", symbol))
    return result


def structural_spans(source: str, maximum: int) -> list[Span]:
    tree = ast.parse(source)
    # splitlines also recognises non-newline characters; offsets must use only LF.
    lines = source.split("\n")
    lines = [line + "\n" for line in lines[:-1]] + [lines[-1]]
    starts = line_starts(source)
    definitions = []
    floor = 0
    for node in tree.body:
        if not isinstance(node, DEFINITIONS):
            continue
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        span = definition_span(node, lines, starts, floor, kind, node.name)
        floor = span.end
        if isinstance(node, ast.ClassDef) and span.end - span.start > maximum:
            methods = []
            method_floor = span.start
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = definition_span(child, lines, starts, method_floor,
                                             "method", f"{node.name}.{child.name}")
                    methods.append(method)
                    method_floor = method.end
            definitions.extend(partition(span.start, span.end, methods, node.name))
        else:
            definitions.append(span)
    return partition(0, len(source), definitions)


def windows(source: str, span: Span, target: int, maximum: int, overlap: int):
    """Split at lines when possible, with bounded overlap and guaranteed progress."""
    start = span.start
    while start < span.end:
        if span.end - start <= maximum:
            end = span.end
        else:
            preferred = min(start + target, span.end)
            newline = source.rfind("\n", start, preferred)
            if newline >= start:
                end = newline + 1
            else:
                # A moderately long single line can still fit below the maximum.
                newline = source.find("\n", preferred, min(start + maximum, span.end))
                end = newline + 1 if newline >= 0 else min(start + maximum, span.end)
        yield Span(start, end, "window", span.symbol)
        if end == span.end:
            break
        next_start = max(start + 1, end - overlap)
        # Prefer a complete trailing line over a partial line as overlap.
        newline = source.find("\n", next_start, end)
        if newline >= 0:
            next_start = newline + 1
        start = next_start


def chunk_source(source: str, target=2000, maximum=4000, overlap=200):
    """Return source spans and whether parsing failed (never execute source)."""
    check_sizes(target, maximum, overlap)
    if not source.strip():
        return [], False
    if len(source) <= target:
        return [Span(0, len(source), "file")], False
    failed = False
    try:
        units = structural_spans(source, maximum)
    except (SyntaxError, ValueError, RecursionError):
        units = [Span(0, len(source), "module")]
        failed = True
    # Group adjacent small units while retaining metadata for standalone symbols.
    grouped = []
    for unit in units:
        if (grouped and grouped[-1].end == unit.start
                and unit.end - grouped[-1].start <= target
                and grouped[-1].kind != "method" and unit.kind != "method"):
            previous = grouped.pop()
            symbol = previous.symbol if previous.symbol == unit.symbol else None
            grouped.append(Span(previous.start, unit.end, "module", symbol))
        else:
            grouped.append(unit)
    result = []
    for unit in grouped:
        if unit.end - unit.start > maximum or failed:
            result.extend(windows(source, unit, target, maximum, overlap))
        else:
            result.append(unit)
    return [span for span in result if source[span.start:span.end].strip()], failed


def make_record(path: str, source: str, span: Span, starts: list[int]) -> dict:
    text = source[span.start:span.end]
    identity = json.dumps([path, span.start, span.end, text], ensure_ascii=False,
                          separators=(",", ":")).encode("utf-8")
    return {
        "id": hashlib.sha256(identity).hexdigest(),
        "path": path, "language": "python", "symbol": span.symbol, "kind": span.kind,
        "start_line": bisect_right(starts, span.start),
        "end_line": bisect_right(starts, span.end - 1),
        "start_offset": span.start, "end_offset": span.end,
        "text": text, "char_count": len(text),
    }


def validate_records(records: list[dict], source: str, maximum: int, seen: set[str]):
    starts = line_starts(source)
    covered = 0
    for record in records:
        start, end = record["start_offset"], record["end_offset"]
        if not 0 <= start < end <= len(source):
            raise ValueError("invalid source offsets")
        if record["text"] != source[start:end] or record["char_count"] != end - start:
            raise ValueError("chunk differs from source")
        if end - start > maximum:
            raise ValueError("chunk exceeds maximum size")
        if (record["start_line"] != bisect_right(starts, start)
                or record["end_line"] != bisect_right(starts, end - 1)):
            raise ValueError("invalid line range")
        if record["id"] in seen:
            raise ValueError("duplicate chunk ID")
        seen.add(record["id"])
        if source[covered:start].strip():
            raise ValueError("uncovered source content")
        covered = max(covered, end)
    if source[covered:].strip():
        raise ValueError("uncovered source content at end of file")


def chunk_repository(root: Path, output: Path, target=2000, maximum=4000, overlap=200):
    check_sizes(target, maximum, overlap)
    root, output = Path(root).resolve(), Path(output).resolve()
    if not root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")
    if output.suffix.lower() == ".py":
        raise ValueError("output must not overwrite Python source; use a .jsonl path")
    paths = discover_python_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    sizes, parse_fallbacks, window_files = [], [], []
    seen = set()
    processed = empty = 0
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, prefix=output.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            for path in paths:
                relative = path.relative_to(root).as_posix()
                source = read_source(path)
                spans, failed = chunk_source(source, target, maximum, overlap)
                starts = line_starts(source)
                records = [make_record(relative, source, span, starts)
                           for span in spans]
                try:
                    validate_records(records, source, maximum, seen)
                    for record in records:
                        serialized = json.dumps(record, ensure_ascii=False)
                        if json.loads(serialized) != record:
                            raise ValueError("JSON round-trip failed")
                        handle.write(serialized + "\n")
                        sizes.append(record["char_count"])
                except ValueError as error:
                    raise ValueError(f"validation failed for {relative}: {error}") from error
                if not records:
                    empty += 1
                    continue
                processed += 1
                if failed:
                    parse_fallbacks.append(relative)
                if any(span.kind == "window" for span in spans):
                    window_files.append(relative)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return {
        "processed_files": processed, "empty_files_skipped": empty,
        "chunk_count": len(sizes), "total_chunk_characters": sum(sizes),
        "size_characters": {
            "min": min(sizes, default=0), "max": max(sizes, default=0),
            "mean": round(statistics.mean(sizes), 2) if sizes else 0,
            "median": statistics.median(sizes) if sizes else 0,
            "up_to_target": sum(size <= target for size in sizes),
            "above_target": sum(size > target for size in sizes),
        },
        "parse_fallback_files": parse_fallbacks, "window_files": window_files,
        "settings": {"target": target, "maximum": maximum, "overlap": overlap},
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parent / "Task_1" / "AI4SE_Playground")
    parser.add_argument("--output", type=Path, default=HERE / "chunks.jsonl")
    parser.add_argument("--target-size", type=int, default=2000)
    parser.add_argument("--max-size", type=int, default=4000)
    parser.add_argument("--overlap", type=int, default=200)
    args = parser.parse_args()
    try:
        summary = chunk_repository(args.repo_root, args.output, args.target_size,
                                   args.max_size, args.overlap)
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
