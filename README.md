# Mauro Quality Gate (MQG)

[![Mauro Quality Gate](https://img.shields.io/badge/Mauro%20Quality%20Gate-Passed-2ea44f?style=flat&logo=github)](https://github.com/MauroDruwel/quality-gate)
[![CI](https://github.com/MauroDruwel/quality-gate/actions/workflows/ci.yml/badge.svg)](https://github.com/MauroDruwel/quality-gate/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Author: Mauro Druwel](https://img.shields.io/badge/Author-Mauro%20Druwel-orange)](https://maurodruwel.be)

The canonical software quality standards, architectural conventions, centralized CI/CD workflows, and automated auditing tool for general software projects authored and maintained by **Mauro Druwel** (@MauroDruwel).

> **Note:** For Home Assistant custom integration components, see the specialized counterpart: **[`MauroDruwel/ha-quality-gate`](https://github.com/MauroDruwel/ha-quality-gate)**.

---

## 🏛️ The 6 Pillars of Mauro Quality Gate

```
                  ┌─────────────────────────────────────────┐
                  │       Mauro Quality Gate (MQG)          │
                  └────────────────────┬────────────────────┘
         ┌───────────────┬─────────────┼─────────────┬───────────────┐
         ▼               ▼             ▼             ▼               ▼
   [Governance]    [Architecture]   [CI/CD]    [Type Safety]     [Testing]
   Clean OSS &     Tauri / Vite /  Central     Zero-warning      Automated
   Attribution     Cargo / Modern  Workflows   Typechecks        Coverage
```

| Pillar | Focus | Requirements |
|---|---|---|
| **1. Governance & Hygiene** | Open source cleanliness | Valid `README.md`, `LICENSE` (MIT © Mauro Druwel), `CHANGELOG.md`, `.github/pull_request_template.md`, comprehensive `.gitignore`, zero OS artifacts (`.DS_Store`). |
| **2. Architecture & Tooling** | Robust foundation | Modern archetypes (Tauri v2 desktop, Python CustomTkinter / Tkinter desktop & background service daemons, TypeScript/Vite frontend, Rust Cargo, modern Python pyproject.toml), strictly committed lockfiles (`pnpm-lock.yaml`, `Cargo.lock`). |
| **3. CI/CD & Automation** | Reusable central pipelines | Reusable GitHub Actions with concurrency cancellation, cross-platform matrix builds, and push/PR validation. |
| **4. Type Safety & Strictness** | Zero-warning philosophy | Strict TypeScript (`tsc --noEmit`), Rust `cargo clippy -- -D warnings`, Python Ruff formatting & linting. |
| **5. Testing & Verification** | Regression prevention | Automated unit & integration test suites, fast feedback, automated runs in CI. |
| **6. Security & Releases** | Supply chain & delivery | Private vulnerability reporting policy, semantic versioning (`v*`), multi-platform binary compilation. |

---

## 🔄 Centralized Reusable Workflows

All repositories inherit centralized, maintained pipelines via GitHub Actions `workflow_call`:

| Workflow | File | Capabilities |
|---|---|---|
| **Tauri CI** | `.github/workflows/tauri-ci.yml` | Node & Rust setup, pnpm cache, ESLint, TypeScript typecheck, frontend tests, Cargo clippy, Cargo test, release dry-run. |
| **Tauri Release** | `.github/workflows/tauri-release.yml` | Multi-platform matrix build (`macos-14` arm64, `windows-latest` x64, `ubuntu-22.04` x64), package signing, DMG/MSI/AppImage bundle generation, automated GitHub Release. |
| **TypeScript CI** | `.github/workflows/typescript-ci.yml` | Matrix Node.js (20, 22), pnpm/npm caching, ESLint, TypeScript typecheck, Vitest/Jest execution, production build verification. |
| **Python CI** | `.github/workflows/python-ci.yml` | Matrix Python (3.11, 3.12, 3.13), Ruff formatting and linting, and Pytest test execution. |
| **Cloudflare Forge & OpenAPI CI** | `.github/workflows/forge-ci.yml` | OpenAPI 3.x schema validation, Cloudflare Forge SDK generation, zero-drift check (`git diff --exit-code`), and target SDK verification (Rust, Python, TypeScript). |

### How to Use in Your Repository

Add a minimal caller workflow in `.github/workflows/ci.yml`:

#### Tauri Desktop Application
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  tauri-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/tauri-ci.yml@main
    with:
      node-version: '22'
      package-manager: 'pnpm'
      run-cargo-test: true
      run-frontend-test: true
      strict: true
```

#### TypeScript / Web Project
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  typescript-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/typescript-ci.yml@main
    with:
      node-version: '22'
      package-manager: 'pnpm'
```

#### Python Project
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  python-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/python-ci.yml@main
    with:
      python-version: '3.12'
```

#### Cloudflare Forge & OpenAPI Project
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  forge-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/forge-ci.yml@main
    with:
      spec-path: 'docs/openapi.yaml'
      validate-spec: true
      check-drift: true
```

---

## 🔍 Automated Quality Gate Audit Tool

This repository includes a Python CLI to audit any local directory or remote GitHub repository against all MQG standards:

```bash
# Audit a local project directory
python scripts/audit_project.py /path/to/project

# Audit current directory with machine-readable JSON output
python scripts/audit_project.py . --json

# Strict mode: treats warnings as failures
python scripts/audit_project.py . --strict

# Audit a remote repository on GitHub
python scripts/audit_project.py MauroDruwel/TunnelDashDesktop --remote
```

### Sample Audit Output

```text
=======================================================
   MAURO QUALITY GATE AUDIT: TunnelDashDesktop
   Detected Project Archetype: TAURI
=======================================================

[1. GOVERNANCE & REPOSITORY HYGIENE]
  ✅ PASS   README.md present                  Size: 13728 bytes
  ✅ PASS   LICENSE (MIT © Mauro Druwel)       MIT © Mauro Druwel
  ✅ PASS   CHANGELOG.md present               Exists
  ✅ PASS   .gitignore present                 Exists
  ✅ PASS   No .DS_Store files present         Clean

[2. ARCHITECTURE & TOOLING (TAURI)]
  ✅ PASS   src-tauri directory present        Tauri backend
  ✅ PASS   Rust Cargo.toml present            Dependencies
  ✅ PASS   package.json present               Frontend app
  ✅ PASS   Frontend lockfile committed        pnpm or npm lockfile
  ✅ PASS   Cargo.lock committed               Rust lockfile
  ✅ PASS   ESLint configuration present       Frontend linter

[3. CI/CD AUTOMATION & WORKFLOWS]
  ✅ PASS   .github/workflows directory        CI pipelines
  ✅ PASS   Active workflow pipelines          Found 4 workflow(s)
  ✅ PASS   Uses Mauro Quality Gate actions    Reusing centralized MQG workflows

[4. AUTOMATED TESTS & VERIFICATION]
  ✅ PASS   Test suite present                 Found 3 frontend test file(s) + Cargo unit tests

-------------------------------------------------------
  Total Checks: 15 | Passed: 15 | Warn: 0 | Fail: 0
  Result: PASSED QUALITY GATE (Score: 100.0%)
=======================================================
```

---

## 📦 Starter Templates

The `templates/` folder provides ready-to-use boilerplate for new or upgraded projects:

- **`templates/governance/`**:
  - `README.md` — Canonical project documentation template with badges.
  - `CONTRIBUTING.md` — Development workflow, branching conventions, and pre-PR checklist.
  - `SECURITY.md` — Vulnerability disclosure policy.
  - `CHANGELOG.md` — Standard Keep a Changelog format.
  - `.gitignore` — Universal multi-language ignore rules (Node, Rust, Python, OS artifacts).
  - `.editorconfig` — Consistent indentation and file formatting.
- **`templates/tauri/`**: Drop-in `ci.yml` and `release.yml` caller workflows.
- **`templates/typescript/`**: Drop-in `ci.yml` caller workflow.
- **`templates/python/`**: Drop-in `ci.yml` caller workflow.

---

## 🤖 AI Agent Skill (Antigravity, Cursor, Copilot)

This repository includes a standardized agent skill (`skills/mauro-quality-gate/SKILL.md`) that equips coding assistants with full context of Mauro's architectural requirements, zero-warning standards, and CI/CD rules.

To install or sync this skill into your local AI workspace:

```bash
# Global Antigravity discovery
mkdir -p ~/.gemini/config/skills/mauro-quality-gate
cp skills/mauro-quality-gate/SKILL.md ~/.gemini/config/skills/mauro-quality-gate/SKILL.md

# Workspace-level discovery
mkdir -p .agents/skills/mauro-quality-gate
cp skills/mauro-quality-gate/SKILL.md .agents/skills/mauro-quality-gate/SKILL.md
```

---

## 📄 License

MIT © [Mauro Druwel](https://maurodruwel.be)
