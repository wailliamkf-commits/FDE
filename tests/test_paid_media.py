"""Offline packaging contracts, not model behavior or live advertising validation."""
import hashlib
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

ADS = {"google-ads-diagnostics": "2.1.0", "meta-ads-diagnostics": "1.1.0"}


class PaidMediaPackagingTests(unittest.TestCase):
    def test_catalog_and_installer_agree(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        names = [s["name"] for s in catalog["skills"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), set(fde.SKILL_NAMES))
        self.assertEqual(catalog["version"], fde.VERSION)
        for entry in catalog["skills"]:
            self.assertEqual(entry["path"], f"skills/{entry['name']}/SKILL.md")
            self.assertTrue((ROOT / entry["path"]).is_file())
            if entry["name"] in ADS:
                self.assertEqual(entry["category"], "growth/paid-media")
                self.assertEqual(entry["content_version"], ADS[entry["name"]])

    def test_metadata_and_display_prompts(self):
        for name, version in ADS.items():
            with self.subTest(skill=name):
                content = (ROOT / "skills" / name / "SKILL.md").read_text()
                self.assertTrue(content.startswith(f"---\nname: {name}\n"))
                frontmatter = content.split("---", 2)[1]
                self.assertIn(f'version: "{version}"', frontmatter)
                self.assertIn('category: "growth/paid-media"', frontmatter)
                ui = (ROOT / "skills" / name / "agents/openai.yaml").read_text()
                self.assertIn(f"${name}", ui)
                short = re.search(r'short_description: "([^"]+)"', ui).group(1)
                self.assertTrue(25 <= len(short) <= 64)

    def test_skill_links_are_self_contained(self):
        for name in ADS:
            skill = ROOT / "skills" / name
            for path in skill.rglob("*.md"):
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                    if urlsplit(target).scheme or target.startswith("#"):
                        continue
                    resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                    with self.subTest(path=path.name, target=target):
                        self.assertTrue(resolved.is_relative_to(skill))
                        self.assertTrue(resolved.is_file())

    def test_paid_media_document_links_exist(self):
        for path in (ROOT / "docs/paid-media").rglob("*.md"):
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if urlsplit(target).scheme or target.startswith("#"):
                    continue
                resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                with self.subTest(path=path.name, target=target):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file())

    def test_meta_reference_definitions_are_unique_and_complete(self):
        base = ROOT / "skills/meta-ads-diagnostics/references"
        data = (base / "data-map.md").read_text()
        playbook = (base / "diagnostic-playbook.md").read_text()
        for prefix, count, content in (("D", 14, data), ("M", 16, data), ("P", 17, playbook)):
            definitions = re.findall(rf"^### {prefix}(\d{{2}})\s", content, re.M)
            self.assertEqual(definitions, [f"{n:02d}" for n in range(1, count + 1)])
        self.assertLessEqual(set(re.findall(r"\bD(\d{2})\b", playbook)), {f"{n:02d}" for n in range(1, 15)})

    def test_google_data_and_problem_map_counts(self):
        base = ROOT / "skills/google-ads-diagnostics/references"
        ids = re.findall(r"^\|(\d{2})\|", (base / "data-sources.md").read_text(), re.M)
        self.assertEqual(ids, [f"{n:02d}" for n in range(1, 17)])
        matrix = (base / "diagnosis-matrix.md").read_text().split("## 定责", 1)[0]
        rows = [line for line in matrix.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows) - 2, 12)

    def test_google_fixtures_remain_explicitly_synthetic(self):
        folder = ROOT / "docs/paid-media/imported/google/validation/inputs"
        ids = []
        for path in sorted(folder.glob("*.json")):
            content = json.loads(path.read_text())
            self.assertIn("合成", content["notice"])
            ids.extend(case["id"] for case in content["cases"])
        self.assertEqual(set(ids), {"mixed-goals", "funnel-and-devices", "shopping-route", "b2b-qualification"})
        self.assertEqual(len(ids), 4)

    def test_imported_reports_cannot_appear_as_current_results(self):
        paths = list((ROOT / "docs/paid-media/imported").rglob("*.md"))
        self.assertEqual(len(paths), 3)
        for path in paths:
            self.assertIn("IMPORTED_HISTORICAL", path.read_text().splitlines()[0])

    def test_reviewed_import_has_only_declared_edits(self):
        provenance = json.loads((ROOT / "docs/paid-media/source-map.json").read_text())
        self.assertEqual(provenance["toolbox_version"], fde.VERSION)
        self.assertFalse(provenance["history_complete"])
        self.assertEqual(len(provenance["files"]), 20)
        paths = [entry["path"] for entry in provenance["files"]]
        self.assertEqual(len(paths), len(set(paths)))
        for entry in provenance["files"]:
            content = (ROOT / entry["path"]).read_text()
            appendix = entry.get("local_appendix")
            if appendix:
                self.assertEqual(appendix["version"], ADS["google-ads-diagnostics"])
                self.assertEqual(content.count(appendix["marker"]), 1)
                original, tail = content.split(appendix["marker"], 1)
                extension = appendix["marker"] + tail
                self.assertEqual(hashlib.sha256(extension.encode()).hexdigest(), appendix["sha256"])
                content = original.replace(f'version: "{appendix["version"]}"', 'version: "2.0.0"', 1)
            if entry["edits"] == "prepend historical notice":
                content = content.split("\n\n", 1)[1]
            elif entry["edits"] == "add final newline":
                self.assertTrue(content.endswith("\n"))
                content = content[:-1]
            elif entry["edits"] == "add version/category metadata":
                content = content.replace('metadata:\n  version: "2.0.0"\n  category: "growth/paid-media"\n', '', 1)
            elif entry["edits"] == "replace provisional classification line":
                content = content.replace(
                    '- 分类为 `growth/paid-media`；资料在本技能目录内按需读取，真实项目数据留在用户批准的项目资料位置。',
                    '- 建议分类为 `growth/paid-media`；具体仓库路径和入口索引遵循目标仓库规范，不重排整个技能库。', 1)
            else:
                self.assertEqual(entry["edits"], "none")
            with self.subTest(path=entry["path"]):
                self.assertEqual(hashlib.sha256(content.encode()).hexdigest(), entry["original_sha256"])

    def test_each_ads_skill_installs_in_isolation_and_preserves_other_skills(self):
        expected = fde.file_hash(ROOT / "MANIFEST.json")
        for name in ADS:
            with self.subTest(skill=name), tempfile.TemporaryDirectory(prefix="fde-ads-test-") as folder:
                project = Path(folder)
                previous = project / ".agents/skills/user-existing/SKILL.md"
                previous.parent.mkdir(parents=True)
                previous.write_text("existing user skill\n")
                plan = install.build_plan(ROOT, project, expected, [name])
                self.assertEqual(plan["mode"], "DRY_RUN")
                self.assertFalse((project / ".agents/skills" / name).exists())
                result = install.apply_plan(plan)
                self.assertEqual(result["mode"], "INSTALLED_FILES_ONLY")
                self.assertFalse(result["native_registration_verified"])
                self.assertEqual(previous.read_text(), "existing user skill\n")
                source = ROOT / "skills" / name
                target = project / ".agents/skills" / name
                for path in source.rglob("*"):
                    if path.is_file():
                        self.assertEqual(path.read_bytes(), (target / path.relative_to(source)).read_bytes())
                self.assertEqual({p.name for p in target.parent.iterdir()}, {name, "user-existing"})
                again = install.apply_plan(install.build_plan(ROOT, project, expected, [name]))
                self.assertEqual(again["mode"], "ALREADY_INSTALLED")


if __name__ == "__main__":
    unittest.main()
