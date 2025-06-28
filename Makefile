.PHONY: all docs-serve docs-build docs-deploy submodules install test lint clean help

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
	@echo "  --- Documentation ---"
	@echo "  docs-serve    Start the live-reloading documentation server."
	@echo "  docs-build    Build the static documentation site."
	@echo "  docs-deploy   Deploy the documentation to GitHub Pages."
	@echo ""
	@echo "  --- Project & Dependencies ---"
	@echo "  install       Install all 'dot' packages in editable mode."
	@echo "  submodules    Initialize and update git submodules."
	@echo ""
	@echo "  --- Quality & Testing ---"
	@echo "  test          Run tests for all 'dot' packages."
	@echo "  lint          Lint all 'dot' packages with ruff."
	@echo ""
	@echo "  --- Housekeeping ---"
	@echo "  clean         Remove build artifacts and cache files."

# ==============================================================================
# Documentation Tasks (MkDocs)
# ==============================================================================

docs-serve:
	@echo "Starting MkDocs development server..."
	@echo "View at: http://127.0.0.1:8000"
	mkdocs serve

docs-build:
	@echo "Building documentation site..."
	mkdocs build
	@echo "Site built in the 'site/' directory."

docs-deploy: docs-build
	@echo "Deploying documentation to GitHub Pages..."
	mkdocs gh-deploy
	@echo "Deployment complete."

# ==============================================================================
# Project Setup & Dependency Management
# ==============================================================================

submodules:
	@echo "Syncing submodule configuration..."
	git submodule sync
	@echo "Initializing and updating Git submodules (non-recursive)..."
	git submodule update --init

install: submodules
	@echo "Installing all 'dot' packages in editable mode..."
	@for dir in packages/*; do \
		if [ -d "$$dir" ] && [ -f "$$dir/pyproject.toml" ]; then \
			(echo "--> Installing $$dir" && cd "$$dir" && pip install --quiet -e .); \
		fi; \
	done
	@echo "Installation complete."

# ==============================================================================
# Quality Assurance
# ==============================================================================

test:
	@echo "Running tests for all 'dot' packages..."
	@for dir in packages/*; do \
		if [ -d "$$dir" ] && [ -d "$$dir/tests" ]; then \
			(echo "--> Testing $$dir" && cd "$$dir" && pytest); \
		fi; \
	done
	@echo "Testing complete."

lint:
	@echo "Linting all 'dot' packages with ruff..."
	python -m ruff check packages
	@echo "Linting complete."

# ==============================================================================
# Cleaning
# ==============================================================================

clean:
	@echo "Cleaning up build artifacts and cache files..."
	rm -rf site
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete."
