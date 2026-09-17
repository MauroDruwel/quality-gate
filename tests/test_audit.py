"""Tests for the Mauro Quality Gate audit tool."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts.audit_project import ProjectAuditor


class TestProjectAuditor(unittest.TestCase):
    def test_detect_tauri(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            tauri_dir = tmppath / "src-tauri"
            tauri_dir.mkdir()
            (tauri_dir / "tauri.conf.json").write_text("{}")
            auditor = ProjectAuditor(tmppath, quiet=True)
            self.assertEqual(auditor.detect_project_type(), "tauri")

    def test_detect_typescript(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            (tmppath / "package.json").write_text("{}")
            auditor = ProjectAuditor(tmppath, quiet=True)
            self.assertEqual(auditor.detect_project_type(), "typescript")

    def test_detect_python(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            (tmppath / "pyproject.toml").write_text("[project]\nname='foo'")
            auditor = ProjectAuditor(tmppath, quiet=True)
            self.assertEqual(auditor.detect_project_type(), "python")

    def test_audit_governance_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            (tmppath / "README.md").write_text("# Test Project\n" + "x" * 120)
            (tmppath / "LICENSE").write_text("MIT License\nCopyright (c) 2026 Mauro Druwel")
            (tmppath / ".gitignore").write_text("node_modules/\n")
            (tmppath / "CHANGELOG.md").write_text("# Changelog\n")
            
            auditor = ProjectAuditor(tmppath, quiet=True)
            auditor.audit_governance()
            
            # All 5 checks should have passed
            self.assertEqual(len(auditor.results), 5)
            self.assertTrue(all(r["passed"] for r in auditor.results))

    def test_cli_json_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmppath = Path(tmp)
            (tmppath / "README.md").write_text("# Sample\n" + "x" * 150)
            (tmppath / "LICENSE").write_text("MIT License Copyright (c) 2026 Mauro Druwel")
            (tmppath / ".gitignore").write_text("*.log\n")
            
            proc = subprocess.run(
                [sys.executable, "scripts/audit_project.py", str(tmppath), "--json"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent)
            )
            # Exit code may be 0 or 1 depending on missing workflows/tests, but JSON must parse
            data = json.loads(proc.stdout)
            self.assertIn("score", data)
            self.assertIn("results", data)
            self.assertEqual(data["project_type"], "generic")


if __name__ == "__main__":
    unittest.main()
