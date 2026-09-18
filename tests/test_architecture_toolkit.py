"""Packaging and provenance contracts; not a production architecture benchmark."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import fde
import install
PACK = ROOT / 'docs/fde-case-delivery-foundation'

class ArchitectureToolkitTests(unittest.TestCase):
    def data(self, name):
        p = PACK / 'architecture' / name
        self.assertTrue(p.is_file(), 'Architecture reference catalog must exist')
        return json.loads(p.read_text())

    def test_patterns_resolve_and_keep_evidence_status(self):
        data = self.data('catalog.json')
        self.assertEqual(len(data['patterns']), 10)
        ids = [p['id'] for p in data['patterns']]
        self.assertEqual(len(set(ids)), len(ids))
        sources = {s['id'] for s in self.data('sources.json')['sources']}
        for p in data['patterns']:
            self.assertTrue((PACK / 'architecture' / p['path']).is_file())
            self.assertEqual(p['status'], 'candidate_reference')
            self.assertTrue(p['use_when'])
            self.assertTrue(p['avoid_when'])
            self.assertTrue(set(p['source_ids']) <= sources)
            self.assertTrue(p['source_ids'])
            self.assertFalse(p['production_verified'])

    def test_source_coverage_without_host_or_media_payloads(self):
        data = self.data('sources.json')
        self.assertEqual([s['id'] for s in data['sources']], [f'video-{i:03}' for i in range(1, 62)])
        self.assertEqual(sum(s['sampled_frames'] for s in data['sources']), 1842)
        for s in data['sources']:
            self.assertRegex(s['sha256'], r'^[a-f0-9]{64}$')
            self.assertFalse(s['audio_transcribed'])
            self.assertFalse(s['independently_verified'])
        self.assertNotIn('/Users/', json.dumps(data))

    def test_skill_is_discoverable_and_installable(self):
        name = 'fde-architecture-select'
        self.assertIn(name, fde.SKILL_NAMES)
        catalog = json.loads((ROOT / 'catalog.json').read_text())
        match = [s for s in catalog['skills'] if s['name'] == name]
        self.assertEqual(len(match), 1)
        self.assertTrue((ROOT / match[0]['path']).is_file())
        self.assertTrue((PACK / 'templates/architecture-selection.md').is_file())

    def test_project_install_keeps_shared_references_resolvable(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            plan = install.build_plan(ROOT, project, fde.file_hash(ROOT / 'MANIFEST.json'), ['fde-architecture-select'])
            self.assertFalse((project / '.fde').exists())
            install.apply_plan(plan)
            lock = json.loads((project / '.fde/toolbox-lock.json').read_text())
            bundle = project / lock['bundle_root']
            self.assertTrue((bundle / 'docs/fde-case-delivery-foundation/architecture/catalog.json').is_file())
            self.assertTrue((project / '.agents/skills/fde-architecture-select/SKILL.md').is_file())
            self.assertFalse((project / '.agents/skills/fde-delivery').exists())
            self.assertTrue(install.build_plan(ROOT, project, fde.file_hash(ROOT / 'MANIFEST.json'), ['fde-architecture-select'])['already_installed'])

if __name__ == '__main__':
    unittest.main()
