.PHONY: help install install-dev test format lint docker-build docker-run clean version tag

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
	@echo "version       Update version (usage: make version VERSION=1.1.0)"
	@echo "tag           Create and push git tag (usage: make tag VERSION=1.1.0)"
	@echo "gh-tag        Create and push git tag with GitHub Actions (usage: make gh-tag VERSION=1.1.0)"
	@echo "gh-dispatch   Trigger GitHub Actions manually (usage: make gh-dispatch VERSION=1.1.0)"
	@echo "gh-status     Check GitHub Actions workflow status"
	@echo "status        Simple status check (works without GitHub CLI)"
	@echo "gh-watch      Watch latest GitHub Actions workflow run"
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

# Version management
version:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make version VERSION=1.1.0"; \
		exit 1; \
	fi
	./scripts/update_version.sh $(VERSION)

# Create and push git tag
tag:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make tag VERSION=1.1.0"; \
		exit 1; \
	fi
	@echo "Creating and pushing tag v$(VERSION)..."
	git add .
	git commit -m "Bump version to $(VERSION)" || true
	git tag v$(VERSION)
	git push origin v$(VERSION)
	@echo "✅ Tag v$(VERSION) created and pushed"
	@echo "🚀 GitHub Actions will now build and publish the Docker image"
	@echo "📋 Check status at: https://github.com/$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"

# GitHub Actions helpers (requires GitHub CLI)
gh-dispatch:
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI not found. Install with: brew install gh"; \
		exit 1; \
	fi
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make gh-dispatch VERSION=1.1.0"; \
		exit 1; \
	fi
	./scripts/github_actions.sh trigger $(VERSION)

gh-status:
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI not found. Install with: brew install gh"; \
		echo "📋 Check status manually at: https://github.com/$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"; \
		exit 1; \
	fi
	./scripts/github_actions.sh status

# Simple status check (works without GitHub CLI)
status:
	./scripts/check_status.sh

gh-watch:
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI not found. Install with: brew install gh"; \
		exit 1; \
	fi
	./scripts/github_actions.sh watch

# Create and push git tag (GitHub Actions version)
gh-tag:
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI not found. Install with: brew install gh"; \
		echo "💡 Use 'make tag VERSION=$(VERSION)' instead"; \
		exit 1; \
	fi
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make gh-tag VERSION=1.1.0"; \
		exit 1; \
	fi
	./scripts/github_actions.sh tag $(VERSION)
