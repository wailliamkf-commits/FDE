#!/usr/bin/env python3
"""Offline delivery checks. Not a sandbox, credential broker, or production executor.

Python 3.10+; standard library only. No network, credential loading or deletion.
"""
from __future__ import annotations

import sys

# Bundle verification is intentionally exact.  Keep the toolbox from creating
# unlisted bytecode inside its own reviewed tree while it imports helper modules.
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from typing import Any

VERSION = "0.1.5"
MAX_JSON_BYTES = 2_000_000
MAX_HASH_BYTES = 100_000_000
SKILL_NAMES = (
    "fde-discovery", "fde-connector-preflight", "fde-delivery",
    "fde-eval-release", "fde-handoff-cleanup", "fde-brand-growth",
    "google-ads-diagnostics", "meta-ads-diagnostics",
)
RISK_LEVELS = {"READ", "LOCAL_WRITE", "STAGING_WRITE", "PRODUCTION_WRITE", "HIGH_IMPACT"}
REMOTE_RISKS = {"STAGING_WRITE", "PRODUCTION_WRITE", "HIGH_IMPACT"}
ACTIONS = {
    "local.read": "READ", "remote.read": "READ", "local.draft": "LOCAL_WRITE",
    "staging.change": "STAGING_WRITE", "production.change": "PRODUCTION_WRITE",
    "price.change": "HIGH_IMPACT", "inventory.change": "HIGH_IMPACT",
    "account.change": "HIGH_IMPACT", "advertising.spend": "HIGH_IMPACT",
    "external.send": "HIGH_IMPACT", "file.delete": "HIGH_IMPACT",
}

class CheckError(ValueError):
    """A failed input, scope, integrity, or safety check."""


def _reject_constant(value: str) -> None:
    raise CheckError("Non-finite JSON number")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise CheckError("Duplicate JSON key")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise CheckError("JSON input must be a bounded, regular, non-symlink file")
    data = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant,
                      object_pairs_hook=_unique_object)
    if not isinstance(data, dict):
        raise CheckError("Expected a JSON object")
    return data


def digest(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                     allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise CheckError("A nonempty bounded relative path is required")
    if "\\" in value or ":" in value or any(ord(c) < 32 for c in value):
        raise CheckError("Unsafe path characters")
    parts = value.split("/")
    if value.startswith("/") or any(p in {"", ".", ".."} for p in parts):
        raise CheckError("Absolute, empty or traversal path component")
    if any(p.endswith((" ", ".")) for p in parts):
        raise CheckError("Ambiguous cross-platform filename")
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1,10)} | {f"LPT{i}" for i in range(1,10)}
    if any(p.split(".")[0].upper() in reserved for p in parts):
        raise CheckError("Reserved cross-platform filename")
    return value


def safe_path(root: Path, relative: str, *, exists: bool = True) -> Path:
    """Resolve only inside an already chosen project root, rejecting symlink components.

    Not race-proof against a hostile concurrent local process; use a sandbox and
    exclusive task ownership. Checks here are validation, not OS authorization.
    """
    relative_path(relative)
    root = root.resolve(strict=True)
    path = root
    for part in PurePosixPath(relative).parts:
        path = path / part
        if path.is_symlink():
            raise CheckError("Symlink path component is not allowed")
        if path.exists() and path != root / relative and not path.is_dir():
            raise CheckError("Non-directory parent")
    if exists and not path.exists():
        raise CheckError("Required file or directory does not exist")
    resolved = path.resolve(strict=exists)
    if not resolved.is_relative_to(root):
        raise CheckError("Path escapes root")
    return path


