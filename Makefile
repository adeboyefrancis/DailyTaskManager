.PHONY: help install lint test format post-install deploy all run dev clean

help:
	@echo "Daily Task Manager - Makefile Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install dependencies (upgrade pip + install from requirements.txt)"
	@echo "  make post-install     Download textblob corpora"
	@echo "  make clean            Clean up cache and build files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run pylint on Python files"
	@echo "  make format           Format code with black"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests with coverage"
	@echo ""
	@echo "Running & Development:"
	@echo "  make run              Run the FastAPI server"
	@echo "  make dev              Run server in development mode with auto-reload"
	@echo ""
	@echo "Complete Workflow:"
	@echo "  make all              Run install, post-install, lint, test, and format"
	@echo ""

install:
	python3 -m pip install --upgrade pip && \
	python3 -m pip install -r requirements.txt

lint:
	python3 -m pylint --disable=R,C backend/app backend/library

test:
	python3 -m pytest -vv --cov=backend backend/tests/

format:
	python3 -m black backend/app/*.py backend/library/*.py backend/tests/*.py

post-install:
	python3 -m textblob.download_corpora

deploy:
	@echo "🚀 Deploy target - Customize for your environment"
	@echo "   Example: docker build and push to registry"

all: install post-install lint test format

run:
	python3 -m backend.app.main

dev:
	python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -rf dist build

# Alias for common commands
t: test
f: format
l: lint
