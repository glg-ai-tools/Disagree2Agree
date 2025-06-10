# Disagree2Agree Scaffold

This directory contains the canonical project scaffold for Disagree2Agree, following best practices for modular Python projects.

## Structure

- `src/` — All source code
- `tests/` — Unit/integration tests, mirrors `src/`
- `notebooks/` — Data exploration, analysis (optional)
- `docker/` — Dockerfiles for dev and deployment
- `gcp/` — Cloud configs, Terraform, etc.
- `rpi/` — Raspberry Pi-specific scripts/configs
- `scripts/` — Automation and deployment scripts
- `.vscode/` — Editor settings
- `.github/` — GitHub Actions workflows

See `docs/02-Directory_Structure_Guide.md` for details.

# Move all source code into the canonical src/ scaffold
# - agents/ → src/agents/
# - app/ → src/app/
# - config/ → src/config/
# - main.py, app.py, debate_cli.py → src/ (if they are entry points)
# - templates/ → src/templates/
# - migrations/ → src/migrations/

# This is a placeholder to document the planned move. Actual file moves will be performed next.
