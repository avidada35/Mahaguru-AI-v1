.PHONY: test test-unit test-integration test-e2e test-cov test-html lint format check-types check-style check-all ci-test ci-lint ci-format ci-check-types ci-check-style ci-check-all

# Variables
PYTHON = python3.11
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest
COVERAGE = $(PYTHON) -m coverage
BLACK = $(PYTHON) -m black
ISORT = $(PYTHON) -m isort
FLAKE8 = $(PYTHON) -m flake8
MYPY = $(PYTHON) -m mypy
PYTEST_OPTS = -v --color=yes --tb=short --showlocals
COV_OPTS = --cov=app --cov-report=term-missing --cov-report=html:htmlcov

# Install dependencies
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt

# Run all tests
test:
	$(PYTEST) $(PYTEST_OPTS) $(COV_OPTS) tests/

# Run unit tests
test-unit:
	$(PYTEST) $(PYTEST_OPTS) -m "unit" tests/unit/

# Run integration tests
test-integration:
	$(PYTEST) $(PYTEST_OPTS) -m "integration" tests/integration/

# Run end-to-end tests
test-e2e:
	$(PYTEST) $(PYTEST_OPTS) -m "e2e" tests/e2e/

# Run tests with coverage report
test-cov:
	$(PYTEST) $(PYTEST_OPTS) $(COV_OPTS) tests/

# Generate HTML coverage report
test-html:
	$(PYTEST) $(PYTEST_OPTS) $(COV_OPTS) --cov-report=html:htmlcov tests/
	@echo "Coverage report generated at htmlcov/index.html"

# Lint the code
lint:
	$(FLAKE8) app/ tests/

# Format the code
format:
	$(BLACK) app/ tests/
	$(ISORT) app/ tests/

# Check types
check-types:
	$(MYPY) app/ tests/

# Check code style
check-style:
	$(BLACK) --check app/ tests/
	$(ISORT) --check-only app/ tests/
	$(FLAKE8) app/ tests/

# Run all checks
check-all: check-style check-types test

# CI test target
ci-test:
	$(PYTEST) $(PYTEST_OPTS) --cov=app --cov-report=xml:coverage.xml --junitxml=junit/test-results.xml tests/

# CI lint target
ci-lint:
	$(FLAKE8) app/ tests/

# CI format check target
ci-format:
	$(BLACK) --check app/ tests/
	$(ISORT) --check-only app/ tests/

# CI type check target
ci-check-types:
	$(MYPY) app/ tests/

# CI style check target
ci-check-style:
	$(FLAKE8) app/ tests/

# Run all CI checks
ci-check-all: ci-format ci-lint ci-check-types ci-test

# Clean up
clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	rm -rf .coverage coverage.xml htmlcov/ junit/ .mypy_cache/ .pytest_cache/ .ruff_cache/

# Help
default: help
help:
	@echo "Available targets:"
	@echo "  install         Install all dependencies"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-e2e        Run end-to-end tests"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  test-html       Generate HTML coverage report"
	@echo "  lint            Run linter"
	@echo "  format          Format the code"
	@echo "  check-types     Run type checker"
	@echo "  check-style     Check code style"
	@echo "  check-all       Run all checks"
	@echo "  ci-test         Run tests in CI mode"
	@echo "  ci-lint         Run linter in CI mode"
	@echo "  ci-format       Check formatting in CI mode"
	@echo "  ci-check-types  Run type checker in CI mode"
	@echo "  ci-check-style  Check code style in CI mode"
	@echo "  ci-check-all    Run all CI checks"
	@echo "  clean           Clean up temporary files"
	@echo "  help            Show this help message"
