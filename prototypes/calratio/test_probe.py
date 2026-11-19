"""Offline safeguards; toy ROOT files here are never extraction evidence."""

import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import awkward as ak
import numpy as np
import uproot

import probe


class Safeguards(unittest.TestCase):
    def test_public_status_drops_service_credentials_and_signed_urls(self):
        value = probe.public_diagnostics(
            {"request_id": "test", "image": "release", "minio_access_key": "dummy-access",
             "minio_secret_key": "dummy-secret", "future_credential_field": "dummy-future"},
            {"results": [{"transform_status": "success", "token": "dummy-token",
                          "signed_url": "https://example.invalid/?signature=dummy"}]})
        self.assertEqual(value, {"status": {"request_id": "test", "image": "release"},
                                 "results": [{"transform_status": "success"}]})
        self.assertNotIn("dummy", json.dumps(value))

    def test_split_writes_do_not_leak_a_secret(self):
        stream = io.StringIO()
        safe = probe.SafeLog(stream, ["dummy-private-token"])
        safe.write("dummy-private-")
        safe.write("token https://example.invalid/?X-Amz-Signature=dummy\n")
        safe.flush()
        self.assertNotIn("dummy", stream.getvalue())
        self.assertNotIn("Signature", stream.getvalue())

    def test_data_root_precedence_and_missing_override(self):
        with tempfile.TemporaryDirectory(dir=probe.REPO / ".work") as tmp:
            base = Path(tmp)
            for name in ("config", "env", "explicit"):
                (base / name).mkdir()
            (base / "data.local.toml").write_text('[data]\nroot = "' + (base / "config").as_posix() + '"\n')
            with patch.object(probe, "REPO", base), patch.dict(os.environ, {}, clear=True):
                self.assertEqual(probe.data_root()[0], (base / "config").resolve())
                os.environ["IRIS_HEP_DATA_DIR"] = str(base / "env")
                self.assertEqual(probe.data_root()[0], (base / "env").resolve())
                self.assertEqual(probe.data_root(base / "explicit")[0], (base / "explicit").resolve())
                with self.assertRaises(FileNotFoundError):
                    probe.data_root(base / "missing")

    def test_root_inspection_exposes_bad_alignment_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory(dir=probe.REPO / ".work") as tmp:
            path = Path(tmp) / "toy.root"
            with uproot.recreate(path) as f:
                tree = f.mktree("events", {"run": "uint32", "lb": "uint32", "event": "uint64",
                                         "jet_pt": "var * float64", "jet_eta": "var * float64"})
                tree.extend({"run": np.array([1, 1], dtype=np.uint32), "lb": np.array([2, 2], dtype=np.uint32),
                             "event": np.array([3, 3], dtype=np.uint64),
                             "jet_pt": ak.Array([[1.0, np.nan], []]), "jet_eta": ak.Array([[0.0], []])})
            result = probe.inspect_files([path])[0]
            self.assertFalse(result["alignment"]["jet_"])
            self.assertEqual(result["duplicate_event_keys"], 1)
            self.assertEqual(result["columns"]["jet_pt"]["nonfinite"], 1)

    def test_run_id_cannot_escape_bulk_directory(self):
        with self.assertRaises(ValueError):
            probe.run_dir(Path("data"), "../outside")

    def test_replay_rebases_recorded_paths_and_rejects_escape(self):
        work = (probe.REPO / ".work" / "moved-run").resolve()
        record = {"data_root": "D:/old-data", "files": ["D:/old-data/calratio/moved-run/smoke/output.root"]}
        self.assertEqual(probe.delivery_paths(work, record), [work / "smoke/output.root"])
        record["files"] = ["D:/old-data/calratio/moved-run/../outside.root"]
        with self.assertRaises(ValueError):
            probe.delivery_paths(work, record)
