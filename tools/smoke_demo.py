#!/usr/bin/env python3
"""Offline synthetic smoke test. Temporary demo fixtures only, no customer files."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

import json
from pathlib import Path
import tempfile
from fde import assess_action, digest, file_hash, load_json, verify_evidence

def main() -> int:
    bundle=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="fde-synthetic-smoke-") as temp:
        root=Path(temp)
        (root/"inputs").mkdir(); (root/"outputs").mkdir()
        (root/"inputs/source.txt").write_text("SYNTHETIC DEMO: not product facts.\n",encoding="utf-8")
        task=load_json(bundle/"templates/task.example.json")
        task["inputs"]=[{"path":"inputs/source.txt","sha256":file_hash(root/"inputs/source.txt")}]
        request={"action":"local.draft","path":"outputs/draft.txt","task_sha256":digest(task)}
        preflight=assess_action(task,request,root)
        if preflight["verdict"] != "PREFLIGHT_ONLY":
            raise RuntimeError("Unexpected preflight rejection")
        # This fixture write is inside this script's freshly-created temporary demo.
        (root/"outputs/draft.txt").write_text("SYNTHETIC DEMO. No product claim. No remote changes.\n",encoding="utf-8")
        result={"task_id":task["task_id"],"task_sha256":digest(task),"checks":[{"id":"AC-1","status":"PASS","evidence":[{"path":"outputs/draft.txt","sha256":file_hash(root/"outputs/draft.txt")}]}]}
        evidence=verify_evidence(task,result,root)
        if evidence["verdict"] != "EVIDENCE_FILES_VERIFIED":
            raise RuntimeError("Unexpected evidence failure")
        print(json.dumps({"synthetic_demo":"PASS","scope_preflight":preflight["verdict"],
                          "evidence":evidence["verdict"],"customer_data_used":False,
                          "external_calls":0,"production_changed":False,
                          "native_plugin_verified":False,
                          "temporary_demo_fixture_cleanup":"Only the directory created by this demo is removed."},indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
