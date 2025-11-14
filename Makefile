.PHONY: help install dev test test-cov lint format type-check clean db-up db-down db-reset migrate migrate-auto migrate-down migrate-history run shell

# Default target
help:
	@echo "Todo Backend API - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install all dependencies"
	@echo "  make dev              Install dev dependencies and setup pre-commit"
	@echo ""
	@echo "Database:"
	@echo "  make db-up            Start PostgreSQL container"
	@echo "  make db-down          Stop PostgreSQL container"
	@echo "  make db-reset         Reset database (drop and recreate)"
	@echo "  make db-test          Test database connection"
	@echo ""
	@echo "Migrations:"
	@echo "  make migrate          Apply all pending migrations"
	@echo "  make migrate-auto     Create new migration (autogenerate)"
	@echo "  make migrate-down     Rollback last migration"
	@echo "  make migrate-history  Show migration history"
	@echo "  make migrate-current  Show current migration version"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make test-watch       Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linter (ruff check)"
	@echo "  make format           Format code (ruff format)"
	@echo "  make type-check       Run type checker (mypy)"
	@echo "  make check            Run all checks (lint + format + type)"
	@echo ""
	@echo "Development:"
	@echo "  make run              Start development server"
	@echo "  make shell            Open Python shell with app context"
	@echo "  make clean            Remove cache and temp files"
	@echo ""

# Installation
install:
	uv sync

dev: install
	@echo "Development environment ready!"

# Database
db-up:
	docker compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	@make db-test

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	@make db-test
	@make migrate

db-test:
	uv run python test_db_connection.py

# Migrations
migrate:
	uv run alembic upgrade head

migrate-auto:
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

migrate-down:
	uv run alembic downgrade -1

migrate-history:
	uv run alembic history

migrate-current:
	uv run alembic current

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html

test-watch:
	uv run pytest-watch

# Code Quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

type-check:
	uv run mypy src

check: lint type-check
	@echo "✓ All checks passed!"

# Development
run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

shell:
	uv run python

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	@echo "✓ Cleaned up cache and temp files"
