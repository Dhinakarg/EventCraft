.PHONY: help lint format typecheck test test-js run verify

VENV = .venv
PYTHON = $(VENV)/Scripts/python
RUFF = $(VENV)/Scripts/ruff
MYPY = $(VENV)/Scripts/mypy
PYTEST = $(VENV)/Scripts/pytest
UVICORN = $(VENV)/Scripts/uvicorn

help:
	@echo "Available commands:"
	@echo "  make lint       - Run ruff linter checks"
	@echo "  make format     - Run ruff format on all python files"
	@echo "  make typecheck  - Run mypy --strict on app"
	@echo "  make test       - Run pytest test suite with coverage"
	@echo "  make test-js    - Run node --test unit tests for static/js"
	@echo "  make verify     - Run full quality verification pipeline"
	@echo "  make run        - Start local development server with uvicorn"

lint:
	$(RUFF) check .
	$(RUFF) format --check .

format:
	$(RUFF) check --fix .
	$(RUFF) format .

typecheck:
	$(MYPY) --strict app

test:
	$(PYTEST) --cov=app --cov-report=term-missing --cov-fail-under=90

test-js:
	node --test tests/js/*.test.js

verify: lint typecheck test test-js

run:
	$(UVICORN) app.main:app --host 127.0.0.1 --port 8000 --reload
