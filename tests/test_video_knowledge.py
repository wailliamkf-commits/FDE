"""Provenance and navigation integrity; not a claim that videos are true."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'docs/fde-case-delivery-foundation'


class VideoKnowledgeTests(unittest.TestCase):
    def entries(self):
        path = PACK / 'source-coverage.json'
        self.assertTrue(path.is_file(), 'The new source coverage index is missing')
        return json.loads(path.read_text(encoding='utf-8'))['entries']

    def test_each_source_version_remains_addressable(self):
        entries = self.entries()
        self.assertEqual([e['id'] for e in entries], [f'new-video-{n:03}' for n in range(1, 134)])
        self.assertEqual(len({e['source_sha256'] for e in entries}), 133)
        for e in entries:
            self.assertRegex(e['source_sha256'], r'^[a-f0-9]{64}$')
            self.assertRegex(e['report_sha256'], r'^[a-f0-9]{64}$')
            self.assertTrue(e['disposition'])
            self.assertTrue(e['uncertainties'])
            self.assertTrue(e['details'] or e['disposition'] == 'EXCLUDED')

    def test_replacements_do_not_silently_merge_evidence(self):
        entries = {e['id']: e for e in self.entries()}
        expected = dict(zip(range(124, 134), [5, 13, 14, 15, 16, 17, 18, 19, 20, 21]))
        for n in range(1, 134):
            e = entries[f'new-video-{n:03}']
            old = expected.get(n)
            self.assertEqual(e['revision_of'], f'new-video-{old:03}' if old else None)
            if old:
                self.assertNotEqual(e['source_sha256'], entries[e['revision_of']]['source_sha256'])

    def test_all_methods_resolve_to_real_anchors(self):
        for e in self.entries():
            self.assertTrue(e['methods'])
            for target in e['methods']:
                relative, sep, anchor = target.partition('#')
                p = (PACK / relative).resolve()
                self.assertTrue(p.is_relative_to(PACK))
                self.assertTrue(p.is_file(), (e['id'], target))
                if sep:
                    self.assertRegex(p.read_text(), r'id=[\"\']' + re.escape(anchor) + r'[\"\']')

    def test_portable_index_does_not_publish_local_locations(self):
        raw = json.dumps(self.entries(), ensure_ascii=False)
        self.assertNotRegex(raw, r'/Users/|/home/|file://|Desktop|原始交付/')

    def test_every_original_detail_has_an_explicit_disposition(self):
        entries = self.entries()
        mapped = withheld = 0
        for e in entries:
            coverage = e['detail_coverage']
            self.assertEqual([c['source_detail_index'] for c in coverage],
                             list(range(1, e['source_detail_count'] + 1)), e['id'])
            for c in coverage:
                self.assertRegex(c['source_detail_sha256'], r'^[a-f0-9]{64}$')
                self.assertTrue(c['source_kind'])
                targets = c.get('detail_indices', [])
                reason = c.get('withhold_reason', '')
                self.assertNotEqual(bool(targets), bool(reason), (e['id'], c))
                self.assertEqual(len(targets), len(set(targets)))
                for target in targets:
                    self.assertIs(type(target), int)
                    self.assertGreaterEqual(target, 1)
                    self.assertLessEqual(target, len(e['details']))
                    self.assertTrue(e['details'][target - 1].strip())
                mapped += bool(targets)
                withheld += bool(reason)
        self.assertEqual((mapped, withheld, mapped + withheld), (406, 22, 428))


if __name__ == '__main__':
    unittest.main()
