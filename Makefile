.PHONY: install backend tui scrape test lint clean

## Install all Python dependencies
install:
	pip install -r requirements.txt

## Start the FastAPI backend (hot-reload)
backend:
	python main.py backend

## Launch the Textual TUI
tui:
	python main.py tui

## Run a one-shot APIs.guru scrape
scrape:
	python main.py scrape

## Run tests
test:
	pytest tests/ -v

## Lint the codebase
lint:
	python -m py_compile apiradar/backend/app/api/main.py \
		apiradar/backend/app/db/models.py \
		apiradar/backend/app/core/database.py \
		apiradar/backend/app/scrapers/apis_guru.py \
		apiradar/backend/app/scrapers/github.py \
		apiradar/tui/src/app.py \
		apiradar/tui/src/screens/dashboard.py \
		apiradar/tui/src/screens/search_screen.py \
		main.py
	@echo "No syntax errors found."

## Remove Python cache files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f leakhub.db