def file_hash(path: Path) -> str:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_HASH_BYTES:
        raise CheckError("Expected a bounded regular file")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise CheckError("Timestamp must be an ISO-8601 string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CheckError("Invalid timestamp") from exc
    if result.tzinfo is None:
        raise CheckError("Timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def validate_task(task: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"schema_version", "task_id", "project_id", "owner", "objective", "non_goals",
                "risk", "allowed_actions", "allowed_paths", "allowed_targets", "inputs",
                "acceptance", "budget", "rollback", "status"}
    missing = required - task.keys()
    if missing:
        errors.append("Missing fields: " + ", ".join(sorted(missing)))
    if task.get("schema_version") != 1:
        errors.append("Unsupported task schema version")
    for field in ("task_id", "project_id", "owner"):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", str(task.get(field, ""))):
            errors.append("Invalid " + field)
    for field in ("objective", "rollback"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            errors.append("Nonempty " + field + " required")
    if task.get("risk") not in RISK_LEVELS:
        errors.append("Unknown risk classification")
    if task.get("status") not in {"READY", "RUNNING", "REVIEW", "BLOCKED", "FAILED", "VERIFIED", "CLOSED", "CANCELLED"}:
        errors.append("Unknown task status")
    for field in ("non_goals", "allowed_actions", "allowed_paths", "allowed_targets", "inputs", "acceptance"):
        if not isinstance(task.get(field), list):
            errors.append(field + " must be an array")
    actions = task.get("allowed_actions", [])
    if isinstance(actions, list):
        if not actions:
            errors.append("Explicit allowed_actions required")
        for action in actions:
            if not isinstance(action, str) or action not in ACTIONS:
                errors.append("Unknown action")
            elif ACTIONS[action] not in {"READ", task.get("risk")}:
                errors.append("Action/risk mismatch")
    for path in task.get("allowed_paths", []) if isinstance(task.get("allowed_paths"), list) else []:
        try:
            relative_path(path)
        except CheckError as exc:
            errors.append(str(exc))
    targets = task.get("allowed_targets", [])
    if isinstance(targets, list) and any(not isinstance(t,str) or not t or "*" in t for t in targets):
        errors.append("Targets must be exact non-wildcard identifiers")
    inputs = task.get("inputs", [])
    if isinstance(inputs, list):
        for item in inputs:
            if not isinstance(item, dict):
                errors.append("Invalid input record")
                continue
            try:
                path = relative_path(item.get("path"))
                if sensitive_read_path(path):
                    errors.append("Sensitive input path is not allowed")
            except CheckError:
                errors.append("Invalid input path")
            if not re.fullmatch(r"[a-f0-9]{64}", str(item.get("sha256", ""))):
                errors.append("Input SHA-256 required")
    accept = task.get("acceptance", [])
    if isinstance(accept, list):
        if not accept:
            errors.append("Acceptance cannot be empty")
        seen = set()
        for item in accept:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item.get("id"):
                errors.append("Acceptance id required")
                continue
            if item["id"] in seen:
                errors.append("Duplicate acceptance id")
            seen.add(item["id"])
            if not isinstance(item.get("criterion"), str) or not item.get("criterion", "").strip():
                errors.append("Acceptance criterion required")
    budget = task.get("budget")
    if not isinstance(budget, dict):
        errors.append("Budget must be an object")
    else:
        for key, maximum in (("max_attempts", 2), ("max_minutes", 240)):
            value = budget.get(key)
            if type(value) is not int or not 1 <= value <= maximum:
                errors.append("Invalid " + key)
        cost = budget.get("max_external_cost_usd")
        if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
            errors.append("Invalid external budget")
    return errors


def protected_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    names = {p.lower() for p in parts}
    if names & {".git", ".ssh", ".codex", ".codex-plugin", ".github", "node_modules"}:
        return True
    if ".agents" in names or "private" in names or "secrets" in names or path.lower().startswith(".fde/vendor/"):
        return True
    base = parts[-1].lower()
    return (base in {"agents.md", "security.md", "policy.json", "toolbox-lock.json", "stop"}
            or sensitive_credential_path(path))


def sensitive_credential_path(path: str) -> bool:
    """Conservative filename guard, not a content scanner or OS permission boundary."""
    parts = tuple(part.lower() for part in PurePosixPath(path).parts)
    names = set(parts)
    base = parts[-1]
    sensitive_names = {
        ".netrc", ".npmrc", ".pypirc", ".git-credentials", "credentials.json",
        "credentials.toml", "credentials.yaml", "credentials.yml", "service-account.json",
        "auth.json", "token.json", "tokens.json", "secrets.toml", "secrets.json",
        "secrets.yaml", "secrets.yml", ".vault-token", "cookies", "cookies.sqlite",
        "cookies.db", "cookies.binarycookies", "login data", "web data", "key4.db", "logins.json",
        "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    }
    sensitive_dirs = {
        ".ssh", ".codex", ".aws", ".azure", ".docker", ".kube", ".gnupg",
        "secrets", "credentials",
    }
    sensitive_path_pairs = any(
        (parts[index] == ".config" and parts[index + 1] in {"gh", "gcloud", "openai"})
        or (parts[index] == "library" and parts[index + 1] in {"keychains", "cookies"})
        for index in range(len(parts) - 1)
    )
    named_json_secret = (
        (base.startswith("client_secret") or base.startswith("service_account"))
        and base.endswith(".json")
    )
    return (bool(names & sensitive_dirs) or sensitive_path_pairs or named_json_secret
            or base in sensitive_names or base.startswith(".env")
            or base.endswith((".pem", ".key", ".p8", ".p12", ".pfx", ".jks", ".kdbx", ".keystore", ".keychain", ".keychain-db")))


def sensitive_read_path(path: str) -> bool:
    """Reject metadata and credential paths before any content read or hashing."""
    names = {part.lower() for part in PurePosixPath(path).parts}
    return ".git" in names or sensitive_credential_path(path)


def within(relative: str, allowed: list[str]) -> bool:
    return any(relative == a or relative.startswith(a.rstrip("/") + "/") for a in allowed)


def assess_action(task: dict[str, Any], request: dict[str, Any], root: Path) -> dict[str, Any]:
    """Fail-closed advisory preflight. Never executes any requested action."""
    def result(verdict: str, reason: str) -> dict[str, Any]:
        return {"verdict": verdict, "reason": reason, "executed": False,
                "authorization_granted": False, "task_sha256": digest(task)}
    errors = validate_task(task)
    if errors:
        return result("DENY", "Invalid task: " + "; ".join(errors))
    if safe_path(root, ".fde/STOP", exists=False).exists():
        return result("DENY", "Project stop marker is present")
    if task["status"] not in {"READY", "RUNNING"}:
        return result("DENY", "Task is not active")
    if request.get("task_sha256") != digest(task):
        return result("DENY", "Task digest mismatch")
    action = request.get("action")
    if action not in task["allowed_actions"] or action not in ACTIONS:
        return result("DENY", "Action not allowlisted")
    for item in task["inputs"]:
        try:
            input_path = relative_path(item["path"])
            if sensitive_read_path(input_path):
                return result("DENY", "Sensitive input path is not allowed")
            if file_hash(safe_path(root,input_path)) != item["sha256"]:
                return result("DENY", "Input changed; refresh task and approval")
        except (OSError, CheckError):
            return result("DENY", "Input unavailable")
    if ACTIONS[action] in REMOTE_RISKS:
        return result("REMOTE_EXECUTOR_REQUIRED", "This release has no remote-write or deletion executor; a JSON approval is not authority")
    if action == "remote.read":
        if request.get("target") not in task["allowed_targets"]:
            return result("DENY", "Target not allowlisted")
        return result("PREFLIGHT_ONLY", "Use the host's separately authenticated, read-only connector")
    path = request.get("path")
    try:
        relative_path(path)
        safe_path(root, path, exists=(action == "local.read"))
    except (CheckError, OSError):
        return result("DENY", "Unsafe or missing path")
    if not within(path, task["allowed_paths"]):
        return result("DENY", "Path outside task scope")
    if action == "local.draft" and protected_path(path):
        return result("DENY", "Protected path requires a separate reviewed maintenance operation")
    if action == "local.read":
        if sensitive_read_path(path):
            return result("DENY", "Sensitive credential or system path")
    return result("PREFLIGHT_ONLY", "Scope checks passed; host permission still required, no command executed")


def verify_evidence(task: dict[str, Any], record: dict[str, Any], root: Path) -> dict[str, Any]:
    errors = validate_task(task)
    if record.get("task_id") != task.get("task_id") or record.get("task_sha256") != digest(task):
        errors.append("Result does not match frozen task")
    checks = record.get("checks", [])
    if not isinstance(checks, list):
        checks = []
        errors.append("Checks must be an array")
    expected = {i["id"] for i in task.get("acceptance", []) if isinstance(i,dict) and "id" in i}
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check,dict):
            errors.append("Invalid check record")
            continue
        identity = check.get("id")
        if not isinstance(identity,str) or identity not in expected or identity in seen:
            errors.append("Unexpected or duplicate check")
        else:
            seen.add(identity)
        if check.get("status") != "PASS":
            errors.append("Non-passing check")
        items = check.get("evidence", [])
        if not isinstance(items,list) or not items:
            errors.append("Missing evidence")
            continue
        for item in items:
            try:
                if not isinstance(item,dict):
                    raise CheckError("Invalid evidence record")
                path = relative_path(item["path"])
                if sensitive_read_path(path):
                    raise CheckError("Sensitive evidence path")
                if file_hash(safe_path(root,path)) != item.get("sha256"):
                    errors.append("Evidence digest mismatch")
            except (KeyError, TypeError, OSError, CheckError):
                errors.append("Unsafe or missing evidence file")
    if seen != expected:
        errors.append("Acceptance coverage mismatch")
    for item in task.get("inputs", []):
        try:
            path = relative_path(item["path"])
            if sensitive_read_path(path):
                raise CheckError("Sensitive input path")
            if file_hash(safe_path(root,path)) != item["sha256"]:
                errors.append("Task input changed")
        except (KeyError, TypeError, OSError, CheckError):
            errors.append("Task input unavailable")
    return {"verdict": "INVALID" if errors else "EVIDENCE_FILES_VERIFIED", "errors": errors,
            "business_claims_verified": False, "release_authorized": False,
            "note": "File hashes and coverage only. Independently inspect tests, claims, actual environment and approval."}


def verify_bundle(root: Path, expected_manifest: str | None = None) -> dict[str, str]:
    path = safe_path(root, "MANIFEST.json")
    if expected_manifest is not None and file_hash(path) != expected_manifest:
        raise CheckError("Manifest digest differs from the reviewed release")
    manifest = load_json(path)
    if manifest.get("schema_version") != 1 or manifest.get("name") != "fde-delivery-toolbox" or manifest.get("version") != VERSION:
        raise CheckError("Unexpected bundle identity or schema")
    files = manifest.get("files")
    if not isinstance(files, dict) or not 1 <= len(files) <= 250:
        raise CheckError("Invalid bundle file map")
    seen = set()
    total_size = 0
    for name, sha in files.items():
        relative_path(name)
        if name == "MANIFEST.json" or name.lower() in seen or name.startswith(".git/"):
            raise CheckError("Invalid, duplicate or reserved manifest path")
        seen.add(name.lower())
        if not isinstance(sha,str) or not re.fullmatch(r"[a-f0-9]{64}",sha):
            raise CheckError("Invalid digest in manifest")
        item = safe_path(root,name)
        total_size += item.stat().st_size
        if total_size > 20_000_000 or file_hash(item) != sha:
            raise CheckError("Bundle too large or file digest mismatch: " + name)
    actual = set()
    for item in root.rglob("*"):
        relative = item.relative_to(root)
        if relative.parts[0] == ".git":
            if len(relative.parts) == 1 and item.is_symlink():
                raise CheckError("Unsafe repository metadata path")
            continue
        if ".git" in relative.parts:
            raise CheckError("Nested Git metadata is not part of the reviewed bundle")
        if item.is_symlink():
            raise CheckError("Unlisted or unsafe bundle member: " + relative.as_posix())
        if item.is_file():
            actual.add(relative.as_posix())
        elif not item.is_dir():
            raise CheckError("Unsupported bundle member type: " + relative.as_posix())
    expected = set(files) | {"MANIFEST.json"}
    if actual != expected:
        raise CheckError("Bundle tree differs from manifest")
    critical = {"tools/fde.py", "tools/install.py", "tools/publish_github.py", "tools/audit_bundle.py", "tools/smoke_demo.py", "SECURITY.md", ".codex-plugin/plugin.json"}
    critical |= {f"skills/{name}/SKILL.md" for name in SKILL_NAMES}
    if not critical.issubset(files):
        raise CheckError("Required bundle members are missing")
    return files


def safe_git_environment() -> dict[str, str]:
    """Keep Git discovery inside explicit -C roots and suppress env-selected helpers."""
    unsafe = {
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE",
        "GIT_EXTERNAL_DIFF", "GIT_SSH", "GIT_SSH_COMMAND", "GIT_ASKPASS",
        "GIT_EXEC_PATH", "GIT_CEILING_DIRECTORIES", "GIT_TEMPLATE_DIR",
    }
    environment = {
        key:value for key,value in os.environ.items()
        if key not in unsafe and not key.startswith("GIT_CONFIG_") and not key.startswith("GIT_TRACE")
    }
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def git_tracked(root: Path, path: str) -> bool | None:
    git = shutil.which("git")
    if not git:
        return None
    try:
        git_command = [git,"-c","core.fsmonitor=false","-c","core.hooksPath="+os.devnull,
                       "-c","diff.external=","-c","core.untrackedCache=false"]
        git_environment = safe_git_environment()
        root = root.resolve(strict=True)
        candidate = safe_path(root,path)
        probe_from = candidate.parent
        checked: set[Path] = set()
        found_repository = False
        while True:
            probe = subprocess.run(git_command+["-C",str(probe_from),"rev-parse","--show-toplevel"],
                                   capture_output=True, text=True, timeout=10, env=git_environment)
            if probe.returncode != 0:
                break
            repository = Path(probe.stdout.strip()).resolve(strict=True)
            if repository in checked:
                break
            checked.add(repository)
            found_repository = True
            try:
                repository_path = candidate.relative_to(repository).as_posix()
            except ValueError:
                return None
            tracked = subprocess.run(git_command+["-C",str(repository),"ls-files","--error-unmatch","--",repository_path],
                                     capture_output=True, text=True, timeout=10, env=git_environment)
            if tracked.returncode == 0:
                return True
            if tracked.returncode != 1:
                return None
            if repository.parent == repository:
                break
            probe_from = repository.parent
        return False if found_repository else None
    except (OSError, CheckError, UnicodeError, subprocess.TimeoutExpired):
        return None


def cleanup_plan(root: Path, manifest: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if manifest.get("schema_version") != 1:
        raise CheckError("Unsupported cleanup schema")
    if not isinstance(manifest.get("items"),list) or len(manifest["items"]) > 500:
        raise CheckError("Invalid bounded cleanup list")
    created = timestamp(manifest.get("generated_at"))
    if not 0 <= (now-created).total_seconds() <= 3600:
        raise CheckError("Cleanup manifest is stale or future-dated")
    base = relative_path(manifest.get("temp_root"))
    if base not in {".fde/tmp", "00_reports/agent_control/tmp"}:
        raise CheckError("Only a supported dedicated temp namespace is permitted")
    safe_path(root,base)
    results = []
    seen = set()
    for item in manifest["items"]:
        reasons = []
        name = item.get("path") if isinstance(item,dict) else None
        if not isinstance(item,dict):
            results.append({"path":None,"candidate":False,"reasons":["Invalid record"]})
            continue
        try:
            relative_path(name)
            if name in seen:
                raise CheckError("Duplicate candidate")
            seen.add(name)
            if not name.startswith(base+"/") or protected_path(name):
                raise CheckError("Outside dedicated temp namespace or protected path")
            path = safe_path(root,name)
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise CheckError("Only singly-linked regular files are candidates")
            if file_hash(path) != item.get("sha256"):
                reasons.append("File changed")
            if item.get("task_status") != "CLOSED":
                reasons.append("Task is not closed")
            if item.get("classification") != "rebuildable-temp":
                reasons.append("Not explicitly rebuildable temp")
            for flag, wanted in (("referenced",False),("active_writer",False),("legal_hold",False),("durable_outputs_verified",True)):
                if item.get(flag) is not wanted:
                    reasons.append("Unproven " + flag)
            closed = timestamp(item.get("closed_at"))
            if (now-closed).total_seconds() < 24*3600 or now.timestamp()-info.st_mtime < 24*3600:
                reasons.append("24-hour retention not met")
            evidence = item.get("durable_evidence")
            if not isinstance(evidence,dict):
                reasons.append("Durable evidence missing")
            else:
                evidence_path = relative_path(evidence.get("path"))
                if (evidence_path.startswith(base+"/") or sensitive_read_path(evidence_path)
                        or file_hash(safe_path(root,evidence_path)) != evidence.get("sha256")):
                    reasons.append("Durable evidence invalid")
            tracked = git_tracked(root,name)
            if tracked is not False:
                reasons.append("Git tracked or tracking status unverified")
        except (OSError, CheckError, TypeError):
            reasons.append("Unsafe path, invalid metadata, or missing evidence")
        results.append({"path":name,"candidate":not reasons,"reasons":reasons})
    return {"mode":"DRY_RUN_ONLY","moved":0,"deleted":0,"items":results,
            "warning":"References and business ownership are declared, not globally discoverable. Recheck before approved quarantine. No cleanup executor is included."}


def doctor() -> dict[str, Any]:
    return {"toolbox_version":VERSION,"python":sys.version.split()[0],
            "git_binary_present":bool(shutil.which("git")),
            "gh_binary_present":bool(shutil.which("gh")),
            "codex_binary_present":bool(shutil.which("codex")),
            "connector_auth":"NOT_PROBED","network":"NOT_PROBED",
            "model_effective":"UNKNOWN","native_skill_registration":"NOT_PROBED",
            "production_executor":"NOT_IMPLEMENTED","secrets_read":False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("validate-task"); p.add_argument("task",type=Path)
    p = sub.add_parser("check-action"); p.add_argument("task",type=Path); p.add_argument("request",type=Path); p.add_argument("--project",type=Path,required=True)
    p = sub.add_parser("verify-evidence"); p.add_argument("task",type=Path); p.add_argument("result",type=Path); p.add_argument("--project",type=Path,required=True)
    p = sub.add_parser("cleanup-plan"); p.add_argument("manifest",type=Path); p.add_argument("--project",type=Path,required=True)
    p = sub.add_parser("verify-bundle"); p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]); p.add_argument("--expected-manifest-sha256")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            out = doctor()
        elif args.command == "validate-task":
            task = load_json(args.task); errors = validate_task(task)
            out = {"valid":not errors,"errors":errors,"task_sha256":digest(task)}
        elif args.command == "check-action":
            out = assess_action(load_json(args.task),load_json(args.request),args.project)
        elif args.command == "verify-evidence":
            out = verify_evidence(load_json(args.task),load_json(args.result),args.project)
        elif args.command == "cleanup-plan":
            out = cleanup_plan(args.project,load_json(args.manifest))
        else:
            files = verify_bundle(args.root,args.expected_manifest_sha256)
            out = {"integrity":"VERIFIED","file_count":len(files),"publisher_identity_verified":False}
        print(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False))
        return 2 if out.get("valid") is False or out.get("verdict") in {"DENY","INVALID","REMOTE_EXECUTOR_REQUIRED"} else 0
    except (CheckError,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"error":str(exc),"executed":False},ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
