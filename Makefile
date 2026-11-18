PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: setup dev test lint

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r requirements.txt
	cd client && npm install

dev:
	@if [ ! -x "$(BIN)/uvicorn" ]; then \
		echo "Run 'make setup' first."; \
		exit 1; \
	fi
	bash scripts/dev.sh

test:
	@if [ ! -x "$(BIN)/pytest" ]; then \
		echo "Run 'make setup' first."; \
		exit 1; \
	fi
	$(BIN)/pytest
	cd client && npm test

lint:
	@if [ ! -x "$(BIN)/ruff" ]; then \
		echo "Run 'make setup' first."; \
		exit 1; \
	fi
	$(BIN)/ruff check backend
	$(BIN)/mypy backend/app
