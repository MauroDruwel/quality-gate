"""Tests for reusable workflow definitions and starter templates."""

import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "docs-check.yml"
DOCS_TEMPLATE = REPO_ROOT / "templates" / "docs" / "docs-check.yml"


def _extract_inventory_script(workflow_text: str) -> str:
    """Extract the embedded Python inventory script from docs-check.yml."""
    match = re.search(
        r"python3 - <<'PYEOF'\n(.*?)\n\s*PYEOF",
        workflow_text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError("Could not locate embedded Python inventory script in docs-check.yml")
    return textwrap.dedent(match.group(1))


class TestDocsCheckWorkflow(unittest.TestCase):
    def test_docs_check_workflow_structure(self):
        text = DOCS_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_call:", text)
        for required_input in [
            "mode:",
            "docs-paths:",
            "source-paths:",
            "base-branch:",
            "branch-name:",
            "model-endpoint:",
            "model:",
            "use-github-token:",
            "fail-on-gaps:",
            "extra-instructions:",
            "share:",
        ]:
            self.assertIn(required_input, text)

        for required_perm in [
            "id-token: write",
            "contents: write",
            "pull-requests: write",
            "issues: write",
        ]:
            self.assertIn(required_perm, text)

        self.assertIn("anomalyco/opencode/github@latest", text)
        self.assertIn("https://maurodruwel.be/ai/default", text)
        self.assertIn("GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}", text)
        # Reserved GITHUB_TOKEN must not be declared under workflow_call.secrets
        self.assertIsNone(re.search(r"^\s+secrets:\s*$", text, re.MULTILINE))
        # Fork PR safety guard
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", text)
        # Avoid /tmp reads/writes that trigger OpenCode external_directory ask prompts
        self.assertNotIn("/tmp/", text)
        self.assertIn(".mqg-docs-inventory.md", text)
        # Ensure agent is instructed to update code snippets and add real examples, not prose-only caveats
        self.assertIn("Rewrite Broken or Incomplete Code Snippets Directly", text)
        self.assertIn("Ensure Real, End-to-End Examples", text)

    def test_docs_check_template_references_quality_gate(self):
        text = DOCS_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("MauroDruwel/quality-gate/.github/workflows/docs-check.yml@main", text)
        for required_perm in [
            "id-token: write",
            "contents: write",
            "pull-requests: write",
            "issues: write",
        ]:
            self.assertIn(required_perm, text)

    def test_embedded_inventory_script_scans_python_and_ts_projects(self):
        workflow_text = DOCS_WORKFLOW.read_text(encoding="utf-8")
        script = _extract_inventory_script(workflow_text)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "mypkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text(
                'from .auth import login, set_auth\n'
                '__all__ = ["login", "set_auth"]\n',
                encoding="utf-8",
            )
            (pkg / "auth.py").write_text(
                "import os\n"
                "from dataclasses import dataclass\n"
                "class BaseError(Exception):\n"
                "    pass\n"
                "class AuthError(BaseError):\n"
                "    pass\n"
                "@dataclass\n"
                "class UserProfile:\n"
                "    email: str\n"
                "    @property\n"
                "    def domain(self) -> str:\n"
                "        return self.email.split('@')[-1]\n"
                "def login(user: str, password: str) -> bool:\n"
                "    _ = os.environ.get('MYPKG_USER')\n"
                "    _ = os.getenv('MYPKG_EMAIL')\n"
                "    return True\n"
                "def set_auth(token: str) -> None:\n"
                "    pass\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                '[project]\nname = "mypkg"\nversion = "0.3.0"\nrequires-python = ">=3.10"\n',
                encoding="utf-8",
            )
            (root / "README.md").write_text("# MyPkg\n\n```python\nprint('hi')\n```\n", encoding="utf-8")
            docs_pages = root / "docs" / "pages"
            docs_pages.mkdir(parents=True)
            (docs_pages / "quick-start.mdx").write_text("# Quick Start\n", encoding="utf-8")
            (docs_pages / "theme.config.tsx").write_text(
                "export const ignoredThemeConfig = true;\n", encoding="utf-8"
            )

            web_src = root / "src"
            web_src.mkdir()
            (web_src / "client.ts").write_text(
                "export async function fetchStatus() { return process.env.PUBLIC_API_URL; }\n",
                encoding="utf-8",
            )

            inventory_path = root / ".mqg-docs-inventory.md"
            env = os.environ.copy()
            env["DOCS_PATHS"] = "README.md,docs"
            env["SOURCE_PATHS"] = ""
            env["BASE_BRANCH"] = "main"
            env["EVENT_NAME"] = "workflow_dispatch"
            env["INVENTORY_OUTPUT"] = str(inventory_path)

            proc = subprocess.run(
                [sys.executable, "-c", script],
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)

            inventory = inventory_path.read_text(encoding="utf-8")
            self.assertIn("`README.md`", inventory)
            self.assertIn("1 headings, 1 code blocks", inventory)
            self.assertIn("`docs/pages/quick-start.mdx`", inventory)
            self.assertIn('requires-python=>=3.10', inventory)
            self.assertIn("`MYPKG_USER`", inventory)
            self.assertIn("`MYPKG_EMAIL`", inventory)
            self.assertIn("`PUBLIC_API_URL`", inventory)
            self.assertIn("`login`", inventory)
            self.assertIn("`set_auth`", inventory)
            self.assertIn("class AuthError(BaseError)", inventory)
            self.assertIn("class UserProfile: attrs=[email, @property domain]", inventory)
            self.assertIn("`fetchStatus`", inventory)
            # Docs folder TS/JS config should be excluded from auto-detected source exports
            self.assertNotIn("ignoredThemeConfig", inventory)


if __name__ == "__main__":
    unittest.main()
