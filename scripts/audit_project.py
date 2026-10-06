#!/usr/bin/env python3
"""
Mauro Quality Gate (MQG) — General Software Project Auditor
Audits local repositories or remote GitHub repositories against Mauro Druwel's
engineering standards for Tauri, TypeScript, Rust, and Python projects.

Usage:
    python scripts/audit_project.py /path/to/project
    python scripts/audit_project.py MauroDruwel/TunnelDashDesktop --remote
    python scripts/audit_project.py . --strict --json
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# ANSI Color formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


class ProjectAuditor:
    def __init__(self, root_path: Path, remote_repo: Optional[str] = None, quiet: bool = False):
        self.root = root_path.resolve()
        self.remote_repo = remote_repo
        self.quiet = quiet
        self.results: List[Dict[str, Any]] = []
        self.project_type = self.detect_project_type()

    def check(self, passed: bool, label: str, detail: str = "", critical: bool = True, section: str = "General"):
        status = "PASS" if passed else ("WARN" if not critical else "FAIL")
        record = {
            "section": section,
            "label": label,
            "detail": detail,
            "status": status,
            "critical": critical,
            "passed": passed,
        }
        self.results.append(record)

        if not self.quiet:
            if passed:
                print(f"  {GREEN}✅ PASS{RESET}   {label:<34} {detail}")
            elif not critical:
                print(f"  {YELLOW}⚠️  WARN{RESET}   {label:<34} {detail}")
            else:
                print(f"  {RED}❌ FAIL{RESET}   {label:<34} {detail}")

    def find_openapi_spec(self) -> Optional[Path]:
        candidates = [
            self.root / "docs" / "openapi.yaml",
            self.root / "docs" / "openapi.yml",
            self.root / "docs" / "openapi.json",
            self.root / "openapi.yaml",
            self.root / "openapi.yml",
            self.root / "openapi.json",
            self.root / "api" / "openapi.yaml",
            self.root / "api" / "openapi.json",
            self.root / "spec" / "openapi.yaml",
            self.root / "spec" / "openapi.json",
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    def audit_openapi_spec(self, spec_path: Path, sec: str):
        valid = False
        detail = "Failed to parse spec"
        try:
            content = spec_path.read_text(encoding="utf-8", errors="ignore")
            if spec_path.suffix == ".json":
                data = json.loads(content)
            else:
                try:
                    import yaml
                    data = yaml.safe_load(content)
                except ImportError:
                    data = {"openapi": "3.0" if "openapi:" in content else None}

            if isinstance(data, dict):
                ver = data.get("openapi") or data.get("swagger")
                info = data.get("info", {})
                title = info.get("title", "Untitled")
                paths = data.get("paths", {})
                if ver and str(ver).startswith("3.") and len(paths) > 0:
                    valid = True
                    detail = f"OpenAPI {ver} | '{title}' ({len(paths)} endpoints)"
                elif ver:
                    valid = True
                    detail = f"Version: {ver} | '{title}'"
        except Exception as e:
            detail = f"Parse error: {e}"
        self.check(valid, "OpenAPI 3.x schema valid", detail, section=sec)

    def detect_project_type(self) -> str:
        if (self.root / "src-tauri" / "tauri.conf.json").exists() or (self.root / "src-tauri" / "Cargo.toml").exists():
            return "tauri"
        if (
            (self.root / "forge.config.ts").exists()
            or (self.root / "forge.config.js").exists()
            or (self.root / "cloudflare.config.ts").exists()
        ):
            return "forge"
        if (self.root / "package.json").exists():
            return "typescript"
        if (self.root / "pyproject.toml").exists() or (self.root / "setup.py").exists():
            return "python"
        if (self.root / "Cargo.toml").exists():
            return "rust"
        if self.find_openapi_spec():
            return "forge"
        return "generic"

    def audit_governance(self):
        sec = "Governance & Repository Hygiene"
        if not self.quiet:
            print(f"\n{BLUE}{BOLD}[1. {sec.upper()}]{RESET}")
        
        # README check
        readme = self.root / "README.md"
        readme_ok = readme.exists() and readme.stat().st_size > 100
        self.check(readme_ok, "README.md present", f"Size: {readme.stat().st_size if readme.exists() else 0} bytes", section=sec)

        # LICENSE check
        license_file = self.root / "LICENSE"
        license_ok = False
        license_detail = "Missing"
        if license_file.exists():
            content = license_file.read_text(errors="ignore")
            if "Mauro Druwel" in content and "MIT" in content:
                license_ok = True
                license_detail = "MIT © Mauro Druwel"
            elif "Mauro Druwel" in content:
                license_ok = True
                license_detail = "Copyright Mauro Druwel"
            else:
                license_detail = "Missing copyright attribution to Mauro Druwel"
        self.check(license_ok, "LICENSE (MIT © Mauro Druwel)", license_detail, section=sec)

        # CHANGELOG.md check
        changelog = self.root / "CHANGELOG.md"
        self.check(changelog.exists(), "CHANGELOG.md present", "Exists" if changelog.exists() else "Missing", critical=False, section=sec)

        # .gitignore check
        gitignore = self.root / ".gitignore"
        self.check(gitignore.exists(), ".gitignore present", "Exists" if gitignore.exists() else "Missing", section=sec)

        # Clean git state (no .DS_Store committed)
        ds_store = list(self.root.rglob(".DS_Store"))
        self.check(len(ds_store) == 0, "No .DS_Store files present", f"Found {len(ds_store)}" if ds_store else "Clean", critical=False, section=sec)

    def audit_architecture_and_tooling(self):
        sec = f"Architecture & Tooling ({self.project_type.upper()})"
        if not self.quiet:
            print(f"\n{BLUE}{BOLD}[2. {sec.upper()}]{RESET}")

        if self.project_type == "tauri":
            self.check((self.root / "src-tauri").is_dir(), "src-tauri directory present", "Tauri backend", section=sec)
            self.check((self.root / "src-tauri" / "Cargo.toml").exists(), "Rust Cargo.toml present", "Dependencies", section=sec)
            self.check((self.root / "package.json").exists(), "package.json present", "Frontend app", section=sec)
            
            # Check lockfiles
            has_lock = (self.root / "pnpm-lock.yaml").exists() or (self.root / "package-lock.yaml").exists()
            self.check(has_lock, "Frontend lockfile committed", "pnpm or npm lockfile", section=sec)
            self.check((self.root / "src-tauri" / "Cargo.lock").exists(), "Cargo.lock committed", "Rust lockfile", section=sec)

            # Check linter
            has_lint = (self.root / "eslint.config.js").exists() or (self.root / ".eslintrc.json").exists() or (self.root / ".eslintrc.js").exists()
            self.check(has_lint, "ESLint configuration present", "Frontend linter", section=sec)

            # Check tauri config bundle identifier
            tauri_conf = self.root / "src-tauri" / "tauri.conf.json"
            valid_id = False
            id_detail = "Missing tauri.conf.json"
            if tauri_conf.exists():
                try:
                    tdata = json.loads(tauri_conf.read_text(errors="ignore"))
                    bundle_id = tdata.get("identifier", "")
                    if bundle_id and bundle_id != "com.tauri.dev":
                        valid_id = True
                        id_detail = f"Identifier: {bundle_id}"
                    else:
                        id_detail = f"Default or invalid identifier: '{bundle_id}'"
                except Exception as e:
                    id_detail = f"Malformed tauri.conf.json: {e}"
            self.check(valid_id, "Tauri unique bundle identifier", id_detail, section=sec)

        elif self.project_type == "typescript":
            self.check((self.root / "package.json").exists(), "package.json present", section=sec)
            self.check((self.root / "tsconfig.json").exists(), "tsconfig.json present", "TypeScript compiler options", section=sec)
            has_lock = (self.root / "pnpm-lock.yaml").exists() or (self.root / "package-lock.yaml").exists()
            self.check(has_lock, "Package lockfile committed", "Reproducible builds", section=sec)
            has_lint = (self.root / "eslint.config.js").exists() or (self.root / ".eslintrc.json").exists()
            self.check(has_lint, "ESLint configuration present", "Linter config", section=sec)

        elif self.project_type == "python":
            pyproject = self.root / "pyproject.toml"
            self.check(pyproject.exists(), "pyproject.toml present", "Modern packaging", section=sec)
            has_ruff = False
            if pyproject.exists():
                content = pyproject.read_text(errors="ignore")
                has_ruff = "tool.ruff" in content
            self.check(has_ruff, "Ruff configuration in pyproject", "Fast linter/formatter", critical=False, section=sec)

        elif self.project_type == "forge":
            spec_path = self.find_openapi_spec()
            self.check(spec_path is not None, "OpenAPI specification present", f"{spec_path.relative_to(self.root)}" if spec_path else "Missing openapi.yaml", section=sec)
            if spec_path:
                self.audit_openapi_spec(spec_path, sec)
            has_forge_conf = (
                (self.root / "forge.config.ts").exists()
                or (self.root / "forge.config.js").exists()
                or (self.root / "cloudflare.config.ts").exists()
            )
            self.check(has_forge_conf, "Forge configuration present", "forge.config.ts" if has_forge_conf else "Missing forge.config.ts", critical=False, section=sec)
            has_lock = (self.root / "pnpm-lock.yaml").exists() or (self.root / "package-lock.yaml").exists() or (self.root / "uv.lock").exists() or (self.root / "Cargo.lock").exists()
            self.check(has_lock, "Package lockfile committed", "Committed lockfile", critical=False, section=sec)

        # Audit OpenAPI schema for projects that define an API surface alongside other archetypes
        spec_path = self.find_openapi_spec()
        if spec_path and self.project_type != "forge":
            sec_api = "API Schema & Cloudflare Forge"
            if not self.quiet:
                print(f"\n{BLUE}{BOLD}[2b. {sec_api.upper()}]{RESET}")
            self.check(True, "OpenAPI specification present", f"{spec_path.relative_to(self.root)} ({spec_path.stat().st_size} bytes)", section=sec_api)
            self.audit_openapi_spec(spec_path, sec_api)
            has_forge = (
                (self.root / "forge.config.ts").exists()
                or (self.root / "forge.config.js").exists()
                or (self.root / "cloudflare.config.ts").exists()
            )
            self.check(has_forge, "Cloudflare Forge config present", "forge.config.ts" if has_forge else "Optional client generation pipeline", critical=False, section=sec_api)

    def audit_ci_cd(self):
        sec = "CI/CD Automation & Workflows"
        if not self.quiet:
            print(f"\n{BLUE}{BOLD}[3. {sec.upper()}]{RESET}")
        workflows_dir = self.root / ".github" / "workflows"
        has_workflows_dir = workflows_dir.is_dir()
        self.check(has_workflows_dir, ".github/workflows directory", "CI pipelines", section=sec)

        if has_workflows_dir:
            yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            self.check(len(yaml_files) > 0, "Active workflow pipelines", f"Found {len(yaml_files)} workflow(s)", section=sec)
            
            # Check if any workflow uses MQG or is MQG itself
            uses_mqg = False
            mqg_archetype_match = False
            is_mqg_itself = self.root.name == "quality-gate" or (self.remote_repo and "quality-gate" in self.remote_repo)
            
            expected_actions = [f"{self.project_type}-ci.yml"]
            if self.project_type == "forge":
                expected_actions = ["forge-ci.yml"]
            elif self.find_openapi_spec():
                # Hybrid project with OpenAPI can use its native language CI or forge-ci.yml
                expected_actions = [f"{self.project_type}-ci.yml", "forge-ci.yml"]

            for yf in yaml_files:
                text = yf.read_text(errors="ignore")
                if "MauroDruwel/quality-gate" in text or "MauroDruwel/ha-quality-gate" in text or is_mqg_itself:
                    uses_mqg = True
                for ea in expected_actions:
                    if ea in text:
                        mqg_archetype_match = True
                        break
                if is_mqg_itself or self.project_type == "generic":
                    mqg_archetype_match = True

            self.check(uses_mqg, "Uses Mauro Quality Gate actions", "Canonical MQG provider" if is_mqg_itself else "Reusing centralized MQG workflows", critical=False, section=sec)
            self.check(mqg_archetype_match, f"CI matches archetype ({self.project_type})", f"Uses {', '.join(expected_actions)}" if mqg_archetype_match else f"Expected one of {expected_actions} in workflows", critical=False, section=sec)
        else:
            self.check(False, "Active workflow pipelines", "None found", section=sec)

    def audit_tests(self):
        sec = "Automated Tests & Verification"
        if not self.quiet:
            print(f"\n{BLUE}{BOLD}[4. {sec.upper()}]{RESET}")
        
        has_tests = False
        test_detail = "None found"
        
        if self.project_type == "tauri":
            test_files = list(self.root.glob("src/**/*.test.ts")) + list(self.root.glob("src/**/*.test.tsx"))
            rust_tests = False
            if (self.root / "src-tauri").is_dir():
                for rs in (self.root / "src-tauri").rglob("*.rs"):
                    if "#[test]" in rs.read_text(errors="ignore"):
                        rust_tests = True
                        break
            has_tests = (len(test_files) > 0) or rust_tests
            detail_parts = []
            if test_files:
                detail_parts.append(f"{len(test_files)} frontend test file(s)")
            if rust_tests:
                detail_parts.append("Rust unit test suite")
            test_detail = " + ".join(detail_parts) if detail_parts else "None found"
        elif self.project_type == "typescript":
            test_files = list(self.root.glob("**/*.test.ts")) + list(self.root.glob("**/*.spec.ts"))
            has_tests = len(test_files) > 0 or (self.root / "tests").is_dir()
            test_detail = f"Found {len(test_files)} test file(s)"
        elif self.project_type == "python":
            has_tests = (self.root / "tests").is_dir()
            test_detail = "tests/ directory" if has_tests else "Missing tests/"
        elif self.project_type == "rust":
            has_tests = (self.root / "tests").is_dir() or list(self.root.glob("src/**/*.rs"))
            test_detail = "Cargo test suite"
        elif self.project_type == "forge":
            test_files = list(self.root.glob("tests/**/*.*")) + list(self.root.glob("spec/**/*.test.*"))
            has_tests = len(test_files) > 0 or (self.root / "tests").is_dir()
            test_detail = f"Found {len(test_files)} test/spec file(s)" if test_files else ("tests/ directory" if has_tests else "Missing tests/")
        else:
            tests_dir = self.root / "tests"
            if tests_dir.is_dir():
                test_files = list(tests_dir.glob("test_*.py")) + list(tests_dir.glob("*.test.*"))
                has_tests = len(test_files) > 0
                test_detail = f"Found {len(test_files)} test file(s) in tests/"

        self.check(has_tests, "Test suite present", test_detail, section=sec)

    def audit_remote(self):
        if not self.remote_repo:
            return
        sec = "GitHub Metadata & Repository Topics"
        if not self.quiet:
            print(f"\n{BLUE}{BOLD}[5. {sec.upper()}]{RESET}")
        try:
            res = subprocess.run(
                ["gh", "repo", "view", self.remote_repo, "--json", "description,repositoryTopics"],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(res.stdout)
            desc = data.get("description") or ""
            topics = [t["name"] for t in data.get("repositoryTopics", [])]

            self.check(bool(desc.strip()), "GitHub repository description set", f"'{desc[:40]}...'", section=sec)
            self.check(len(topics) > 0, "Repository topics configured", f"{topics}", section=sec)
            self.check(len(topics) <= 6, "Focused topic tagging (<= 6)", f"{len(topics)} topics", critical=False, section=sec)
        except Exception as e:
            self.check(False, "Query GitHub API via gh", str(e), critical=False, section=sec)

    def run(self, strict: bool = False) -> Tuple[bool, Dict[str, Any]]:
        if not self.quiet:
            print(f"{BOLD}======================================================={RESET}")
            print(f"{BOLD}   MAURO QUALITY GATE AUDIT: {self.remote_repo or self.root.name}{RESET}")
            print(f"   Detected Project Archetype: {BOLD}{self.project_type.upper()}{RESET}")
            print(f"{BOLD}======================================================={RESET}")

        self.audit_governance()
        self.audit_architecture_and_tooling()
        self.audit_ci_cd()
        self.audit_tests()
        self.audit_remote()

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warn = sum(1 for r in self.results if r["status"] == "WARN")
        fail = sum(1 for r in self.results if r["status"] == "FAIL")
        score = (passed / total * 100) if total > 0 else 0

        is_passed = (fail == 0) if not strict else (fail == 0 and warn == 0)

        if not self.quiet:
            print(f"\n{BOLD}-------------------------------------------------------{RESET}")
            print(f"  Total Checks: {total} | Passed: {GREEN}{passed}{RESET} | Warn: {YELLOW}{warn}{RESET} | Fail: {RED}{fail}{RESET}")
            status_str = f"{GREEN}PASSED QUALITY GATE{RESET}" if is_passed else f"{RED}FAILED QUALITY GATE{RESET}"
            print(f"  Result: {status_str} (Score: {score:.1f}%)")
            print(f"{BOLD}======================================================={RESET}\n")

        summary = {
            "target": self.remote_repo or str(self.root),
            "project_type": self.project_type,
            "passed": is_passed,
            "score": round(score, 1),
            "total_checks": total,
            "passed_checks": passed,
            "warn_checks": warn,
            "failed_checks": fail,
            "strict": strict,
            "results": self.results,
        }
        return is_passed, summary


def main():
    parser = argparse.ArgumentParser(description="Audit a repository against the Mauro Quality Gate.")
    parser.add_argument("target", help="Path to local directory or GitHub repo (owner/repo)")
    parser.add_argument("--remote", action="store_true", help="Treat target as a remote GitHub repository")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if args.remote:
        repo = args.target
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            if not args.json:
                print(f"Cloning {repo} for audit...")
            subprocess.run(["gh", "repo", "clone", repo, tmpdir, "--", "--depth=1"], check=True, stdout=subprocess.DEVNULL if args.json else None)
            auditor = ProjectAuditor(Path(tmpdir), remote_repo=repo, quiet=args.json)
            passed, summary = auditor.run(strict=args.strict)
            if args.json:
                print(json.dumps(summary, indent=2))
            sys.exit(0 if passed else 1)
    else:
        path = Path(args.target)
        if not path.exists():
            print(f"Error: path {path} does not exist", file=sys.stderr)
            sys.exit(1)
        auditor = ProjectAuditor(path, quiet=args.json)
        passed, summary = auditor.run(strict=args.strict)
        if args.json:
            print(json.dumps(summary, indent=2))
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
