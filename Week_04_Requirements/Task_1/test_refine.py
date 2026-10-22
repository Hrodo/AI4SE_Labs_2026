"""Offline tests: execute real LangGraph transitions with scripted model responses."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from openai import LengthFinishReasonError

from refine import (
    APICaller, Candidate, Discarded, Draft, Extraction, Finding, OutputTruncatedError, Requirement,
    Review, add_findings, build_graph, ground_quote, grounded_call, load_documents, validate_draft,
)

MODELS = ("gpt-4.1-nano", "gpt-5-mini", "gpt-4o-mini")


def finding(name="CSV export", quote="Export CSV."):
    return Finding(name=name, explanation="The system shall export reports as CSV files.", quote=quote)


def make_draft(candidates):
    return Draft(title="Synthetic test specification", scope="Test reporting system.",
                 glossary=["CSV: comma-separated values"], blacklist=[], open_questions=[],
                 requirements=[Requirement(name=c["name"], explanation=c["explanation"],
                                           priority="Should", priority_reason="Priority unstated.",
                                           candidate_ids=[c["id"]]) for c in candidates])


class ScriptedCaller:
    def __init__(self, reject=False, discover=False, bad_draft=False):
        self.calls = []
        self.reject, self.discover, self.bad_draft = reject, discover, bad_draft
        self.refinements = 0

    def call(self, stage, model, prompt, payload, schema):
        self.calls.append({"stage": stage, "model": model})
        if stage == "extract":
            return Extraction(findings=[finding()])
        if stage == "refine":
            self.refinements += 1
            result = make_draft(payload["candidates"])
            if self.bad_draft and self.refinements == 1:
                result.requirements[0].candidate_ids = ["UNKNOWN"]
            return result
        new = [finding("PDF export", "Export PDF.")] if self.discover and self.refinements == 1 else []
        issues = ["Revise the explanation."] if self.reject else []
        return Review(approved=not (issues or new), issues=issues, new_findings=new)


class RefinementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.corpus = self.root / "corpus"
        self.corpus.mkdir()
        (self.corpus / "request.eml").write_text("Subject: Reports\nExport CSV.\nExport PDF.", encoding="utf-8")
        self.output = self.root / "output"

    def run_graph(self, caller, max_iterations=3):
        graph = build_graph(caller, self.corpus, self.output, MODELS, max_iterations)
        return graph.invoke({}, {"recursion_limit": 30})["artifact"]

    def test_recursive_ingestion_preserves_threads_and_ignores_binary(self):
        nested = self.corpus / "conversations"
        nested.mkdir()
        (nested / "thread.eml").write_bytes(b"\xef\xbb\xbfFirst\r\n===\r\nSecond")
        (nested / "image.png").write_bytes(b"\xff")
        docs = load_documents(self.corpus, 1000)
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0]["source"], "conversations/thread.eml")
        self.assertEqual(docs[0]["chunks"][0]["text"], "First\n===\nSecond")

    def test_chunks_cover_every_character_and_overlap(self):
        text = "".join(f"Line {i:04d}: lots of text.\n" for i in range(200))
        (self.corpus / "long.txt").write_text(text, encoding="utf-8")
        chunks = next(d for d in load_documents(self.corpus, 1000) if d["source"] == "long.txt")["chunks"]
        rebuilt = chunks[0]["text"]
        for previous, chunk in zip(chunks, chunks[1:]):
            self.assertEqual(previous["text"][-200:], chunk["text"][:200])
            rebuilt += chunk["text"][200:]
        self.assertEqual(rebuilt, text)

    def test_evidence_must_be_verbatim(self):
        with self.assertRaisesRegex(ValueError, "not verbatim"):
            add_findings([finding(quote="Invented text")], {"source": "a.txt"},
                         {"id": "CH-001", "text": "Export CSV."}, [])

    def test_whitespace_changes_restore_original_source_quote(self):
        self.assertEqual(ground_quote("Export CSV files.", "Export\n CSV files."), "Export\n CSV files.")
        self.assertEqual(ground_quote("Export CSV files.", "Export CSV files"), "Export CSV files")

    def test_flattened_list_with_added_periods_restores_source(self):
        text = "Report on:\n- Items checked in\n- Items checked out\n\nBreak down by:\n- Category"
        quote = "Report on: - Items checked in - Items checked out. Break down by: - Category."
        self.assertEqual(ground_quote(quote, text), text)

    def test_grounding_preserves_negation_numbers_and_comparison_operators(self):
        for quote, source in (("Do allow access.", "Do not allow access."),
                              ("Version 1.5", "Version 15"),
                              ("Limit < 100", "Limit > 100"),
                              ("Export PDF files", "Export CSV files")):
            with self.subTest(quote=quote), self.assertRaises(ValueError):
                ground_quote(quote, source)

    def test_reported_corpus_quote_formatting_regression(self):
        root = Path(__file__).parent
        source = root / "data/corpus/conversations/conv_pines014_material_volume.eml"
        text = source.read_text(encoding="utf-8")
        passage = text[text.index("The system should provide the ability"):text.index("This will be tracked")].strip()
        quote = " ".join(passage.split()).replace("(checked out)", "(checked out).") + "."
        restored = ground_quote(quote, text)
        self.assertEqual(restored, passage)

    def test_invalid_evidence_is_repaired_with_feedback(self):
        with patch.object(ScriptedCaller, "call") as call:
            call.side_effect = [Extraction(findings=[finding(quote="Paraphrase.")]),
                                Extraction(findings=[finding()])]
            result = grounded_call(ScriptedCaller(), "extract", MODELS[0], "test",
                                   {"source": "a.txt", "id": "CH-001", "text": "Export CSV."},
                                   Extraction, "findings")
            self.assertEqual(result.findings[0].quote, "Export CSV.")
            self.assertIn("evidence_repair", call.call_args.args[3])

    def test_repeated_invalid_evidence_is_marked_after_three_attempts(self):
        with patch.object(ScriptedCaller, "call", return_value=Extraction(findings=[finding(quote="Invented.")])) as call:
            result = grounded_call(ScriptedCaller(), "extract", MODELS[0], "test",
                                   {"source": "a.txt", "id": "CH-001", "text": "Export CSV."},
                                   Extraction, "findings")
            self.assertEqual(call.call_count, 3)
            self.assertEqual(result.findings[0].quote, "")
            self.assertEqual(result.findings[0].name, "CSV export")

    def test_bad_quotes_do_not_prevent_export_or_claim_verified_evidence(self):
        class BadQuoteCaller(ScriptedCaller):
            def call(self, stage, model, prompt, payload, schema):
                if stage == "extract":
                    return Extraction(findings=[finding(quote="Invented quote")])
                return super().call(stage, model, prompt, payload, schema)
        artifact = self.run_graph(BadQuoteCaller())
        self.assertEqual(artifact["status"], "needs_review")
        self.assertEqual(len(artifact["requirements"]), 1)
        self.assertEqual(artifact["requirements"][0]["sources"], ["request.eml"])
        self.assertFalse(artifact["candidates"][0]["quote_verified"])
        self.assertEqual(artifact["candidates"][0]["quote"], "")
        self.assertIn("no verified quote", artifact["issues"][0])
        markdown = (self.output / "requirements.md").read_text(encoding="utf-8")
        self.assertIn("Evidence warning", markdown)
        self.assertIn("Unverified quote", markdown)
        self.assertNotIn("Invented quote", markdown)

    def test_bad_evidence_does_not_partially_modify_ledger(self):
        candidates = []
        with self.assertRaises(ValueError):
            add_findings([finding(), finding(quote="Invented.")], {"source": "a.txt"},
                         {"id": "CH-001", "text": "Export CSV."}, candidates)
        self.assertEqual(candidates, [])

    def test_accounting_detects_missing_unknown_and_reused_ids(self):
        cs = [{"id": "C-00001"}, {"id": "C-00002"}]
        draft = make_draft([{**finding().model_dump(), "id": "C-00001"}])
        draft.requirements[0].candidate_ids += ["C-00001", "UNKNOWN"]
        issues = " ".join(validate_draft(draft, cs))
        for text in ("Unaccounted", "Unknown", "more than once"):
            self.assertIn(text, issues)

    def test_blacklist_counts_as_accounted(self):
        cs = [{**finding().model_dump(), "id": "C-00001"}, {"id": "C-00002"}]
        draft = make_draft(cs[:1])
        draft.blacklist.append(Discarded(name="Conflicting proposal", reason="Superseded by decision.",
                                        candidate_ids=["C-00002"]))
        self.assertEqual(validate_draft(draft, cs), [])

    def test_approved_run_exports_ids_sources_and_evidence(self):
        artifact = self.run_graph(ScriptedCaller())
        self.assertEqual(artifact["status"], "approved")
        self.assertEqual(artifact["iterations"], 1)
        self.assertEqual(artifact["requirements"][0]["id"], "REQ-0001")
        self.assertEqual(artifact["requirements"][0]["sources"], ["request.eml"])
        self.assertEqual(len({c["model"] for c in artifact["calls"]}), 3)
        markdown = (self.output / "requirements.md").read_text(encoding="utf-8")
        self.assertIn("Evidence ledger", markdown)
        self.assertIn("> Export CSV.", markdown)
        self.assertEqual(json.loads((self.output / "requirements.json").read_text(encoding="utf-8"))["status"], "approved")

    def test_rejection_loops_then_stops_with_visible_issues(self):
        artifact = self.run_graph(ScriptedCaller(reject=True), max_iterations=2)
        self.assertEqual(artifact["status"], "needs_review")
        self.assertEqual(artifact["iterations"], 2)
        self.assertEqual(len(artifact["review_history"]), 2)
        self.assertTrue(artifact["issues"])

    def test_review_can_recover_requirement_missed_in_extraction(self):
        artifact = self.run_graph(ScriptedCaller(discover=True))
        self.assertEqual(artifact["iterations"], 2)
        self.assertEqual(artifact["status"], "approved")
        self.assertEqual(len(artifact["requirements"]), 2)
        self.assertEqual(artifact["requirements"][1]["name"], "PDF export")

    def test_deterministic_failure_overrides_model_approval(self):
        artifact = self.run_graph(ScriptedCaller(bad_draft=True))
        self.assertEqual(artifact["iterations"], 2)
        self.assertEqual(artifact["status"], "approved")
        self.assertFalse(artifact["review_history"][0]["approved"])

    def test_empty_and_missing_inputs_fail(self):
        with self.assertRaises(ValueError):
            load_documents(self.root / "missing", 1000)
        (self.corpus / "request.eml").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Empty"):
            load_documents(self.corpus, 1000)

    def test_three_distinct_allowed_models_required(self):
        with self.assertRaisesRegex(ValueError, "three distinct"):
            build_graph(ScriptedCaller(), self.corpus, self.output, (MODELS[0],) * 3)

    def test_api_adapter_and_cache_without_network(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(refusal=None, parsed=Extraction(findings=[finding()])))],
            usage=SimpleNamespace(model_dump=lambda: {"total_tokens": 10}))
        with patch("refine.OpenAI") as factory:
            client = factory.return_value
            client.base_url = "https://example.invalid/v1"
            client.chat.completions.parse.return_value = response
            caller = APICaller(self.root / "cache")
            args = ("extract", MODELS[0], "test prompt", {"text": "Export CSV."}, Extraction)
            caller.call(*args)
            caller.call(*args)
            self.assertEqual(client.chat.completions.parse.call_count, 1)
            self.assertEqual([c["cached"] for c in caller.calls], [False, True])
            self.assertEqual(client.chat.completions.parse.call_args.kwargs["response_format"], Extraction)
            self.assertEqual(client.chat.completions.parse.call_args.kwargs["max_completion_tokens"], 16384)

    def test_truncated_api_response_retries_with_larger_budget(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(refusal=None, parsed=Extraction(findings=[finding()])))],
            usage=SimpleNamespace(model_dump=lambda: {"total_tokens": 10}))
        truncated = LengthFinishReasonError(completion=SimpleNamespace(
            usage=SimpleNamespace(completion_tokens=16384)))
        with patch("refine.OpenAI") as factory:
            client = factory.return_value
            client.base_url = "https://example.invalid/v1"
            client.chat.completions.parse.side_effect = [truncated, response]
            caller = APICaller(self.root / "cache")
            result = caller.call("extract", MODELS[0], "prompt", {"text": "Export CSV."}, Extraction)
            self.assertEqual(len(result.findings), 1)
            self.assertEqual([call.kwargs["max_completion_tokens"]
                              for call in client.chat.completions.parse.call_args_list], [16384, 32768])
            self.assertTrue(caller.calls[0]["truncated"])
            self.assertEqual(len(list((self.root / "cache").glob("*.json"))), 1)

    def test_persistently_truncated_response_is_not_cached(self):
        truncated = LengthFinishReasonError(completion=SimpleNamespace(
            usage=SimpleNamespace(completion_tokens=8192)))
        with patch("refine.OpenAI") as factory:
            client = factory.return_value
            client.base_url = "https://example.invalid/v1"
            client.chat.completions.parse.side_effect = truncated
            caller = APICaller(self.root / "cache")
            with self.assertRaisesRegex(OutputTruncatedError, "extract response truncated"):
                caller.call("extract", "gpt-4o-mini", "prompt", {"text": "Export CSV."}, Extraction)
            self.assertEqual([call.kwargs["max_completion_tokens"]
                              for call in client.chat.completions.parse.call_args_list], [8192, 16384])
            self.assertFalse((self.root / "cache").exists())

    def test_extraction_truncation_splits_source_and_preserves_review_coverage(self):
        text = "Export CSV.\n" * 300
        (self.corpus / "request.eml").write_text(text, encoding="utf-8")
        class TruncatingCaller(ScriptedCaller):
            def __init__(self):
                super().__init__()
                self.extracted, self.reviewed = [], []
            def call(self, stage, model, prompt, payload, schema):
                if stage == "extract":
                    if len(payload["text"]) > 2000:
                        raise OutputTruncatedError("synthetic length limit")
                    self.extracted.append(payload["text"])
                if stage == "review":
                    self.reviewed.append(payload["text"])
                return super().call(stage, model, prompt, payload, schema)
        caller = TruncatingCaller()
        artifact = self.run_graph(caller)
        self.assertEqual(artifact["status"], "approved")
        self.assertEqual(len(caller.extracted), 2)
        self.assertEqual(caller.reviewed, caller.extracted)
        self.assertTrue(caller.extracted[0].startswith(text[:100]))
        self.assertTrue(caller.extracted[1].endswith(text[-100:]))
        self.assertEqual(artifact["candidates"][0]["chunk"], "CH-001.A")

    def test_truncation_of_small_chunks_does_not_split_forever(self):
        with patch.object(ScriptedCaller, "call", side_effect=OutputTruncatedError("synthetic length limit")):
            with self.assertRaises(OutputTruncatedError):
                self.run_graph(ScriptedCaller())


if __name__ == "__main__":
    unittest.main()
