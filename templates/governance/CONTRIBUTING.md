# Contributing to [Project Name]

Thank you for your interest in contributing! This project adheres to the **[Mauro Quality Gate (MQG)](https://github.com/MauroDruwel/quality-gate)** standards for software quality, architecture, and developer experience.

---

## 🛠️ Development Workflow

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/MauroDruwel/[REPO_NAME].git
   cd [REPO_NAME]
   ```

2. **Branching**:
   - Always branch off `main`.
   - Use descriptive branch names with conventional prefixes:
     - `feat/feature-name`
     - `fix/bug-name`
     - `docs/documentation-update`
     - `refactor/clean-architecture`

3. **Install Dependencies & Verify Local Setup**:
   - Use the pinned package manager (e.g. `pnpm install`, `cargo check`, or `pip install -e ".[test]"`).
   - Verify that your local environment passes all tests before making edits.

---

## 📐 Quality Standards & Conventions

All pull requests must satisfy the following criteria:

- **Type Safety**: No untyped `any` in TypeScript or unannotated public functions in Python/Rust.
- **Linters & Formatting**: Zero warnings or errors in ESLint, Biome, Clippy, or Ruff.
- **Tests**:
  - Every bug fix should include a regression test.
  - Every new feature must include accompanying unit/integration tests.
  - All tests must pass locally prior to submitting the PR.
- **Git Hygiene**:
  - Do not commit OS-specific files (`.DS_Store`, `Thumbs.db`, editor workspaces).
  - Use conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
  - Keep pull requests focused on a single change or objective.

---

## 🧪 Pre-PR Checklist

Before opening a pull request, run:

```bash
# Frontend / TypeScript
pnpm lint
pnpm test
pnpm build

# Rust / Tauri Core (if applicable)
cargo clippy --all-targets --all-features -- -D warnings
cargo test

# Python (if applicable)
ruff check .
ruff format --check .
pytest

# MQG Audit
python /path/to/quality-gate/scripts/audit_project.py .
```

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
