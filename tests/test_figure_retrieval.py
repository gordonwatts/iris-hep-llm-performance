"""Synthetic file/evidence regressions; no protected note text or figure assets."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from pypdf import PdfWriter
import yaml

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("figure_retrieval", REPO / "scripts/figure_retrieval.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FigureValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = self.root / "catalog.json"
        self.catalog.write_text(json.dumps({"cases": {"synthetic": {
            "note_id": "TEST-NOTE", "figure_numbers": [1, 2]}}}))
        self.fixture = self.root / "targets.json"
        self.fixture.write_text(json.dumps({"cases": {"synthetic": {
            "note_id": "TEST-NOTE", "figure_numbers": [1, 2],
            "caption_hint": "Synthetic caption one"}}}))
        self.patcher = patch.object(module, "CATALOG", self.catalog)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.manifest = {"schema_version": 1, "case_id": "synthetic", "requests": [], "figures": []}
        for n in (1, 2):
            caption = "Synthetic caption " + ("one" if n == 1 else "two")
            image = Image.new("RGB", (32, 32), "white")
            ImageDraw.Draw(image).line((n, 1, 30, 28 - n), fill="black", width=n)
            image.save(self.root / f"figure-{n}.png")
            receipt = {"note_id": "TEST-NOTE", "figure_number": n,
                       "caption": caption, "source_record": f"synthetic-index-record-{n}",
                       "source_version": "synthetic-revision-1"}
            (self.root / f"mapping-{n}.json").write_text(json.dumps(receipt))
            self.manifest["requests"].append({"id": str(n), "tool": "mcp__atlas_af__synthetic_payload",
                "stage": "payload", "status": "succeeded", "query": {"figure": n},
                "result_record": f"synthetic-result-{n}"})
            self.manifest["figures"].append({"number": n, "note_id": "TEST-NOTE", "status": "retrieved",
                "caption": caption, "mapping_verified": True,
                "source_version": "synthetic-revision-1",
                "mapping_receipt": self.record(f"mapping-{n}.json"),
                "retrieval_request_id": str(n), "payload": {**self.record(f"figure-{n}.png"),
                    "bytes": (self.root / f"figure-{n}.png").stat().st_size,
                    "media_type": "image/png", "route": "mcp_figure",
                    "source_locator": f"mcp://synthetic/figures/{n}"}})

    def record(self, name):
        return {"path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def validate(self):
        (self.root / "retrieval-evidence.json").write_text(json.dumps(self.manifest))
        return module.validate_manifest(self.root, self.fixture, "synthetic")

    def test_distinct_decoded_payloads_and_caption_mapping(self):
        result = self.validate()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["caption_hint_matched_figures"], [1])

    def test_each_requested_figure_is_required(self):
        self.manifest["figures"].pop()
        self.assertFalse(self.validate()["passed"])

    def test_metadata_hit_is_not_payload_retrieval(self):
        self.manifest["figures"][0]["status"] = "metadata_only"
        self.assertFalse(self.validate()["passed"])

    def test_successful_search_request_is_not_payload_provenance(self):
        self.manifest["requests"][0]["stage"] = "search"
        self.assertFalse(self.validate()["passed"])

    def test_partial_success_preserves_both_outcomes(self):
        self.manifest["figures"][1]["status"] = "payload_error"
        result = self.validate()
        self.assertFalse(result["passed"])
        self.assertTrue(result["figures"][0]["passed"])
        self.assertFalse(result["figures"][1]["passed"])

    def test_unrelated_captions_do_not_satisfy_search_hint(self):
        fixture = json.loads(self.fixture.read_text())
        fixture["cases"]["synthetic"]["caption_hint"] = "Different requested topic"
        self.fixture.write_text(json.dumps(fixture))
        self.assertFalse(self.validate()["passed"])

    def test_source_revision_must_be_preserved(self):
        self.manifest["figures"][0]["source_version"] = "other-revision"
        self.assertFalse(self.validate()["passed"])

    def test_rejected_access_is_retained_per_figure_and_fails(self):
        for row in self.manifest["figures"]:
            row["status"] = "blocked_access"
            row["payload"] = None
        result = self.validate()
        self.assertFalse(result["passed"])
        self.assertEqual(len(result["figures"]), 2)

    def test_swapped_caption_mapping(self):
        self.manifest["figures"][1]["mapping_receipt"] = self.manifest["figures"][0]["mapping_receipt"]
        self.assertFalse(self.validate()["passed"])

    def test_caption_mapping_cannot_be_assumed(self):
        self.manifest["figures"][1]["mapping_verified"] = False
        self.assertFalse(self.validate()["passed"])

    def test_html_masquerading_as_image(self):
        p = self.root / "figure-1.png"
        p.write_text("<html>Please sign in</html>")
        self.manifest["figures"][0]["payload"].update(self.record(p.name), bytes=p.stat().st_size)
        self.assertFalse(self.validate()["passed"])

    def test_missing_or_modified_payload(self):
        (self.root / "figure-1.png").write_bytes(b"")
        self.assertFalse(self.validate()["passed"])

    def test_wrong_note_or_figure_identity(self):
        self.manifest["figures"][0]["note_id"] = "OTHER-NOTE"
        self.assertFalse(self.validate()["passed"])

    def test_payload_path_cannot_escape_workspace(self):
        self.manifest["figures"][0]["payload"]["path"] = "../outside.png"
        self.assertFalse(self.validate()["passed"])

    def test_duplicate_payload_for_two_figures(self):
        self.manifest["figures"][1]["payload"] = copy.deepcopy(self.manifest["figures"][0]["payload"])
        self.assertFalse(self.validate()["passed"])

    def test_signed_url_is_not_retained(self):
        self.manifest["figures"][0]["payload"]["source_locator"] += "?token=synthetic"
        self.assertFalse(self.validate()["passed"])

    def test_archived_crop_cannot_pass_as_live_retrieval(self):
        self.manifest["figures"][0]["payload"]["route"] = "archive_reference"
        self.assertFalse(self.validate()["passed"])

    def test_whole_note_is_not_a_figure_payload(self):
        path = self.root / "whole-note.pdf"
        writer = PdfWriter()
        writer.add_blank_page(200, 200)
        writer.add_blank_page(200, 200)
        with path.open("wb") as stream:
            writer.write(stream)
        with self.assertRaises(ValueError):
            module.check_payload(path, "application/pdf")

    def test_prepare_does_not_seed_private_archive_or_write_in_repo(self):
        fixture = json.loads(self.fixture.read_text())
        fixture["cases"]["synthetic"]["archive_path"] = "DO-NOT-STAGE.pdf"
        self.fixture.write_text(json.dumps(fixture))
        suite = {"questions": [{"id": "synthetic"}]}
        with patch.object(module.yaml, "safe_load", return_value=suite):
            runtime = module.prepare_run("synthetic", self.fixture, self.root, "bounded")
        staged = json.loads((runtime.parent / "inputs/figure-targets.json").read_text())
        self.assertNotIn("archive_path", staged["cases"]["synthetic"])
        self.assertFalse(json.loads((runtime.parent / "provenance.json").read_text())["payloads_seeded"])
        with self.assertRaises(FileExistsError):
            module.prepare_run("synthetic", self.fixture, self.root, "bounded")


class CaseDefinitions(unittest.TestCase):
    def test_public_catalogue_contains_no_caption_text_or_payload_path(self):
        cases = json.loads((REPO / "spec/figure-retrieval-cases.json").read_text())["cases"]
        for case in cases.values():
            self.assertNotIn("caption_hint", case)
            self.assertNotIn("expected_captions", case)
            self.assertNotIn("archive_path", case)

    def test_exactly_two_new_cases_in_existing_suite(self):
        suite = yaml.safe_load((REPO / "atlas-metadata-queries.yaml").read_text())
        cases = json.loads((REPO / "spec/figure-retrieval-cases.json").read_text())["cases"]
        added = [q for q in suite["questions"] if q["id"] in cases]
        self.assertEqual(len(added), 2)
        self.assertEqual(len(suite["questions"]), 8)
        self.assertEqual(sorted(len(c["figure_numbers"]) for c in cases.values()), [1, 2])
        for question in added:
            self.assertEqual(question["validators"][0]["name"], "figure_retrieval")
            self.assertEqual(question["validators"][0]["arguments"]["case_id"], question["id"])


if __name__ == "__main__":
    unittest.main()
