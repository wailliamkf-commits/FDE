#!/usr/bin/env python3
"""Install a reviewed bundle into one project. Dry-run by default; never overwrites.

Do not run a downloaded installer until you have inspected its code. The manifest
is an integrity check, not a publisher signature or authorization mechanism.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

import argparse
import json
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from fde import CheckError, SKILL_NAMES, VERSION, file_hash, load_json, safe_path, verify_bundle


def build_plan(source: Path, project: Path, expected: str, selected: list[str]) -> dict:
    source = source.resolve(strict=True)
    project = project.resolve(strict=True)
    if not project.is_dir() or project == Path(project.anchor):
        raise CheckError("Choose an existing, non-root project directory")
    if project == source or project.is_relative_to(source):
        raise CheckError("Toolbox source and installation project must be separate")
    home = Path.home().resolve(strict=True)
    protected_roots = (home / ".agents", home / ".codex", home / ".config", home / ".ssh", home / ".local", home / "Library")
    personal_roots = {home, home.parent, home / "Desktop", home / "Documents", home / "Downloads"}
    if project in personal_roots or any(project == item or project.is_relative_to(item) for item in protected_roots):
        raise CheckError("Choose a dedicated project folder, not a user or global configuration root")
    temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
    system_roots = [Path(name).resolve(strict=True) for name in (
        "/System", "/Library", "/Applications", "/bin", "/sbin", "/usr", "/etc",
        "/var", "/opt", "/boot", "/dev", "/proc", "/sys",
    ) if Path(name).exists()]
    if not project.is_relative_to(temp_root) and any(project == item or project.is_relative_to(item) for item in system_roots):
        raise CheckError("System and application directories are not project installation roots")
    if not selected or len(set(selected)) != len(selected) or set(selected)-set(SKILL_NAMES):
        raise CheckError("Select unique known skills")
    if safe_path(project,".fde/STOP",exists=False).exists():
        raise CheckError("Project stop marker is present")
    files = verify_bundle(source,expected)
    vendor = f".fde/vendor/fde-delivery-toolbox/{VERSION}-{expected[:16]}"
    mappings = {f"{vendor}/{p}": p for p in files}
    mappings[f"{vendor}/MANIFEST.json"] = "MANIFEST.json"
    for name in selected:
        prefix = f"skills/{name}/"
        for p in files:
            if p.startswith(prefix):
                mappings[f".agents/skills/{name}/{p[len(prefix):]}"] = p
    lock_path = safe_path(project,".fde/toolbox-lock.json",exists=False)
    lock = None
    if lock_path.exists():
        lock = load_json(lock_path)
        if lock.get("manifest_sha256") != expected or sorted(lock.get("skills",[])) != sorted(selected):
            raise CheckError("Existing install differs; review a versioned migration, do not overwrite")
    for name in selected:
        folder = safe_path(project,f".agents/skills/{name}",exists=False)
        if folder.exists() and lock is None:
            raise CheckError("Existing skill has no matching ownership record")
        if folder.exists():
            for item in folder.rglob("*"):
                if item.is_symlink():
                    raise CheckError("Symlink inside an installed skill")
                if item.is_file() and item.relative_to(project).as_posix() not in mappings:
                    raise CheckError("Unexpected file in installed skill; refusing overwrite")
    copies = []
    for destination, original in sorted(mappings.items()):
        target = safe_path(project,destination,exists=False)
        src = safe_path(source,original)
        if target.exists():
            if file_hash(target) != file_hash(src):
                raise CheckError("Conflicting destination: " + destination)
        else:
            copies.append({"source":original,"destination":destination,"sha256":file_hash(src)})
    return {"schema_version":1,"mode":"DRY_RUN","source":str(source),"project":str(project),
            "version":VERSION,"manifest_sha256":expected,"skills":sorted(selected),
            "bundle_root":vendor,"copies":copies,"already_installed":lock is not None and not copies,
            "global_configuration_changed":False,"native_registration_verified":False}


def apply_plan(plan: dict) -> dict:
    source, project = Path(plan["source"]), Path(plan["project"])
    # Revalidate immediately before writes. Exclusive single-user install required.
    fresh = build_plan(source,project,plan["manifest_sha256"],plan["skills"])
    if fresh != plan:
        raise CheckError("Installation inputs changed; regenerate plan")
    if fresh["already_installed"]:
        return {**fresh,"mode":"ALREADY_INSTALLED","created_files":0}
    count = 0
    for entry in fresh["copies"]:
        src = safe_path(source,entry["source"])
        target = safe_path(project,entry["destination"],exists=False)
        content = src.read_bytes()
        import hashlib
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise CheckError("Source changed during installation")
        target.parent.mkdir(parents=True,exist_ok=True)
        safe_path(project,entry["destination"],exists=False)
        with target.open("xb") as stream:
            stream.write(content)
        count += 1
    lock = {"schema_version":1,"version":VERSION,"manifest_sha256":fresh["manifest_sha256"],
            "bundle_root":fresh["bundle_root"],"skills":fresh["skills"],
            "installed_at":datetime.now(timezone.utc).isoformat(),
            "source_commit":None,"native_registration_verified":False,
            "note":"Files copied only; verify skill discovery in the actual host. No production authority."}
    lock_path = safe_path(project,".fde/toolbox-lock.json",exists=False)
    if not lock_path.exists():
        lock_path.parent.mkdir(parents=True,exist_ok=True)
        with lock_path.open("x",encoding="utf-8") as stream:
            json.dump(lock,stream,ensure_ascii=False,indent=2)
            stream.write("\n")
        count += 1
    return {**fresh,"mode":"INSTALLED_FILES_ONLY","created_files":count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project",type=Path,required=True)
    parser.add_argument("--expected-manifest-sha256",required=True)
    parser.add_argument("--skills",nargs="+",choices=SKILL_NAMES,required=True)
    parser.add_argument("--apply",action="store_true")
    args = parser.parse_args()
    try:
        plan = build_plan(args.source,args.project,args.expected_manifest_sha256,args.skills)
        output = apply_plan(plan) if args.apply else plan
        print(json.dumps(output,ensure_ascii=False,indent=2))
        return 0
    except (CheckError,OSError,ValueError) as exc:
        print(json.dumps({"error":str(exc),"installed":False,
                          "note":"Partial copies may remain after interruption; inspect, do not delete blindly."},ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
