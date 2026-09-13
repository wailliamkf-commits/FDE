"""Offline packaging checks, not model behavior, deployment or business outcomes."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fde
import install

NAME = "fde-brand-site"
BASE = ROOT / "skills" / NAME


class BrandSitePackagingTests(unittest.TestCase):
    def test_catalog_and_ui_contract(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        entry = next(item for item in catalog["skills"] if item["name"] == NAME)
        self.assertEqual(entry["content_version"], "1.0.0")
        self.assertEqual(entry["category"], "brand/storefront")
        self.assertIn(NAME, fde.SKILL_NAMES)
        text = (BASE / "SKILL.md").read_text()
        self.assertTrue(text.startswith(f"---\nname: {NAME}\n"))
        self.assertIn('version: "1.0.0"', text.split("---", 2)[1])
        ui = (BASE / "agents/openai.yaml").read_text()
        self.assertIn(f"${NAME}", ui)
        short = re.search(r'short_description: "([^"]+)"', ui).group(1)
        self.assertTrue(25 <= len(short) <= 64)

    def test_local_links_remain_self_contained(self):
        for path in BASE.rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if urlsplit(target).scheme or target.startswith("#"):
                    continue
                resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                with self.subTest(file=path.name, target=target):
                    self.assertTrue(resolved.is_relative_to(BASE))
                    self.assertTrue(resolved.is_file())

    def test_expected_resources_are_packaged(self):
        expected = {
            "business-adaptation.md", "model-orchestration.md", "market-competitors.md",
            "architecture-content.md", "visual-interaction.md", "discovery-growth.md",
            "release-maintenance.md", "sources.md",
        }
        self.assertEqual({p.name for p in (BASE / "references").glob("*.md")}, expected)
        templates = {"research-page-workbook.md", "visual-state-contract.md",
                     "content-experiments.md", "release-improvement.md", "model-work-order.md"}
        self.assertEqual({p.name for p in (BASE / "assets").glob("*.md")},
                         templates | {"forward-cases.md"})

    def test_routing_remains_intent_and_has_no_frozen_model_id(self):
        routing = json.loads((ROOT / "configs/model-routing.example.json").read_text())
        self.assertEqual(routing["type"], "intent_not_native_configuration")
        self.assertFalse(routing["auto_update"])
        self.assertTrue(routing["provider_changes_require_approval"])
        self.assertEqual(routing["planner_policy"]["executor_selected_by"], "planner")
        self.assertTrue(routing["planner_policy"]["lock_within_batch"])
        self.assertTrue((ROOT / routing["planner_policy"]["reference"]).is_file())
        for route in routing["routes"]:
            self.assertIsNone(route["requested_model"])
            self.assertEqual(route["effective_model"], "UNKNOWN")

    def test_isolated_install_preserves_user_files_and_is_idempotent(self):
        expected = fde.file_hash(ROOT / "MANIFEST.json")
        with tempfile.TemporaryDirectory(prefix="fde-brand-site-test-") as folder:
            project = Path(folder)
            existing = project / "AGENTS.md"
            existing.write_text("existing project instructions\n")
            plan = install.build_plan(ROOT, project, expected, [NAME])
            self.assertEqual(plan["mode"], "DRY_RUN")
            self.assertFalse((project / ".agents").exists())
            result = install.apply_plan(plan)
            self.assertEqual(result["mode"], "INSTALLED_FILES_ONLY")
            self.assertFalse(result["native_registration_verified"])
            self.assertEqual(existing.read_text(), "existing project instructions\n")
            target = project / ".agents/skills" / NAME
            for path in BASE.rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (target / path.relative_to(BASE)).read_bytes())
            self.assertEqual({p.name for p in target.parent.iterdir()}, {NAME})
            again = install.apply_plan(install.build_plan(ROOT, project, expected, [NAME]))
            self.assertEqual(again["mode"], "ALREADY_INSTALLED")


if __name__ == "__main__":
    unittest.main()
