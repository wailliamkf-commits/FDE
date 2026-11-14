"""Validate delivered navigation and honest scope, not external media or claim truth."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/media-intake"


class MediaIntakeTests(unittest.TestCase):
    def data(self):
        return json.loads((PACK / "sources.json").read_text(encoding="utf-8"))

    def test_complete_navigation_preserves_denominators(self):
        data = self.data()
        rows = data["sources"]
        self.assertEqual(len(rows), 382)
        self.assertEqual([r["id"] for r in rows], [f"MI-{i:03d}" for i in range(1, 383)])
        self.assertEqual(len({r["unit_id"] for r in rows}), 382)
        self.assertEqual(sum(r["source_file_count"] for r in rows), 573)
        self.assertEqual(sum(r["source_file_count"] for r in rows if r["kind"] == "video"), 354)
        self.assertEqual(sum(r["source_file_count"] for r in rows if r["kind"] == "image"), 219)
        for row in rows:
            self.assertEqual(len(row["source_sha256"]), row["source_file_count"])
            for digest in row["source_sha256"] + [row["analysis_sha256"]]:
                self.assertRegex(digest, r"^[a-f0-9]{64}$")

    def test_incomplete_source_is_not_promoted(self):
        data = self.data()
        accepted = [r for r in data["sources"] if r["decision"] == "accepted_visual"]
        limited = [r for r in data["sources"] if r["decision"] == "limited_visual"]
        self.assertEqual(len(accepted), 381)
        self.assertEqual(sum(r["source_file_count"] for r in accepted), 572)
        self.assertEqual([r["unit_id"] for r in limited], ["u-73f9242946b4dc40e8d2"])
        self.assertEqual(limited[0]["scope"], "incomplete_visual_semantics")
        self.assertEqual(data["mode"], "visual_only")
        self.assertFalse(data["originals_included"])
        self.assertFalse(data["runtime_included"])
        for row in data["sources"]:
            self.assertFalse(row["business_effect_tested"])
            self.assertTrue(row["evidence_is_external"])
            self.assertEqual(row["target_business"], "unknown")
            self.assertEqual(row["evidence_locator"], f"逐项报告/{row['unit_id']}/Codex核查与分析.md")

    def test_reference_pack_is_discoverable_and_links_resolve(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        rows = [r for r in catalog["reference_packs"] if r["name"] == "fde-media-intake"]
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["native_skill"])
        self.assertEqual(rows[0]["source_index"], "docs/media-intake/sources.json")
        for path in PACK.glob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT))
                self.assertTrue(resolved.is_file(), f"{path.name}: {target}")

    def test_project_execution_state_stays_external(self):
        for path in PACK.glob("*"):
            if path.is_file():
                text = path.read_text()
                self.assertNotIn("/Users/", text)
                self.assertNotIn("127.0.0.1", text)
                self.assertNotIn(".Trash/", text)
        self.assertFalse((PACK / "worker.mjs").exists())
        self.assertFalse((PACK / "cleanup.mjs").exists())


if __name__ == "__main__":
    unittest.main()
