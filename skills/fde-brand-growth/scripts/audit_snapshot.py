#!/usr/bin/env python3
"""Offline contract checks for one normalized snapshot, not an attribution engine."""
from __future__ import annotations

import argparse
from datetime import date
import json
import math
from pathlib import Path
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CHANNELS = {"paid_search", "paid_social", "organic_search", "organic_social", "email", "referral", "direct", "other", "unknown"}
COUNTS = {"sessions", "intent_known_sessions", "intent_matched_sessions", "qualified_sessions", "purchase_sessions"}
SCOPE = {"source_id", "account", "demand_unit", "period_start", "period_end", "timezone", "currency", "conversion_action", "date_basis", "attribution_model"}
QUALITY = {"mature", "same_cohort", "deduplicated", "exclusive_channels"}


def exact(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != keys:
        raise ValueError(f"Invalid fields: {label}")


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def reject_constant(_):
    raise ValueError("Non-finite JSON number")


def load(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError("Expected bounded regular JSON file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=reject_constant)


def audit(data):
    exact(data, {"schema_version", "evidence_type", "scope", "quality", "metrics", "channels"}, "root")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["evidence_type"] not in ("synthetic", "observed"):
        raise ValueError("Invalid version or evidence type")
    scope, quality, m = data["scope"], data["quality"], data["metrics"]
    exact(scope, SCOPE, "scope")
    if any(not isinstance(v, str) or not v.strip() or len(v) > 500 for v in scope.values()):
        raise ValueError("Scope requires bounded nonempty strings")
    for key in ("period_start", "period_end"):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", scope[key]):
            raise ValueError("Invalid ISO date")
        date.fromisoformat(scope[key])
    if scope["period_start"] > scope["period_end"]:
        raise ValueError("Reversed period")
    if not re.fullmatch(r"[A-Z]{3}", scope["currency"]) or scope["date_basis"] not in ("interaction_date", "conversion_date"):
        raise ValueError("Invalid currency or date basis")
    try:
        ZoneInfo(scope["timezone"])
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError("Unknown timezone; IANA timezone data required") from exc
    exact(quality, QUALITY, "quality")
    if any(type(v) is not bool for v in quality.values()):
        raise ValueError("Quality flags must be booleans")
    exact(m, COUNTS | {"spend", "purchase_value"}, "metrics")
    for key, value in m.items():
        if value is None:
            continue
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Metrics require finite numbers or null")
        if key != "purchase_value" and value < 0:
            raise ValueError("Negative count or spend")
        if key in COUNTS and type(value) is not int:
            raise ValueError("Session counts must be integers")
    for child, parent in (("intent_known_sessions", "sessions"), ("intent_matched_sessions", "intent_known_sessions"), ("qualified_sessions", "sessions"), ("purchase_sessions", "sessions")):
        if m[child] is not None and m[parent] is not None and m[child] > m[parent]:
            raise ValueError("Session subset exceeds parent")
    if m["sessions"] is not None and m["intent_matched_sessions"] is not None and m["intent_matched_sessions"] > m["sessions"]:
        raise ValueError("Matched sessions exceed sessions")
    rows = data["channels"]
    if rows is not None:
        if not isinstance(rows, list) or len(rows) > len(CHANNELS):
            raise ValueError("Invalid channels")
        seen = set()
        for row in rows:
            exact(row, {"channel", "sessions"}, "channel")
            if not isinstance(row["channel"], str) or row["channel"] not in CHANNELS or row["channel"] in seen:
                raise ValueError("Invalid or duplicate channel")
            seen.add(row["channel"])
            if type(row["sessions"]) is not int or row["sessions"] < 0:
                raise ValueError("Invalid channel session count")
        if m["sessions"] is not None and sum(r["sessions"] for r in rows) != m["sessions"]:
            raise ValueError("Channel total does not reconcile")
    blocks, warnings, ratios = [], [], {}
    for key, value in quality.items():
        if not value:
            blocks.append("UNCONFIRMED_" + key.upper())
    if scope["conversion_action"] != "purchase":
        blocks.append("NOT_PURCHASE_ONLY")

    def ratio(name, numerator, denominator, ready=True):
        if not ready:
            ratios[name] = None
            warnings.append(name + ":blocked_by_contract")
        elif numerator is None or denominator is None or denominator == 0:
            ratios[name] = None
            warnings.append(name + ":missing_or_zero_denominator")
        else:
            value = numerator / denominator
            if not math.isfinite(value):
                raise ValueError("Ratio overflow")
            ratios[name] = round(value, 6)

    cohorts = quality["same_cohort"] and quality["deduplicated"]
    ratio("intent_coverage", m["intent_known_sessions"], m["sessions"], cohorts)
    ratio("intent_match_rate", m["intent_matched_sessions"], m["intent_known_sessions"], cohorts)
    ratio("qualified_session_rate", m["qualified_sessions"], m["sessions"], cohorts)
    ratio("purchase_session_rate", m["purchase_sessions"], m["sessions"], cohorts and quality["mature"] and scope["conversion_action"] == "purchase")
    ratio("attributed_purchase_roas", m["purchase_value"], m["spend"], quality["mature"] and cohorts and scope["conversion_action"] == "purchase")
    shares = None
    if rows is not None and m["sessions"] and quality["exclusive_channels"] and cohorts:
        shares = {r["channel"]: round(r["sessions"] / m["sessions"], 6) for r in rows}
    else:
        warnings.append("channel_shares:missing_or_blocked")
    warnings.append("Quality flags and source provenance are caller assertions; business value and incrementality need separate evidence.")
    return {"schema_version": 1, "evidence_type": data["evidence_type"], "scope": scope, "status": "CONTRACT_BLOCKED" if blocks else "DESCRIPTIVE_ONLY", "source_verified": False, "business_verdict": "NOT_ASSESSED", "raw_metrics": m, "ratios": ratios, "channel_shares": shares, "blocks": blocks, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = audit(load(args.input))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 3 if result["blocks"] else 0
    except (ValueError, TypeError, OSError, OverflowError, RecursionError):
        print(json.dumps({"status": "INVALID_INPUT", "detail": "Check fields, types, period, units and totals against references/offline-audit.md", "source_verified": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
