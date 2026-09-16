"""Reference-pack integrity, not business validation or model behavior."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'docs' / 'fde-case-delivery-foundation'


class CaseFoundationTests(unittest.TestCase):
    def load_cases(self):
        path = PACK / 'cases.json'
        self.assertTrue(path.is_file(), 'Case evidence index must be delivered')
        return json.loads(path.read_text(encoding='utf-8'))

    def test_case_coverage_and_page_provenance(self):
        data = self.load_cases()
        cases = data['cases']
        self.assertEqual([c['id'] for c in cases], [f'DW-{i:02}' for i in range(1, 25)])
        pages = []
        for case in cases:
            start, end = case['physical_pages']
            self.assertLessEqual(start, end)
            pages.extend(range(start, end + 1))
            self.assertTrue(case['reported_approach'])
            self.assertTrue(case['limitations'])
            self.assertFalse(case['independently_verified'])
        self.assertEqual(pages, list(range(7, 245)))
        self.assertEqual(data['source']['physical_page_count'], 246)

    def test_claim_types_remain_distinct(self):
        cases = {c['id']: c for c in self.load_cases()['cases']}
        self.assertEqual(cases['DW-01']['claims'][0]['kind'], 'acceptance_threshold')
        self.assertEqual(cases['DW-06']['claims'][0]['kind'], 'projection')
        self.assertEqual(cases['DW-24']['claims'][0]['kind'], 'anonymized_report')
        for case in cases.values():
            for claim in case['claims']:
                self.assertIn(claim['kind'], {'acceptance_threshold', 'projection', 'reported_result', 'anonymized_report', 'not_measured'})
                self.assertTrue(claim['qualification'])
                self.assertTrue(set(claim['physical_pages']).issubset(set(range(case['physical_pages'][0], case['physical_pages'][1]+1))))

    def test_catalog_resource_paths_and_source_identity(self):
        catalog = json.loads((ROOT / 'catalog.json').read_text())
        entries = catalog.get('reference_packs', [])
        match = [e for e in entries if e['name'] == 'fde-case-delivery-foundation']
        self.assertEqual(len(match), 1, 'Reference pack must be discoverable in catalog')
        self.assertTrue((ROOT / match[0]['path']).is_file())
        source = self.load_cases()['source']
        self.assertRegex(source['sha256'], r'^[a-f0-9]{64}$')
        self.assertFalse(source['original_included'])

    def test_pack_links_resolve_inside_bundle(self):
        self.assertTrue((PACK / 'README.md').is_file())
        for path in PACK.rglob('*.md'):
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                resolved = (path.parent / target.split('#', 1)[0]).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT))
                self.assertTrue(resolved.is_file(), f'{path.name}: {target}')


if __name__ == '__main__':
    unittest.main()
