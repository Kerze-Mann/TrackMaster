# GitHub Actions CI/CD Guide

This document explains how to use the automated GitHub Actions workflow for building and publishing TrackMaster Docker images.

## Overview

The GitHub Actions workflow automatically:
- Updates version numbers across all source files
- Builds Docker images with proper semantic versioning
- Tests the built image to ensure it works correctly
- Publishes to GitHub Container Registry (ghcr.io)
- Creates GitHub releases with documentation
- Generates security attestations for the build

## Workflow File

The main workflow is defined in `.github/workflows/build-and-publish.yml` and consists of 4 jobs:

1. **update-version**: Extracts version and updates source files
2. **build-and-test**: Builds Docker image and runs health checks
3. **publish**: Publishes to GitHub Container Registry
4. **create-release**: Creates GitHub release with documentation

## Triggering the Workflow

### Method 1: Create Version Tag (Recommended)

This is the standard way to release a new version:

```bash
# Update version and create tag
make gh-tag VERSION=1.2.0

# Or use the helper script directly
./scripts/github_actions.sh tag 1.2.0

# Or manually
make version VERSION=1.2.0
git add .
git commit -m "Bump version to 1.2.0"
git tag v1.2.0
git push origin v1.2.0
```

### Method 2: Manual Workflow Dispatch

Trigger the workflow manually without creating a tag:

```bash
# Using make
make gh-dispatch VERSION=1.2.0

# Using helper script
./scripts/github_actions.sh trigger 1.2.0

# Using GitHub CLI directly
gh workflow run build-and-publish.yml -f version=1.2.0
```

## Monitoring Workflow Status

### Check Recent Runs

```bash
# Using make
make gh-status

# Using helper script
./scripts/github_actions.sh status

# Using GitHub CLI directly
gh run list -w build-and-publish.yml -L 5
```

### Watch Live Run

```bash
# Watch latest run
make gh-watch

# Watch specific run
./scripts/github_actions.sh watch <run-id>

# Using GitHub CLI directly
gh run watch <run-id>
```

## Version Management

The workflow automatically updates version numbers in:
- `src/trackmaster/__init__.py`
- `setup.py`
- `pyproject.toml`

Version format must follow semantic versioning: `MAJOR.MINOR.PATCH` (e.g., `1.2.0`)

## Docker Image Publishing

### Registry Information

Images are published to GitHub Container Registry:
- **Registry**: `ghcr.io`
- **Repository**: `ghcr.io/<username>/trackmaster`

### Image Tags

The workflow creates multiple tags:
- `<version>` (e.g., `1.2.0`)
- `<major>` (e.g., `1`)
- `<major>.<minor>` (e.g., `1.2`)
- `latest`

### Using Published Images

```bash
# Pull specific version
docker pull ghcr.io/<username>/trackmaster:1.2.0

# Pull latest
docker pull ghcr.io/<username>/trackmaster:latest

# Run container
docker run -p 8000:8000 ghcr.io/<username>/trackmaster:1.2.0
```

## Requirements

### GitHub CLI

Install and authenticate with GitHub CLI:

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login
```

### Repository Permissions

Ensure your repository has:
- **Contents**: Write (for creating releases)
- **Packages**: Write (for publishing to ghcr.io)
- **Actions**: Write (for running workflows)

### Repository Settings

1. Go to your repository **Settings** → **Actions** → **General**
2. Set **Workflow permissions** to "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"

## Security Features

### Package Visibility

By default, packages are published as private. To make them public:

1. Go to your repository **Packages** tab
2. Click on the `trackmaster` package
3. Go to **Package settings**
4. Change visibility to **Public**

### Artifact Attestation

The workflow generates build provenance attestations for security:
- Provides cryptographic proof of build integrity
- Links the image to the source code and build process
- Can be verified using GitHub's attestation APIs

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check repository permissions and workflow settings
2. **Authentication Failed**: Ensure GitHub CLI is authenticated (`gh auth login`)
3. **Version Format Error**: Use semantic versioning format (e.g., `1.2.0`)
4. **Package Push Failed**: Check package visibility and permissions

### Debug Information

View workflow logs:
```bash
# Get run ID and view logs
gh run list -w build-and-publish.yml -L 1
gh run view <run-id> --log
```

### Re-running Failed Workflows

```bash
# Re-run failed jobs
gh run rerun <run-id> --failed

# Re-run entire workflow
gh run rerun <run-id>
```

## Example Release Process

Here's a complete example of releasing version 1.2.0:

```bash
# 1. Make your code changes
git add .
git commit -m "Add new features for v1.2.0"

# 2. Create release with GitHub Actions
make gh-tag VERSION=1.2.0

# 3. Monitor the build
make gh-status
make gh-watch

# 4. Once complete, the image is available
docker pull ghcr.io/<username>/trackmaster:1.2.0
```

## Integration with Other Tools

### Docker Compose

Update your `docker-compose.yml` to use published images:

```yaml
version: '3.8'
services:
  trackmaster:
    image: ghcr.io/<username>/trackmaster:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
```

### Kubernetes

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trackmaster
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trackmaster
  template:
    metadata:
      labels:
        app: trackmaster
    spec:
      containers:
      - name: trackmaster
        image: ghcr.io/<username>/trackmaster:1.2.0
        ports:
        - containerPort: 8000
```

## Best Practices

1. **Use semantic versioning** for clear version communication
2. **Test locally** before creating tags
3. **Monitor workflow runs** to catch issues early
4. **Use specific version tags** in production deployments
5. **Keep CHANGELOG.md updated** with release notes
6. **Review generated releases** on GitHub for accuracy

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry Guide](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Semantic Versioning](https://semver.org/)
