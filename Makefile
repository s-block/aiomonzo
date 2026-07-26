.PHONY: help install install-dev pre-commit-install format format-check lint type-check test test-cov build check-dist check clean
.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

install: ## Install locked production dependencies
	uv sync --no-dev --frozen

install-dev: ## Install locked development dependencies
	uv sync --dev --frozen

pre-commit-install: ## Install the repository pre-commit hooks
	uv run pre-commit install

format: ## Apply Ruff formatting and safe lint fixes
	uv run ruff check --fix .
	uv run ruff format .

format-check: ## Check formatting without changing files
	uv run ruff format --check .

lint: ## Run Ruff lint checks
	uv run ruff check .

type-check: ## Type-check source, tests, and package scripts
	uv run mypy src/aiomonzo tests scripts

test: ## Run the test suite
	uv run pytest -v

test-cov: ## Run tests with terminal coverage
	uv run coverage run -m pytest -v
	uv run coverage report --show-missing

build: ## Build source and wheel distributions
	uv build

check-dist: clean build ## Validate metadata, package contents, and isolated wheel import
	uv run twine check dist/*
	uv run python scripts/check_dist.py

check: format-check lint type-check test check-dist ## Run all required package checks

clean: ## Remove generated local build and test artifacts
	uv run python -c "import shutil; [shutil.rmtree(path, ignore_errors=True) for path in ('build', 'dist', '.mypy_cache', '.pytest_cache', '.ruff_cache', 'htmlcov')]"
