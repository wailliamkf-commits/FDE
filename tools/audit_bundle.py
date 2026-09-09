#!/usr/bin/env python3
"""Heuristic scan of the exact manifest-verified bundle; never prints matching secrets.

This is not a complete secret detector, malware review, or copyright audit.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

import argparse
import json
from pathlib import Path
import re
from fde import CheckError, safe_path, sensitive_read_path, verify_bundle

PATTERNS = {
    "private_key_header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github_token_shape": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "github_fine_grained_shape": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
    "shopify_token_shape": re.compile(r"\bshp(?:at|ua|ss|ca)_[a-fA-F0-9]{25,}\b"),
    "openai_token_shape": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{35,}\b"),
    "aws_access_key_shape": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
}


def audit(root: Path, expected: str | None = None) -> dict:
    files = verify_bundle(root,expected)
    findings = []
    names = list(files) + ["MANIFEST.json"]
    for name in names:
        parts = name.lower().split("/")
        if sensitive_read_path(name) or any(p in {"private","customer-data","logs",".fde"} for p in parts):
            findings.append({"path":name,"rule":"sensitive_filename"})
        data = safe_path(root,name).read_text(encoding="utf-8")
        for rule, pattern in PATTERNS.items():
            if pattern.search(data):
                findings.append({"path":name,"rule":rule})
    return {"heuristic_scan":"FLAGGED" if findings else "NO_MATCHES",
            "findings":findings,"scanned_files":len(names),
            "complete_security_audit":False,
            "note":"Only listed token shapes and filenames are checked; manually review source, customer data, dependencies and rights."}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--expected-manifest-sha256")
    args=parser.parse_args()
    try:
        result=audit(args.root,args.expected_manifest_sha256)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if result["findings"] else 0
    except (OSError,ValueError,CheckError) as exc:
        print(json.dumps({"error":str(exc)})); return 2
if __name__=="__main__":
    raise SystemExit(main())
