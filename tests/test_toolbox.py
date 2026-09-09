"""Offline boundary tests; do not exercise GitHub writes or any production system."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

# Normal documented test runs must not invalidate the exact bundle by creating
# Python cache files inside the reviewed repository.
sys.dont_write_bytecode = True
sys.pycache_prefix = f"{sys.base_prefix}/.fde-disabled-bytecode-cache-{id(sys)}"

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import fde
import install
import publish_github
import audit_bundle


def example():
    return fde.load_json(ROOT/"templates/task.example.json")

class TaskValidationTests(unittest.TestCase):
    def test_valid_example(self): self.assertEqual(fde.validate_task(example()),[])
    def test_missing_objective(self):
        task=example(); del task["objective"]; self.assertTrue(fde.validate_task(task))
    def test_unknown_risk(self):
        task=example(); task["risk"]="ALL_ALLOWED"; self.assertTrue(fde.validate_task(task))
    def test_unknown_action(self):
        task=example(); task["allowed_actions"].append("shell.anything"); self.assertTrue(fde.validate_task(task))
    def test_risk_mismatch(self):
        task=example(); task["allowed_actions"].append("price.change"); self.assertTrue(fde.validate_task(task))
    def test_empty_acceptance(self):
        task=example(); task["acceptance"]=[]; self.assertTrue(fde.validate_task(task))
    def test_duplicate_acceptance(self):
        task=example(); task["acceptance"]*=2; self.assertTrue(fde.validate_task(task))
    def test_boolean_attempts_rejected(self):
        task=example(); task["budget"]["max_attempts"]=True; self.assertTrue(fde.validate_task(task))
    def test_too_many_retries(self):
        task=example(); task["budget"]["max_attempts"]=99; self.assertTrue(fde.validate_task(task))
    def test_nonfinite_cost(self):
        task=example(); task["budget"]["max_external_cost_usd"]=float('inf'); self.assertTrue(fde.validate_task(task))
    def test_bad_input_hash(self):
        task=example(); task["inputs"]=[{"path":"inputs/a","sha256":"fake"}]; self.assertTrue(fde.validate_task(task))
    def test_wildcard_target(self):
        task=example(); task["allowed_targets"]=["*"]; self.assertTrue(fde.validate_task(task))

class PathTests(unittest.TestCase):
    def test_rejects_unsafe_paths(self):
        for name in ["../a","a/../b","/tmp/a","C:/a","a\\b","a//b","a/./b","a/CON","a/thing.","a\x00"]:
            with self.subTest(name=name),self.assertRaises(fde.CheckError): fde.relative_path(name)
    def test_accepts_relative_path(self): self.assertEqual(fde.relative_path("outputs/图片.md"),"outputs/图片.md")
    def test_symlink_parent(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as out:
            root=Path(t); (root/"link").symlink_to(out,target_is_directory=True)
            with self.assertRaises(fde.CheckError): fde.safe_path(root,"link/a",exists=False)
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"x.json";p.write_text('{"a":1,"a":2}')
            with self.assertRaises(fde.CheckError): fde.load_json(p)
    def test_nan_json(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"x.json";p.write_text('{"a":NaN}')
            with self.assertRaises(fde.CheckError): fde.load_json(p)
    def test_timezone_required(self):
        with self.assertRaises(fde.CheckError): fde.timestamp("2026-09-08T12:00:00")

class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/"outputs").mkdir(); self.task=example()
    def request(self,**kwargs): return {"task_sha256":fde.digest(self.task),"action":"local.draft","path":"outputs/a.txt",**kwargs}
    def test_local_scope_no_execution(self):
        value=fde.assess_action(self.task,self.request(),self.root)
        self.assertEqual(value["verdict"],"PREFLIGHT_ONLY");self.assertFalse(value["executed"]);self.assertFalse((self.root/"outputs/a.txt").exists())
    def test_wrong_digest(self): self.assertEqual(fde.assess_action(self.task,self.request(task_sha256="x"),self.root)["verdict"],"DENY")
    def test_outside_scope(self): self.assertEqual(fde.assess_action(self.task,self.request(path="elsewhere/a"),self.root)["verdict"],"DENY")
    def test_stop_marker(self):
        (self.root/".fde").mkdir();(self.root/".fde/STOP").write_text("stop")
        self.assertEqual(fde.assess_action(self.task,self.request(),self.root)["verdict"],"DENY")
    def test_closed_task(self):
        self.task["status"]="CLOSED"; self.assertEqual(fde.assess_action(self.task,self.request(),self.root)["verdict"],"DENY")
    def test_protected_local_write(self):
        self.task["allowed_paths"].append("AGENTS.md")
        self.assertEqual(fde.assess_action(self.task,self.request(path="AGENTS.md"),self.root)["verdict"],"DENY")
    def test_can_read_nonsensitive_instruction(self):
        (self.root/"AGENTS.md").write_text("safe instructions")
        self.task["allowed_paths"].append("AGENTS.md")
        self.assertEqual(fde.assess_action(self.task,self.request(action="local.read",path="AGENTS.md"),self.root)["verdict"],"PREFLIGHT_ONLY")
    def test_cannot_read_credential(self):
        (self.root/"outputs/.env").write_text("SYNTHETIC")
        self.assertEqual(fde.assess_action(self.task,self.request(action="local.read",path="outputs/.env"),self.root)["verdict"],"DENY")
    def test_cannot_read_common_credential_files(self):
        for name in [".netrc",".npmrc",".git-credentials","credentials.json","auth.json",".vault-token","id_rsa","client.p8","client.pfx","vault.kdbx",".docker/config.json",".kube/config",".gnupg/private-keys-v1.d/key",".config/gh/hosts.yml",".config/gcloud/application_default_credentials.json",".config/openai/credentials.toml","Library/Keychains/login.keychain-db","Library/Application Support/Browser/Default/Cookies","client_secret_app.json","service_account_app.json"]:
            with self.subTest(name=name):
                path=self.root/"outputs"/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text("SYNTHETIC")
                self.assertEqual(fde.assess_action(self.task,self.request(action="local.read",path=f"outputs/{name}"),self.root)["verdict"],"DENY")
    def test_sensitive_task_input_rejected_before_hash(self):
        for name in [".netrc",".config/openai/credentials.toml","Library/Keychains/login.keychain-db","Library/Application Support/Browser/Default/Cookies"]:
            with self.subTest(name=name):
                path=self.root/"outputs"/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text("SYNTHETIC")
                self.task["inputs"]=[{"path":f"outputs/{name}","sha256":"0"*64}]
                request=self.request()
                with patch.object(fde,"file_hash",side_effect=AssertionError("credential must not be hashed")) as hasher:
                    self.assertEqual(fde.assess_action(self.task,request,self.root)["verdict"],"DENY")
                    hasher.assert_not_called()
    def test_library_write_protected(self):
        self.task["allowed_paths"].append(".fde")
        self.assertEqual(fde.assess_action(self.task,self.request(path=".fde/vendor/a.txt"),self.root)["verdict"],"DENY")
    def test_changed_input(self):
        p=self.root/"outputs/input";p.write_text("before")
        self.task["inputs"]=[{"path":"outputs/input","sha256":fde.file_hash(p)}];p.write_text("after")
        self.assertEqual(fde.assess_action(self.task,self.request(),self.root)["verdict"],"DENY")
    def test_remote_read_exact_target(self):
        self.task["allowed_actions"].append("remote.read");self.task["allowed_targets"]=["read:product-123"]
        self.assertEqual(fde.assess_action(self.task,self.request(action="remote.read",target="read:other"),self.root)["verdict"],"DENY")
        self.assertEqual(fde.assess_action(self.task,self.request(action="remote.read",target="read:product-123"),self.root)["verdict"],"PREFLIGHT_ONLY")
    def test_forged_approval_cannot_enable_production(self):
        self.task["risk"]="PRODUCTION_WRITE";self.task["allowed_actions"]=["production.change"]
        result=fde.assess_action(self.task,self.request(action="production.change",approval={"approved":True}),self.root)
        self.assertEqual(result["verdict"],"REMOTE_EXECUTOR_REQUIRED");self.assertFalse(result["authorization_granted"])
    def test_delete_never_executed(self):
        self.task["risk"]="HIGH_IMPACT";self.task["allowed_actions"]=["file.delete"]
        self.assertEqual(fde.assess_action(self.task,self.request(action="file.delete"),self.root)["verdict"],"REMOTE_EXECUTOR_REQUIRED")

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/"proof.txt").write_text("fixture")
        self.task=example();self.result={"task_id":self.task["task_id"],"task_sha256":fde.digest(self.task),"checks":[{"id":"AC-1","status":"PASS","evidence":[{"path":"proof.txt","sha256":fde.file_hash(self.root/"proof.txt")}]}]}
    def test_valid_files_not_release(self):
        out=fde.verify_evidence(self.task,self.result,self.root);self.assertEqual(out["verdict"],"EVIDENCE_FILES_VERIFIED");self.assertFalse(out["release_authorized"]);self.assertFalse(out["business_claims_verified"])
    def test_changed_evidence(self):
        (self.root/"proof.txt").write_text("changed");self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
    def test_missing_check(self):
        self.result["checks"]=[];self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
    def test_duplicate_check(self):
        self.result["checks"]*=2;self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
    def test_failed_check(self):
        self.result["checks"][0]["status"]="FAIL";self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
    def test_claim_without_file(self):
        self.result["checks"][0]["evidence"]=[];self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
    def test_sensitive_evidence_rejected_before_hash(self):
        (self.root/".netrc").write_text("SYNTHETIC")
        self.result["checks"][0]["evidence"]=[{"path":".netrc","sha256":"0"*64}]
        with patch.object(fde,"file_hash",side_effect=AssertionError("credential must not be hashed")) as hasher:
            self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
            hasher.assert_not_called()
    def test_sensitive_task_input_not_hashed_during_evidence_check(self):
        (self.root/".netrc").write_text("SYNTHETIC")
        self.task["inputs"]=[{"path":".netrc","sha256":"0"*64}]
        self.result["task_sha256"]=fde.digest(self.task);self.result["checks"]=[]
        with patch.object(fde,"file_hash",side_effect=AssertionError("credential must not be hashed")) as hasher:
            self.assertEqual(fde.verify_evidence(self.task,self.result,self.root)["verdict"],"INVALID")
            hasher.assert_not_called()

class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/".fde/tmp/t/r").mkdir(parents=True);(self.root/"evidence").mkdir()
        self.p=self.root/".fde/tmp/t/r/a.txt";self.p.write_text("temp");(self.root/"evidence/proof").write_text("saved")
        self.now=datetime.now(timezone.utc);old=(self.now-timedelta(days=2)).timestamp();os.utime(self.p,(old,old))
        self.item={"path":".fde/tmp/t/r/a.txt","sha256":fde.file_hash(self.p),"task_status":"CLOSED","closed_at":(self.now-timedelta(days=2)).isoformat(),"classification":"rebuildable-temp","referenced":False,"active_writer":False,"legal_hold":False,"durable_outputs_verified":True,"durable_evidence":{"path":"evidence/proof","sha256":fde.file_hash(self.root/"evidence/proof")}}
        self.manifest={"schema_version":1,"generated_at":self.now.isoformat(),"temp_root":".fde/tmp","items":[self.item]}
    def run_plan(self):
        with patch.object(fde,"git_tracked",return_value=False): return fde.cleanup_plan(self.root,self.manifest,now=self.now)
    def test_candidate_not_deleted(self):
        result=self.run_plan();self.assertTrue(result["items"][0]["candidate"]);self.assertEqual(result["deleted"],0);self.assertTrue(self.p.exists())
    def test_active_reference(self):
        self.item["referenced"]=True;self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_unclosed(self):
        self.item["task_status"]="RUNNING";self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_recent(self):
        self.item["closed_at"]=self.now.isoformat();self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_durable_evidence_missing(self):
        self.item["durable_evidence"]["path"]="absent";self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_sensitive_durable_evidence_rejected_before_hash(self):
        (self.root/".netrc").write_text("SYNTHETIC")
        self.item["durable_evidence"]={"path":".netrc","sha256":"0"*64}
        original_hash=fde.file_hash
        def guarded_hash(path):
            if path.name == ".netrc":
                raise AssertionError("credential must not be hashed")
            return original_hash(path)
        with patch.object(fde,"file_hash",side_effect=guarded_hash) as hasher:
            with patch.object(fde,"git_tracked",return_value=False):
                result=fde.cleanup_plan(self.root,self.manifest,now=self.now)
            self.assertFalse(result["items"][0]["candidate"])
            self.assertEqual(hasher.call_count,1)
    def test_hash_changed(self):
        self.item["sha256"]="0"*64;self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_symlink_protected(self):
        (self.root/".fde/tmp/t/r/link").symlink_to(self.root/"evidence/proof");self.item["path"]=".fde/tmp/t/r/link"
        self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_hardlink_protected(self):
        os.link(self.p,self.root/"evidence/link");self.assertFalse(self.run_plan()["items"][0]["candidate"])
    def test_tracking_unknown_protected(self):
        with patch.object(fde,"git_tracked",return_value=None):self.assertFalse(fde.cleanup_plan(self.root,self.manifest,now=self.now)["items"][0]["candidate"])
    def test_git_tracked_protected(self):
        with patch.object(fde,"git_tracked",return_value=True):self.assertFalse(fde.cleanup_plan(self.root,self.manifest,now=self.now)["items"][0]["candidate"])
    @unittest.skipUnless(shutil.which("git"),"git required")
    def test_nested_git_tracked_file_protected(self):
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        nested=self.root/".fde/tmp/t"
        subprocess.run(["git","init","-q",str(nested)],check=True)
        subprocess.run(["git","-C",str(nested),"add","r/a.txt"],check=True)
        result=fde.cleanup_plan(self.root,self.manifest,now=self.now)
        self.assertFalse(result["items"][0]["candidate"])
        self.assertIn("Git tracked or tracking status unverified",result["items"][0]["reasons"])
    @unittest.skipUnless(shutil.which("git"),"git required")
    def test_outer_git_tracked_file_protected_inside_nested_repo(self):
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        subprocess.run(["git","-C",str(self.root),"add",".fde/tmp/t/r/a.txt"],check=True)
        subprocess.run(["git","init","-q",str(self.root/".fde/tmp/t")],check=True)
        self.assertTrue(fde.git_tracked(self.root,".fde/tmp/t/r/a.txt"))
    @unittest.skipUnless(shutil.which("git"),"git required")
    def test_git_tracking_check_disables_fsmonitor_execution(self):
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        subprocess.run(["git","-C",str(self.root),"add",".fde/tmp/t/r/a.txt"],check=True)
        marker=self.root/"fsmonitor-executed";hook=self.root/"fsmonitor-hook"
        hook.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n")
        hook.chmod(0o700)
        subprocess.run(["git","-C",str(self.root),"config","core.fsmonitor",str(hook)],check=True)
        subprocess.run(["git","-C",str(self.root),"ls-files","--error-unmatch","--",".fde/tmp/t/r/a.txt"],capture_output=True,text=True)
        self.assertTrue(marker.exists());marker.unlink()
        self.assertTrue(fde.git_tracked(self.root,".fde/tmp/t/r/a.txt"))
        self.assertFalse(marker.exists())
    @unittest.skipUnless(shutil.which("git"),"git required")
    def test_linked_worktree_tracked_file_protected(self):
        with tempfile.TemporaryDirectory() as temp:
            base=Path(temp)/"base";linked=Path(temp)/"linked";base.mkdir()
            subprocess.run(["git","init","-q",str(base)],check=True)
            tracked=base/"tracked.txt";tracked.write_text("fixture")
            subprocess.run(["git","-C",str(base),"add","tracked.txt"],check=True)
            subprocess.run(["git","-C",str(base),"-c","user.name=FDE Test","-c","user.email=fde-test@example.invalid","commit","-qm","fixture"],check=True)
            subprocess.run(["git","-C",str(base),"worktree","add","-q","--detach",str(linked),"HEAD"],check=True)
            self.assertTrue(fde.git_tracked(linked,"tracked.txt"))
    def test_stale_manifest(self):
        self.manifest["generated_at"]=(self.now-timedelta(hours=2)).isoformat()
        with self.assertRaises(fde.CheckError):self.run_plan()
    def test_wrong_namespace(self):
        self.manifest["temp_root"]="Desktop"
        with self.assertRaises(fde.CheckError):self.run_plan()

class BundleAndInstallTests(unittest.TestCase):
    def setUp(self):
        self.expected=fde.file_hash(ROOT/"MANIFEST.json")
    def test_manifest_matches(self):self.assertGreater(len(fde.verify_bundle(ROOT,self.expected)),20)
    def test_wrong_manifest_hash(self):
        with self.assertRaises(fde.CheckError):fde.verify_bundle(ROOT,"0"*64)
    def test_unlisted_bundle_file_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            (copy/"UNLISTED.txt").write_text("not reviewed")
            with self.assertRaises(fde.CheckError):fde.verify_bundle(copy,fde.file_hash(copy/"MANIFEST.json"))
    def test_readme_puts_isolated_exact_verify_first(self):
        readme=(ROOT/"README.md").read_text()
        gate="python3 -I -B tools/fde.py verify-bundle"
        self.assertIn(gate,readme)
        self.assertLess(readme.index(gate),readme.index("python3 tools/fde.py doctor"))
        self.assertIn("python3 -B -m unittest discover -s tests -v",readme)
    def test_isolated_verify_rejects_shadow_module_before_execution(self):
        with tempfile.TemporaryDirectory() as t:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            marker=Path(t)/"shadow-executed"
            (copy/"tools/hashlib.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n")
            process=subprocess.run([sys.executable,"-I","-B",str(copy/"tools/fde.py"),"verify-bundle","--root",str(copy),"--expected-manifest-sha256",self.expected],capture_output=True,text=True)
            self.assertNotEqual(process.returncode,0)
            self.assertFalse(marker.exists())
    def test_audit_does_not_execute_unchecked_local_fde_bytecode(self):
        with tempfile.TemporaryDirectory() as t:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            marker=Path(t)/"pyc-executed";malicious=Path(t)/"malicious.py"
            malicious.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n")
            cache=copy/"tools/__pycache__"/f"fde.{sys.implementation.cache_tag}.pyc"
            cache.parent.mkdir(parents=True)
            py_compile.compile(str(malicious),cfile=str(cache),doraise=True,invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
            process=subprocess.run([sys.executable,str(copy/"tools/audit_bundle.py"),"--root",str(copy),"--expected-manifest-sha256",self.expected],capture_output=True,text=True)
            self.assertNotEqual(process.returncode,0)
            self.assertFalse(marker.exists())
    def test_nested_git_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            (copy/"nested/.git").mkdir(parents=True);(copy/"nested/.git/config").write_text("fixture")
            with self.assertRaises(fde.CheckError):fde.verify_bundle(copy,fde.file_hash(copy/"MANIFEST.json"))
    def test_nested_git_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as outside:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            (copy/"nested").mkdir();(copy/"nested/.git").symlink_to(outside,target_is_directory=True)
            with self.assertRaises(fde.CheckError):fde.verify_bundle(copy,fde.file_hash(copy/"MANIFEST.json"))
    @unittest.skipUnless(hasattr(os,"mkfifo"),"FIFO fixture unsupported")
    def test_unlisted_fifo_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            copy=Path(t)/"bundle";shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns(".git"))
            os.mkfifo(copy/"UNLISTED.pipe")
            with self.assertRaises(fde.CheckError):fde.verify_bundle(copy,fde.file_hash(copy/"MANIFEST.json"))
    def test_plugin_minimal(self):
        data=fde.load_json(ROOT/".codex-plugin/plugin.json");self.assertEqual(data["skills"],"./skills/");self.assertNotIn("hooks",data);self.assertNotIn("mcpServers",data)
        self.assertEqual(data["version"],fde.VERSION);self.assertTrue(data["author"]["name"])
        for field in ["displayName","shortDescription","longDescription","developerName","category","capabilities","defaultPrompt"]:
            self.assertIn(field,data["interface"])
    def test_workspace_marketplace(self):
        data=fde.load_json(ROOT/".agents/plugins/marketplace.json");self.assertEqual(len(data["plugins"]),1)
        entry=data["plugins"][0];self.assertEqual(entry["name"],"fde-delivery-toolbox")
        self.assertEqual(entry["source"],{"source":"local","path":"./"})
        self.assertEqual(entry["policy"]["installation"],"AVAILABLE")
    def test_delivery_templates_present(self):
        for name in ["SCENARIO_CARD.md","INTEGRATION_CONTRACT.md","EVAL_RELEASE_SCORECARD.md","REUSE_FEEDBACK.md"]:
            self.assertTrue((ROOT/"templates"/name).is_file())
    def test_generic_example_has_no_customer_identity(self):
        data=fde.load_json(ROOT/"examples/enterprise-workflow.profile.example.json")
        self.assertEqual(data["project_id"],"enterprise-workflow-example");self.assertTrue(data["example_only"])
    def test_each_skill_metadata(self):
        for name in fde.SKILL_NAMES:
            content=(ROOT/f"skills/{name}/SKILL.md").read_text();self.assertTrue(content.startswith("---\nname: "+name+"\n"));self.assertIn("description:",content)
    def test_install_plan_no_write(self):
        with tempfile.TemporaryDirectory() as t:
            plan=install.build_plan(ROOT,Path(t),self.expected,["fde-discovery"]);self.assertEqual(plan["mode"],"DRY_RUN");self.assertEqual(list(Path(t).iterdir()),[])
    def test_install_and_idempotent(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);selected=["fde-discovery","fde-connector-preflight"]
            out=install.apply_plan(install.build_plan(ROOT,root,self.expected,selected));self.assertEqual(out["mode"],"INSTALLED_FILES_ONLY")
            self.assertTrue((root/".agents/skills/fde-discovery/SKILL.md").is_file());self.assertFalse((root/"AGENTS.md").exists())
            again=install.apply_plan(install.build_plan(ROOT,root,self.expected,selected));self.assertEqual(again["mode"],"ALREADY_INSTALLED")
    def test_install_created_files_includes_lock(self):
        with tempfile.TemporaryDirectory() as source_dir,tempfile.TemporaryDirectory() as project_dir:
            source=Path(source_dir);project=Path(project_dir);payload=source/"payload.txt";payload.write_text("fixture")
            plan={"schema_version":1,"mode":"DRY_RUN","source":str(source),"project":str(project),
                  "version":fde.VERSION,"manifest_sha256":"0"*64,"skills":["fde-discovery"],
                  "bundle_root":".fde/vendor/fde-delivery-toolbox/test","copies":[{
                      "source":"payload.txt","destination":".agents/skills/fde-discovery/payload.txt",
                      "sha256":fde.file_hash(payload)}],"already_installed":False,
                  "global_configuration_changed":False,"native_registration_verified":False}
            with patch.object(install,"build_plan",return_value=plan):out=install.apply_plan(plan)
            self.assertEqual(out["created_files"],2)
            self.assertEqual(sum(1 for path in project.rglob("*") if path.is_file()),2)
    def test_install_refuses_existing_skill(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/".agents/skills/fde-discovery";p.mkdir(parents=True);(p/"SKILL.md").write_text("old")
            with self.assertRaises(fde.CheckError):install.build_plan(ROOT,root,self.expected,["fde-discovery"])
    def test_install_refuses_symlink(self):
        with tempfile.TemporaryDirectory() as t,tempfile.TemporaryDirectory() as target:
            root=Path(t);(root/".agents").symlink_to(target,target_is_directory=True)
            with self.assertRaises(fde.CheckError):install.build_plan(ROOT,root,self.expected,["fde-discovery"])
    def test_invalid_skill(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(fde.CheckError):install.build_plan(ROOT,Path(t),self.expected,["../evil"])
    def test_install_stop(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/".fde").mkdir();(root/".fde/STOP").write_text("stop")
            with self.assertRaises(fde.CheckError):install.build_plan(ROOT,root,self.expected,["fde-discovery"])
    def test_install_refuses_global_roots(self):
        for root in [Path.home(),Path.home()/"Desktop",Path.home()/".codex",Path.home()/".config",Path("/etc")]:
            if root.is_dir():
                with self.subTest(root=root),self.assertRaises(fde.CheckError):
                    install.build_plan(ROOT,root,self.expected,["fde-discovery"])
    def test_install_refuses_source_as_project(self):
        with self.assertRaises(fde.CheckError):
            install.build_plan(ROOT,ROOT,self.expected,["fde-discovery"])
        with self.assertRaises(fde.CheckError):
            install.build_plan(ROOT,ROOT/"tests",self.expected,["fde-discovery"])
    def test_heuristic_scan(self):
        out=audit_bundle.audit(ROOT,self.expected);self.assertEqual(out["heuristic_scan"],"NO_MATCHES")
        self.assertEqual(out["scanned_files"],len(fde.verify_bundle(ROOT,self.expected))+1)
    def test_secret_shape_recognized(self):
        synthetic="ghp_"+"A"*40;self.assertTrue(audit_bundle.PATTERNS["github_token_shape"].search(synthetic))
    def test_publish_dry_run_no_cli(self):
        with patch.object(publish_github.subprocess,"run",side_effect=AssertionError("No subprocess in dry-run")):
            out=publish_github.publish(ROOT,"example-user","fde-delivery-toolbox",self.expected)
        self.assertEqual(out["status"],"NOT_UPLOADED");self.assertEqual(out["visibility"],"private")
    def test_git_environment_overrides_removed(self):
        injected={"GIT_DIR":"/tmp/external.git","GIT_WORK_TREE":"/tmp/external-tree","GIT_CONFIG_COUNT":"1","GIT_CONFIG_KEY_0":"core.fsmonitor","GIT_CONFIG_VALUE_0":"/tmp/hook","GIT_TRACE":"/tmp/trace"}
        with patch.dict(os.environ,injected,clear=False):
            environment=fde.safe_git_environment()
        for name in injected:
            self.assertNotIn(name,environment)
        self.assertEqual(environment["GIT_OPTIONAL_LOCKS"],"0")
    def test_publisher_environment_pins_public_github(self):
        injected={"GH_HOST":"ghe.example.invalid","GH_REPO":"other/target","GH_DEBUG":"api","GH_FORCE_TTY":"120"}
        with patch.dict(os.environ,injected,clear=False):
            environment=publish_github.safe_publisher_environment()
        self.assertEqual(environment["GH_HOST"],"github.com")
        self.assertEqual(environment["GH_PROMPT_DISABLED"],"1")
        for name in ("GH_REPO","GH_DEBUG","GH_FORCE_TTY"):
            self.assertNotIn(name,environment)
    def test_publisher_remote_identity_is_exact(self):
        publish_github.validate_remote_url("https://github.com/example-user/fde-delivery-toolbox.git","example-user","fde-delivery-toolbox")
        publish_github.validate_remote_url("git@github.com:example-user/fde-delivery-toolbox.git","example-user","fde-delivery-toolbox")
        metadata={"nameWithOwner":"example-user/fde-delivery-toolbox","isPrivate":True,
                  "url":"https://github.com/example-user/fde-delivery-toolbox"}
        publish_github.validate_remote_metadata(metadata,"example-user","fde-delivery-toolbox")
        for bad in ("https://ghe.example.invalid/example-user/fde-delivery-toolbox.git",
                    "https://github.com/example-user/other.git"):
            with self.assertRaises(fde.CheckError):
                publish_github.validate_remote_url(bad,"example-user","fde-delivery-toolbox")
        with self.assertRaises(fde.CheckError):
            publish_github.validate_remote_metadata({**metadata,"nameWithOwner":"other/fde-delivery-toolbox"},"example-user","fde-delivery-toolbox")
        with self.assertRaises(fde.CheckError):
            publish_github.validate_remote_metadata({**metadata,"url":"https://ghe.example.invalid/example-user/fde-delivery-toolbox"},"example-user","fde-delivery-toolbox")
    def test_publisher_rejects_rewritten_push_destination(self):
        git=shutil.which("git")
        if not git:self.skipTest("git unavailable")
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            subprocess.run([git,"init"],cwd=root,check=True,capture_output=True)
            subprocess.run([git,"remote","add","origin","https://github.com/example-user/fde-delivery-toolbox.git"],cwd=root,check=True)
            subprocess.run([git,"config","url.https://evil.invalid/.pushInsteadOf","https://github.com/"],cwd=root,check=True)
            self.assertEqual(subprocess.run([git,"remote","get-url","origin"],cwd=root,check=True,capture_output=True,text=True).stdout.strip(),
                             "https://github.com/example-user/fde-delivery-toolbox.git")
            with self.assertRaises(fde.CheckError):
                publish_github.validate_git_remote(git,root,"example-user","fde-delivery-toolbox")
    def test_publisher_rejects_any_additional_push_destination(self):
        git=shutil.which("git")
        if not git:self.skipTest("git unavailable")
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            subprocess.run([git,"init"],cwd=root,check=True,capture_output=True)
            subprocess.run([git,"remote","add","origin","https://github.com/example-user/fde-delivery-toolbox.git"],cwd=root,check=True)
            subprocess.run([git,"config","--add","remote.origin.pushurl","https://github.com/example-user/fde-delivery-toolbox.git"],cwd=root,check=True)
            subprocess.run([git,"config","--add","remote.origin.pushurl","https://evil.invalid/example-user/fde-delivery-toolbox.git"],cwd=root,check=True)
            self.assertEqual(subprocess.run([git,"remote","get-url","--push","origin"],cwd=root,check=True,capture_output=True,text=True).stdout.strip(),
                             "https://github.com/example-user/fde-delivery-toolbox.git")
            with self.assertRaises(fde.CheckError):
                publish_github.validate_git_remote(git,root,"example-user","fde-delivery-toolbox")
    def test_publisher_rejects_other_repository(self):
        with self.assertRaises(fde.CheckError):publish_github.validate_destination("example-user","customer-production")
    def test_publisher_requires_real_cli(self):
        with patch.object(publish_github.shutil,"which",return_value=None):
            with self.assertRaises(fde.CheckError):publish_github.publish(ROOT,"example-user","fde-delivery-toolbox",self.expected,apply=True)
    def test_doctor_no_secrets_no_auth_claim(self):
        out=fde.doctor();self.assertFalse(out["secrets_read"]);self.assertEqual(out["connector_auth"],"NOT_PROBED")

if __name__=="__main__":unittest.main()
