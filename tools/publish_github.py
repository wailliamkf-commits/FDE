#!/usr/bin/env python3
"""Create ONE NEW PRIVATE personal repository, using an already authenticated gh.

Default is offline planning. --apply performs the specifically requested GitHub
publication, not deployment to a client or permission escalation. Existing repos
are never overwritten. No tokens are read, printed, requested or stored by this
script. Authenticate gh interactively through the host beforehand.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlparse
from fde import CheckError, VERSION, file_hash, safe_git_environment, verify_bundle

GITHUB_HOST = "github.com"


def safe_publisher_environment() -> dict[str, str]:
    """Pin gh to the reviewed public GitHub destination and disable prompting."""
    environment = safe_git_environment()
    for name in ("GH_HOST", "GH_REPO", "GH_DEBUG", "GH_FORCE_TTY", "GH_PAGER", "GH_EDITOR", "GH_BROWSER"):
        environment.pop(name, None)
    environment["GH_HOST"] = GITHUB_HOST
    environment["GH_PROMPT_DISABLED"] = "1"
    return environment


def checked(command: list[str], root: Path) -> str:
    proc = subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=180,env=safe_publisher_environment())
    if proc.returncode:
        # Avoid copying command output that might contain credentials into chats.
        raise CheckError("Command failed; inspect the local CLI safely: " + Path(command[0]).name)
    return proc.stdout.strip()


def validate_destination(owner: str, repository: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}",owner):
        raise CheckError("Invalid owner")
    if repository != "fde-delivery-toolbox":
        raise CheckError("This initial publisher is restricted to the new fde-delivery-toolbox repository")


def validate_remote_url(value: str, owner: str, repository: str) -> None:
    expected_path = f"{owner}/{repository}".casefold()
    candidate = value.strip()
    if candidate.startswith("git@github.com:"):
        actual_path = candidate.removeprefix("git@github.com:")
    else:
        parsed = urlparse(candidate)
        if parsed.hostname != GITHUB_HOST or parsed.scheme not in {"https", "ssh"}:
            raise CheckError("Created Git remote is not the reviewed github.com destination")
        actual_path = parsed.path.lstrip("/")
    if actual_path.removesuffix(".git").rstrip("/").casefold() != expected_path:
        raise CheckError("Created Git remote does not match the requested repository")


def validate_git_remote(git: str, root: Path, owner: str, repository: str) -> None:
    """Validate both fetch and effective push targets before any code leaves the host."""
    for command in ([git,"remote","get-url","--all","origin"],
                    [git,"remote","get-url","--all","--push","origin"]):
        values = checked(command,root).splitlines()
        if not values:
            raise CheckError("Created Git remote has no usable destination")
        for value in values:
            validate_remote_url(value,owner,repository)


def validate_remote_metadata(metadata: dict, owner: str, repository: str) -> None:
    expected = f"{owner}/{repository}".casefold()
    if not isinstance(metadata.get("nameWithOwner"), str) or metadata["nameWithOwner"].casefold() != expected:
        raise CheckError("Remote read-back repository identity mismatch")
    if metadata.get("isPrivate") is not True:
        raise CheckError("Remote read-back visibility mismatch")
    url = metadata.get("url")
    if not isinstance(url, str):
        raise CheckError("Remote read-back URL missing")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != GITHUB_HOST or parsed.path.strip("/").casefold() != expected:
        raise CheckError("Remote read-back URL mismatch")


def publish(root: Path, owner: str, repository: str, manifest_sha: str, *, apply: bool=False) -> dict:
    validate_destination(owner,repository)
    root = root.resolve(strict=True)
    files = verify_bundle(root,manifest_sha)
    from audit_bundle import audit
    if audit(root,manifest_sha)["findings"]:
        raise CheckError("Heuristic audit has unresolved findings")
    plan = {"status":"NOT_UPLOADED","destination":f"{owner}/{repository}","visibility":"private",
            "file_count":len(files)+1,"manifest_sha256":manifest_sha,
            "actions":["verify authenticated owner","reject existing destination","initialize isolated source Git repository",
                       "commit only manifest-listed files","create new private repository and push","read back visibility and commit"],
            "client_project_changes":False,"plugin_installed":False}
    if not apply:
        return plan
    git, gh = shutil.which("git"), shutil.which("gh")
    if not git or not gh:
        raise CheckError("git and authenticated gh are required; installation is a separate approved operation")
    safe_environment = safe_publisher_environment()
    if (root/".git").exists() or (root/".git").is_symlink():
        raise CheckError("Existing Git metadata: do not overwrite or retry blindly; use the recovery instructions")
    parent = subprocess.run([git,"-C",str(root.parent),"rev-parse","--show-toplevel"],capture_output=True,text=True,timeout=15,env=safe_environment)
    if parent.returncode == 0:
        raise CheckError("Bundle is inside another Git repository; choose a separate staging directory")
    checked([gh,"auth","status","--hostname",GITHUB_HOST],root)
    user = json.loads(checked([gh,"api","--hostname",GITHUB_HOST,"user"],root))
    if user.get("login","").lower() != owner.lower() or type(user.get("id")) is not int:
        raise CheckError("Authenticated account does not match the requested personal repository owner")
    endpoint = f"repos/{owner}/{repository}"
    existing = subprocess.run([gh,"api","--hostname",GITHUB_HOST,endpoint,"--silent"],cwd=root,capture_output=True,text=True,timeout=45,env=safe_environment)
    if existing.returncode == 0:
        raise CheckError("Destination already exists; no overwrite. Inspect it and use a reviewed branch/PR")
    if "404" not in existing.stderr:
        raise CheckError("Cannot establish destination availability; resolve connection/permission first")
    login = user["login"]
    email = f"{user['id']}+{login}@users.noreply.github.com"
    # Per-command identity, no global Git configuration, no hooks from host.
    prefix = [git,"-c","core.hooksPath=" + os.devnull,"-c","core.fsmonitor=false",
              "-c","diff.external=","-c","init.templateDir=",
              "-c","user.name="+login,"-c","user.email="+email,"-c","commit.gpgsign=false"]
    checked(prefix+["init","--initial-branch=main"],root)
    names = sorted(files)+["MANIFEST.json"]
    for start in range(0,len(names),50):
        checked(prefix+["add","--"]+names[start:start+50],root)
    staged = checked([git,"diff","--cached","--name-only"],root).splitlines()
    if set(staged) != set(names):
        raise CheckError("Staged files do not equal the reviewed manifest")
    checked(prefix+["commit","-m",f"Initial reviewed FDE toolbox v{VERSION}"],root)
    commit = checked([git,"rev-parse","HEAD"],root)
    checked([gh,"repo","create",f"{owner}/{repository}","--private","--source",str(root),"--remote","origin"],root)
    validate_git_remote(git,root,owner,repository)
    checked(prefix+["push","-u","origin","main"],root)
    metadata = json.loads(checked([gh,"repo","view",f"{GITHUB_HOST}/{owner}/{repository}","--json","nameWithOwner,isPrivate,url"],root))
    validate_remote_metadata(metadata,owner,repository)
    remote_sha = checked([gh,"api","--hostname",GITHUB_HOST,endpoint+"/commits/main","--jq",".sha"],root)
    if remote_sha != commit:
        raise CheckError("Remote read-back commit mismatch; stop and inspect, do not redeploy")
    return {**plan,"status":"UPLOADED_AND_READ_BACK","repository_url":metadata["url"],
            "commit":commit,"remote_commit":remote_sha,"plugin_installed":False}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--owner",required=True)
    parser.add_argument("--repo",default="fde-delivery-toolbox")
    parser.add_argument("--expected-manifest-sha256",required=True)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    try:
        print(json.dumps(publish(args.root,args.owner,args.repo,args.expected_manifest_sha256,apply=args.apply),ensure_ascii=False,indent=2))
        return 0
    except (CheckError,OSError,ValueError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status":"BLOCKED_OR_PARTIAL","error":str(exc),
                          "note":"Check local git and remote state before retry; never force-push or recreate blindly."},ensure_ascii=False))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
