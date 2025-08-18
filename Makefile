.PHONY: all venv install-dev install test lint format typecheck docs-serve docs-build docs-deploy clean clean-all help

# ==============================================================================
# Variables
# ==============================================================================

PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
SRC_DIR := src

# ==============================================================================
# Default Target
# ==============================================================================

all: help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  help          Show this help message."
	@echo ""
	@echo "  --- Environment Setup ---"
	@echo "  venv          Create a Python virtual environment."
	@echo "  install-dev   Install package in editable mode with dev dependencies."
	@echo "  install       Install package in editable mode."
	@echo ""
	@echo "  --- Documentation ---"
	@echo "  docs-serve    Start the live-reloading documentation server."
	@echo "  docs-build    Build the static documentation site."
	@echo "  docs-deploy   Deploy the documentation to GitHub Pages."
	@echo ""
	@echo "  --- Quality & Testing ---"
	@echo "  test          Run all tests with pytest."
	@echo "  lint          Check code with ruff."
	@echo "  format        Format code with ruff."
	@echo "  typecheck     Run type checking with mypy."
	@echo ""
	@echo "  --- Housekeeping ---"
	@echo "  clean         Remove build artifacts and cache files."
	@echo "  clean-all     Remove venv, build artifacts, and cache files."
	@echo ""
	@echo "  --- PyPI Deployment ---"
	@echo "  build         Build distribution packages for PyPI."
	@echo "  publish-test  Publish to TestPyPI (for testing)."
	@echo "  publish       Publish to PyPI (requires authentication)."

# ==============================================================================
# Environment Setup
# ==============================================================================

venv:
	@echo "Creating Python virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@$(VENV_PIP) install --upgrade pip setuptools wheel
	@echo "Virtual environment created at $(VENV)"
	@echo "Activate with: source $(VENV)/bin/activate"

install-dev: venv
	@echo "Installing package in editable mode with dev dependencies..."
	@$(VENV_PIP) install -e .[dev]
	@echo "Installation complete."

install: venv
	@echo "Installing package in editable mode..."
	@$(VENV_PIP) install -e .
	@echo "Installation complete."

# ==============================================================================
# Documentation Tasks (MkDocs)
# ==============================================================================

docs-serve: venv
	@echo "Starting MkDocs development server..."
	@echo "View at: http://127.0.0.1:8000"
	@$(VENV_PYTHON) -m mkdocs serve

docs-build: venv
	@echo "Building documentation site..."
	@$(VENV_PYTHON) -m mkdocs build
	@echo "Site built in the 'site/' directory."

docs-deploy: docs-build
	@echo "Deploying documentation to GitHub Pages..."
	@$(VENV_PYTHON) -m mkdocs gh-deploy
	@echo "Deployment complete."

# ==============================================================================
# Quality Assurance
# ==============================================================================

test: venv
	@echo "Running tests with pytest..."
	@if [ -d "tests" ]; then \
		$(VENV_PYTHON) -m pytest tests -v; \
	else \
		echo "No tests directory found."; \
	fi

lint: venv
	@echo "Linting code with ruff..."
	@$(VENV_PYTHON) -m ruff check $(SRC_DIR)
	@echo "Linting complete."

format: venv
	@echo "Formatting code with ruff..."
	@$(VENV_PYTHON) -m ruff format $(SRC_DIR)
	@echo "Formatting complete."

typecheck: venv
	@echo "Running type checking with mypy..."
	@$(VENV_PYTHON) -m mypy $(SRC_DIR) --ignore-missing-imports
	@echo "Type checking complete."

# ==============================================================================
# Cleaning
# ==============================================================================

clean:
	@echo "Cleaning up build artifacts and cache files..."
	@rm -rf site dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@echo "Clean complete."

clean-all: clean
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "Full clean complete."

# ==============================================================================
# PyPI Deployment
# ==============================================================================

build: clean venv
	@echo "Building distribution packages..."
	@$(VENV_PIP) install --upgrade build
	@$(VENV_PYTHON) -m build
	@echo "Build complete. Packages in dist/"

publish-test: build
	@echo "Publishing to TestPyPI..."
	@$(VENV_PIP) install --upgrade twine
	@$(VENV_PYTHON) -m twine upload --repository testpypi dist/*
	@echo "Published to TestPyPI."
	@echo "Test with: pip install --index-url https://test.pypi.org/simple/ dotsuite"

publish: build
	@echo "Publishing to PyPI..."
	@echo "WARNING: This will publish to the real PyPI!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || (echo "Aborted." && exit 1)
	@$(VENV_PIP) install --upgrade twine
	@$(VENV_PYTHON) -m twine upload dist/*
	@echo "Published to PyPI."
	@echo "Install with: pip install dotsuite"
