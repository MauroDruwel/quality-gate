# Changelog

All notable changes to the Mauro Quality Gate (MQG) specification and tooling will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-17

### Added
- Initial release of the **Mauro Quality Gate (MQG)** for general software projects (desktop apps, full-stack web, libraries, CLIs).
- Centralized reusable GitHub Actions workflows:
  - `tauri-ci.yml`: Frontend lint/test + Rust clippy/test/build.
  - `tauri-release.yml`: Multi-platform matrix release builder (macOS arm64, Windows x64, Linux x64).
  - `typescript-ci.yml`: Matrix Node testing, linting, typechecking, and production builds.
  - `python-ci.yml`: Modern Python 3.11-3.13 matrix, ruff check/format, and pytest.
- Automated CLI auditor (`scripts/audit_project.py`) with support for local directories, remote GitHub repositories, `--json` structured output, and `--strict` evaluation.
- Comprehensive starter templates in `templates/`:
  - `governance/`: README, CONTRIBUTING, SECURITY, CHANGELOG, .editorconfig, .gitignore.
  - `tauri/`, `typescript/`, `python/`: Drop-in caller workflows.
- AI Agent Skill (`skills/mauro-quality-gate/SKILL.md`) for Antigravity, Cursor, and Copilot.
- Full unit test suite for the auditing tool (`tests/test_audit.py`).
