# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based todo backend application currently in early development stages.

**Tech Stack:**
- Python 3.12.11+
- No external dependencies yet (empty dependencies list in pyproject.toml)
- Uses `uv` for Python package management (evidenced by pyproject.toml structure)

## Development Commands

**Run the application:**
```bash
python main.py
```

**Install dependencies (when added):**
```bash
uv sync
```

**Activate virtual environment:**
```bash
source .venv/bin/activate  # On Unix/macOS
```

## Architecture Notes

Currently minimal architecture:
- `main.py` - Entry point with a basic main() function
- Project uses pyproject.toml for dependency management
- Python version pinned via `.python-version` file

The codebase is in its initial phase and will need to be expanded with:
- Web framework (e.g., FastAPI, Flask, Django)
- Database layer
- API endpoints for todo operations
- Data models
