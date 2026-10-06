---
name: mauro-quality-gate
description: Standards, architecture, reusable CI/CD workflows, and testing conventions for general software projects (Tauri, TypeScript/Node, Rust, Python, Cloudflare Forge / OpenAPI) maintained by Mauro Druwel. Load when creating, reviewing, refactoring, or auditing software repositories.
---

# Mauro Quality Gate (MQG)

This skill governs the standards, architecture, testing, and CI/CD pipelines for all non-Home Assistant software repositories (desktop applications, full-stack web, libraries, CLIs, OpenAPI & Forge SDK generators) maintained by **Mauro Druwel** (@MauroDruwel).

Authoritative central repository, reusable GitHub workflows, templates, and auditing CLI:
👉 **`https://github.com/MauroDruwel/quality-gate`**

---

## 1. The 6 Pillars of Mauro Quality Gate

| Pillar | Focus | Requirements |
|---|---|---|
| **1. Governance & Hygiene** | Open source cleanliness | README, MIT License (Mauro Druwel), CHANGELOG, .gitignore, no OS junk (`.DS_Store`) |
| **2. Architecture & Tooling** | Maintainable foundations | Modern archetypes (Tauri v2, Python CustomTkinter/Tkinter desktop & background services, TS + Vite, Cargo, pyproject.toml + ruff, Cloudflare Forge OpenAPI specs), committed lockfiles |
| **3. CI/CD & Automation** | Centralized reusable workflows | Push/PR validation, concurrency groups, cross-platform builds, matrix testing |
| **4. Type Safety & Strictness** | Zero-warning philosophy | Strict TypeScript (`noImplicitAny`), Rust `clippy -D warnings`, Python Ruff |
| **5. Testing & Verification** | Regression prevention | Unit + integration tests, high coverage of core business logic, automated CI runs |
| **6. Security & Releases** | Supply chain & distribution | Dependabot/lockfile checks, semantic version tags (`vX.Y.Z`), automated binary releases |

---

## 2. Centralized Reusable CI/CD Pipelines

All repositories reuse centralized workflows from `MauroDruwel/quality-gate/.github/workflows/` via GitHub Actions `workflow_call`:

- **`tauri-ci.yml`**: Full frontend lint/test/typecheck + Rust cargo clippy/test/build.
- **`tauri-release.yml`**: Multi-platform matrix build (macOS arm64, Windows x64, Linux x64) creating GitHub releases with cross-platform bundles.
- **`typescript-ci.yml`**: Node/pnpm test, lint, tsc typecheck, and production bundle.
- **`python-ci.yml`**: Python 3.11-3.13 matrix, ruff format/lint, and pytest.
- **`forge-ci.yml`**: OpenAPI 3.x schema validation, Cloudflare Forge SDK generation, zero-drift check (`git diff --exit-code`), and target SDK verification (Rust, Python, TypeScript).

### Example Caller Workflows

#### Tauri Application (`.github/workflows/ci.yml`)
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

#### TypeScript / Web Project (`.github/workflows/ci.yml`)
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
  typescript-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/typescript-ci.yml@main
    with:
      node-version: '22'
      package-manager: 'pnpm'
      run-tests: true
      run-build: true
      strict: true
```

#### Python Library / CLI (`.github/workflows/ci.yml`)
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
  python-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/python-ci.yml@main
    with:
      python-version: '3.12'
      run-tests: true
      run-lint: true
      run-format: true
      strict: true
```

#### Cloudflare Forge & OpenAPI Project (`.github/workflows/ci.yml`)
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
  forge-ci:
    uses: MauroDruwel/quality-gate/.github/workflows/forge-ci.yml@main
    with:
      spec-path: 'docs/openapi.yaml'
      validate-spec: true
      check-drift: true
      run-python-checks: true
      run-rust-checks: true
      run-typescript-checks: true
```

---

## 3. GitHub Metadata & Topic Conventions

Do not overload repositories with dozens of tags. Follow focused tagging:

- Desktop / Tauri: `tauri`, `rust`, `typescript`, `desktop-app`
- Web / Tools: `typescript`, `react` (or framework), `developer-tools`
- Cloudflare Forge / OpenAPI: `forge`, `openapi`, `sdk-generator`, `api-client`
- Quality Gate: `quality-gate`, `engineering-standards`, `ci-cd`

Always set:
- Clean GitHub description (< 100 characters, clear summary).
- Homepage URL (e.g. `https://maurodruwel.be` or documentation URL).

---

## 4. Automated Project Auditor

To audit any project locally or remotely against these rules:

```bash
# Audit current directory
python /path/to/quality-gate/scripts/audit_project.py .

# Output machine-readable JSON
python /path/to/quality-gate/scripts/audit_project.py . --json

# Strict mode (warnings count as failures)
python /path/to/quality-gate/scripts/audit_project.py . --strict

# Audit remote GitHub repo
python /path/to/quality-gate/scripts/audit_project.py MauroDruwel/TunnelDashDesktop --remote
```
