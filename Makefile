.PHONY: help install install-dev test format lint docker-build docker-run clean

# Default target
help:
	@echo "TrackMaster Development Commands"
	@echo "================================"
	@echo "install       Install the package"
	@echo "install-dev   Install with development dependencies"
	@echo "test          Run tests"
	@echo "format        Format code with black and isort"
	@echo "lint          Run linting checks"
	@echo "docker-build  Build Docker image"
	@echo "docker-run    Run Docker container"
	@echo "clean         Clean build artifacts"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=trackmaster --cov-report=html

# Code formatting
format:
	black src/ tests/ examples/
	isort src/ tests/ examples/

# Linting
lint:
	flake8 src/ tests/
	mypy src/
	black --check src/ tests/ examples/
	isort --check-only src/ tests/ examples/

# Docker commands
docker-build:
	docker build -t trackmaster .

docker-run:
	docker run -p 8000:8000 trackmaster

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

# Development server
dev:
	python -m trackmaster.main

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
