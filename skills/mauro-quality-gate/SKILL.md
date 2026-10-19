---
name: mauro-quality-gate
description: Standards, architecture, reusable CI/CD workflows, and testing conventions for general software projects (Tauri, TypeScript/Node, Rust, Python, Cloudflare Forge / OpenAPI) maintained by Mauro Druwel. Load when creating, reviewing, refactoring, or auditing software repositories.
---

# Mauro Quality Gate (MQG)

This skill governs the standards, architecture, testing, and CI/CD pipelines for all software repositories (desktop applications, full-stack web, libraries, CLIs, OpenAPI & Forge SDK generators, and Home Assistant / HACS integrations) maintained by **Mauro Druwel** (@MauroDruwel).

Authoritative central repository, reusable GitHub workflows, templates, and auditing CLI:
👉 **`https://github.com/MauroDruwel/quality-gate`**

---

## 1. The 7 Pillars of Mauro Quality Gate

| Pillar | Focus | Requirements |
|---|---|---|
| **1. Governance & Hygiene** | Open source cleanliness | README, MIT License (Mauro Druwel), CHANGELOG, .gitignore, no OS junk (`.DS_Store`) |
| **2. Architecture & Tooling** | Maintainable foundations | Modern archetypes (Tauri v2, Python CustomTkinter/Tkinter desktop & background services, TS + Vite, Cargo, pyproject.toml + ruff, Cloudflare Forge OpenAPI specs), committed lockfiles |
| **3. CI/CD & Automation** | Centralized reusable workflows | Push/PR validation, concurrency groups, cross-platform builds, matrix testing |
| **4. Type Safety & Strictness** | Zero-warning philosophy | Strict TypeScript (`noImplicitAny`), Rust `clippy -D warnings`, Python Ruff |
| **5. Testing & Verification** | Regression prevention | Unit + integration tests, high coverage of core business logic, automated CI runs |
| **6. Security & Releases** | Supply chain & distribution | Dependabot/lockfile checks, semantic version tags (`vX.Y.Z`), automated binary releases |
| **7. Home Assistant & HACS** | Core integration quality | Reauth flows, async event loop safety (SSL contexts), ConfigEntryAuthFailed/NotReady, Coordinator auth handling, timezone awareness, recent `min_ha_version`, hassfest + HACS CI actions |

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

## 3. Home Assistant & HACS Integration Standard (The "Frenck Checklist")

All Home Assistant integrations (`custom_components`) and client libraries must adhere to the core architectural requirements enforced during HACS default store reviews:

### A. Event Loop & Async Safety
1. **Never block the event loop**: Client libraries and integrations running inside Home Assistant must never execute blocking I/O (synchronous `requests`, disk reads, synchronous certificate loading) directly on the asyncio loop.
2. **Explicit SSL Context for WebSockets (`wss://`)**:
   - `websockets.connect(url)` on `wss://` without an `ssl=` parameter causes `asyncio` to create a default SSL context on every connect/reconnect, calling `SSLContext.load_default_certs()` synchronously from disk on the event loop (flagged by HA as a blocking call).
   - **Requirement**: Client libraries must accept `ssl: ssl.SSLContext | None = None` in their client constructor/connect methods. In the integration, pass `homeassistant.util.ssl.get_default_context()`.

### B. Startup & Error Handling (`async_setup_entry`)
1. **Never leak raw library exceptions**: All library exceptions during entry setup must be caught and translated.
2. **`ConfigEntryAuthFailed`**: If credentials/tokens are rejected on startup, catch `AuthenticationError` and raise `ConfigEntryAuthFailed(err)`. This triggers HA's reauthentication banner instead of failing silently or logging infinite retries.
3. **`ConfigEntryNotReady`**: If the cloud API or device is unreachable (timeouts, 502/503/504, connection refused), catch connection errors and raise `ConfigEntryNotReady(err)`. Home Assistant will automatically handle exponential backoff and retry loading.

### C. Mandatory Reauthentication Flow (`config_flow.py`)
1. Every integration storing credentials (username, password, API tokens) must implement:
   - `async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult`
   - `async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult`
2. On successful reauthentication, call:
   ```python
   return self.async_update_reload_and_abort(existing_entry, data={**existing_entry.data, **user_input})
   ```
3. Strings and translations (`strings.json` and `translations/*.json`) must include:
   - `config.step.reauth_confirm` (title, description, and data fields)
   - `config.abort.reauth_successful`

### D. DataUpdateCoordinator & Streaming State
1. **Polled Updates**: In `_async_update_data()`:
   - Catch `AuthenticationError` and raise `ConfigEntryAuthFailed(err)`.
   - Catch network errors and raise `UpdateFailed(err)`.
2. **WebSocket / Long-lived Streams**:
   - When a token renewal or authentication check fails mid-stream, do **not** catch `Exception` and loop forever with `sleep(5)`.
   - Surface the authentication failure or call `self.entry.async_start_reauth(self.hass)` immediately.

### E. Timezone Awareness
- Never hardcode timezones (e.g. `"Europe/Brussels"`) or assume fixed UTC day boundaries in energy calculations.
- Pass `hass.config.time_zone` to client libraries, and calculate day/month boundaries using `homeassistant.util.dt.now(time_zone)`.

### F. HACS Repository & Publishing Quality
1. **`hacs.json`**:
   - `name`: Human-readable component name.
   - `min_ha_version`: Must be recent (at most 6 months old, currently `>= 2024.11.0`).
2. **Mandatory CI Workflows**:
   - `.github/workflows/hacs.yml`: `hacs/action` with zero disabled checks.
   - `.github/workflows/hassfest.yml`: `home-assistant/actions/hassfest`.
3. **Catalog Submissions (`hacs/default`)**:
   - Ensure the `integration` catalog file remains strictly sorted alphabetically (`python scripts/is_sorted.py`).

### G. Integration Archetypes & Lessons Learned (Mauro's Integration Portfolio)
1. **Cloud REST + Auto-generated SDK (`Weathercloud-HA`)**:
   - Best practice: Generate async client libraries from OpenAPI specs using Cloudflare Forge to guarantee zero schema drift.
   - Use standard `DataUpdateCoordinator` with exponential backoff on HTTP 429/5xx errors.
2. **Local LAN Device Scraping (`SolarlogLegacyHA`)**:
   - Map unreachable local devices / timeouts to `UpdateFailed` so entities turn `unavailable` instead of crashing coordinator.
   - Routinely bump `min_ha_version` in `hacs.json` to keep pace with Home Assistant minor releases.
3. **Multi-device Cloud Portals (`SMA-ennexOS-cloud-HA`)**:
   - Multi-device topology: split inverters, batteries, and meters into distinct HA devices via `DeviceInfo(identifiers={...})`.
   - Never hardcode timezones (e.g. `"Europe/Brussels"`); always compute local day boundaries from `hass.config.time_zone`.
4. **Interactive 2FA Limitations & Anti-Patterns (`HeyTelecomHA`)**:
   - When an upstream API enforces interactive SMS/push 2FA with short (1h) token lifetimes and no persistent OAuth refresh token, background automation is infeasible.
   - Clearly document authentication limitations and pause broken integrations rather than implementing fragile workarounds.
5. **Real-time WebSockets & Streaming (`homewizard-cloud-ha`)**:
   - Always accept an explicit `ssl.SSLContext` in the client library to prevent blocking `SSLContext.load_default_certs` in the asyncio event loop.
   - Surface mid-stream authentication drops immediately via `entry.async_start_reauth(hass)` and break connection retry loops.

---

## 4. GitHub Metadata & Topic Conventions

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
