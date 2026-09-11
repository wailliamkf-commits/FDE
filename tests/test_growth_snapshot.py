"""Synthetic metric-contract regressions; no business or platform integration proof."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/fde-brand-growth"
spec = importlib.util.spec_from_file_location("growth_snapshot", SKILL / "scripts/audit_snapshot.py")
growth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(growth)


def sample():
    return json.loads((SKILL / "assets/snapshot.synthetic.json").read_text())


class SnapshotTests(unittest.TestCase):
    def test_descriptive_result_never_implies_business_success(self):
        r = growth.audit(sample())
        self.assertEqual(r["ratios"]["attributed_purchase_roas"], 1.8)
        self.assertEqual(r["ratios"]["intent_match_rate"], 0.75)
        self.assertEqual(r["ratios"]["purchase_session_rate"], 0.02)
        self.assertEqual(r["business_verdict"], "NOT_ASSESSED")
        self.assertFalse(r["source_verified"])

    def test_mixed_conversion_value_cannot_be_purchase_roas(self):
        d = sample(); d["scope"]["conversion_action"] = "purchase_and_atc"
        r = growth.audit(d)
        self.assertIn("NOT_PURCHASE_ONLY", r["blocks"])
        self.assertIsNone(r["ratios"]["attributed_purchase_roas"])

    def test_immature_no_scale_signal(self):
        d = sample(); d["quality"]["mature"] = False
        r = growth.audit(d)
        self.assertIsNone(r["ratios"]["purchase_session_rate"])
        self.assertIsNone(r["ratios"]["attributed_purchase_roas"])
        self.assertEqual(r["ratios"]["intent_match_rate"], 0.75)

    def test_cross_cohort_blocks_all_ratios(self):
        d = sample(); d["quality"]["same_cohort"] = False
        self.assertTrue(all(v is None for v in growth.audit(d)["ratios"].values()))

    def test_no_dedup_blocks_session_rates(self):
        d = sample(); d["quality"]["deduplicated"] = False
        result = growth.audit(d)
        self.assertIsNone(result["ratios"]["purchase_session_rate"])
        self.assertIsNone(result["ratios"]["attributed_purchase_roas"])

    def test_unknown_is_not_zero(self):
        d = sample(); d["metrics"]["purchase_value"] = None
        self.assertIsNone(growth.audit(d)["ratios"]["attributed_purchase_roas"])

    def test_zero_spend_not_infinite_return(self):
        d = sample(); d["metrics"]["spend"] = 0
        self.assertIsNone(growth.audit(d)["ratios"]["attributed_purchase_roas"])

    def test_negative_adjusted_value_retained(self):
        d = sample(); d["metrics"]["purchase_value"] = -100
        self.assertEqual(growth.audit(d)["ratios"]["attributed_purchase_roas"], -0.1)

    def test_session_subset_rejected(self):
        for key in ("purchase_sessions", "qualified_sessions", "intent_known_sessions", "intent_matched_sessions"):
            with self.subTest(key=key):
                d = sample(); d["metrics"][key] = 2000
                with self.assertRaises(ValueError): growth.audit(d)

    def test_unknown_parent_cannot_hide_matched_excess(self):
        d = sample(); d["metrics"]["intent_known_sessions"] = None; d["metrics"]["intent_matched_sessions"] = 2000
        with self.assertRaises(ValueError): growth.audit(d)

    def test_bad_numeric_types(self):
        for value in (True, float("nan"), float("inf"), -1, 2.5, "20"):
            with self.subTest(value=value):
                d = sample(); d["metrics"]["purchase_sessions"] = value
                with self.assertRaises(ValueError): growth.audit(d)

    def test_channel_totals_reconcile(self):
        d = sample(); d["channels"][0]["sessions"] += 1
        with self.assertRaises(ValueError): growth.audit(d)

    def test_repeat_is_not_channel(self):
        d = sample(); d["channels"][0]["channel"] = "repeat"
        with self.assertRaises(ValueError): growth.audit(d)

    def test_duplicate_channel(self):
        d = sample(); d["channels"][0]["channel"] = "organic_search"
        with self.assertRaises(ValueError): growth.audit(d)

    def test_overlapping_channel_flag_blocks_shares(self):
        d = sample(); d["quality"]["exclusive_channels"] = False
        self.assertIsNone(growth.audit(d)["channel_shares"])

    def test_missing_channel_data(self):
        d = sample(); d["channels"] = None
        self.assertIsNone(growth.audit(d)["channel_shares"])

    def test_invalid_period_and_timezone(self):
        for key, value in (("period_start", "2026-08-31"), ("period_end", "2026-02-30"), ("timezone", "invalid-zone")):
            d = sample(); d["scope"][key] = value
            with self.assertRaises(ValueError): growth.audit(d)

    def test_unknown_fields_rejected(self):
        d = sample(); d["customer_email"] = "not-used"
        with self.assertRaises(ValueError): growth.audit(d)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "input.json"; p.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ValueError): growth.load(p)

    def test_cli_success_and_contract_block_exit_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "input.json"
            for mature, expected in ((True, 0), (False, 3)):
                d = sample(); d["quality"]["mature"] = mature; p.write_text(json.dumps(d))
                run = subprocess.run([sys.executable, "-I", "-B", str(SKILL / "scripts/audit_snapshot.py"), str(p)], capture_output=True, text=True)
                self.assertEqual(run.returncode, expected)
                self.assertEqual(json.loads(run.stdout)["business_verdict"], "NOT_ASSESSED")

    def test_zero_sessions_defined_as_unavailable(self):
        d = sample()
        for key in growth.COUNTS: d["metrics"][key] = 0
        d["channels"] = []
        r = growth.audit(d)
        self.assertIsNone(r["ratios"]["purchase_session_rate"])
        self.assertIsNone(r["channel_shares"])


if __name__ == "__main__":
    unittest.main()
