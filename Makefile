# Makefile for nova-api project

.PHONY: help install test lint format clean run-dev run-prod

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean build artifacts"
	@echo "  run-dev    - Run development server"
	@echo "  run-prod   - Run production server"

install:
	uv sync

test:
	uv run pytest

lint:
	uv run flake8 src/ tests/

format:
	uv run black src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .venv/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

run-dev:
	uv run uvicorn src.nova_agent.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uv run uvicorn src.nova_agent.main:app --host 0.0.0.0 --port 8000
