# GitLab CI/CD Deployment Guide

This document explains how to use the automated CI/CD pipeline for TrackMaster.

## Overview

The GitLab CI/CD pipeline automatically:
1. **Updates version numbers** in source code when you push a version tag
2. **Builds Docker images** with proper versioning
3. **Publishes to GitLab Container Registry** with multiple tags
4. **Creates GitLab releases** with documentation
5. **Tests the built images** before publishing

## Quick Start

### 1. Update Version and Deploy

```bash
# Method 1: Using make (recommended)
make version VERSION=1.1.0  # Updates all version files
make tag VERSION=1.1.0      # Commits, tags, and pushes

# Method 2: Manual process
./scripts/update_version.sh 1.1.0
git add .
git commit -m "Bump version to 1.1.0"
git tag v1.1.0
git push origin v1.1.0
```

### 2. Monitor Pipeline

1. Go to your GitLab project
2. Navigate to **CI/CD > Pipelines**
3. Watch the pipeline progress through: `version` → `build` → `publish`

### 3. Use Published Images

After successful pipeline completion, your images will be available:

```bash
# Pull specific version
docker pull registry.gitlab.com/your-username/trackmaster:1.1.0

# Pull latest
docker pull registry.gitlab.com/your-username/trackmaster:latest

# Pull major version (e.g., all 1.x.x versions)
docker pull registry.gitlab.com/your-username/trackmaster:v1

# Pull major.minor version (e.g., all 1.1.x versions)  
docker pull registry.gitlab.com/your-username/trackmaster:v1.1
```

## Pipeline Stages

### Stage 1: Version Update
- **Trigger**: Tag matching `v*.*.*` pattern
- **Actions**:
  - Updates `pyproject.toml`
  - Updates `setup.py` 
  - Updates `src/trackmaster/__init__.py`
  - Updates version in API responses
- **Artifacts**: Updated source files

### Stage 2: Docker Build
- **Dependencies**: Version update stage
- **Actions**:
  - Builds Docker image with version tags
  - Runs health check tests
  - Validates image functionality
- **Tags Created**:
  - `registry.gitlab.com/your-username/trackmaster:1.1.0`
  - `registry.gitlab.com/your-username/trackmaster:latest`

### Stage 3: Publish
- **Dependencies**: Build stage
- **Actions**:
  - Pushes to GitLab Container Registry
  - Creates additional semantic version tags
  - Creates GitLab release with documentation

### Stage 4: Release (Optional)
- **Actions**:
  - Creates GitLab release page
  - Includes Docker usage instructions
  - Links to API documentation

## Environment Variables

The pipeline uses these GitLab CI variables:

| Variable | Description | Auto-provided |
|----------|-------------|---------------|
| `CI_REGISTRY` | GitLab container registry URL | ✅ |
| `CI_REGISTRY_IMAGE` | Full image path | ✅ |
| `CI_REGISTRY_USER` | Registry username | ✅ |
| `CI_REGISTRY_PASSWORD` | Registry password | ✅ |
| `CI_COMMIT_TAG` | Git tag that triggered pipeline | ✅ |

## Version Tagging Strategy

### Semantic Versioning
- **Format**: `v<major>.<minor>.<patch>`
- **Examples**: `v1.0.0`, `v1.1.0`, `v2.0.0`

### Docker Tags Created
For tag `v1.1.0`, these Docker tags are created:
- `1.1.0` (exact version)
- `latest` (always points to newest)
- `v1` (latest in major version 1)
- `v1.1` (latest in minor version 1.1)

## Local Development

### Test Version Update Locally
```bash
# Test version script
./scripts/update_version.sh 1.1.0

# Verify changes
git diff
```

### Build and Test Docker Image Locally
```bash
# Build with version
docker build --build-arg VERSION=1.1.0 -t trackmaster:1.1.0 .

# Test the image
docker run -p 8000:8000 trackmaster:1.1.0

# Check version
curl http://localhost:8000/health
```

## Troubleshooting

### Pipeline Fails at Version Stage
- **Cause**: Invalid version format
- **Solution**: Use semantic versioning (e.g., `v1.1.0`)

### Pipeline Fails at Build Stage
- **Cause**: Docker build errors or health check failure
- **Solution**: Test Docker build locally first

### Pipeline Fails at Publish Stage
- **Cause**: Registry authentication issues
- **Solution**: Check GitLab project settings and registry permissions

### No Pipeline Triggered
- **Cause**: Tag doesn't match pattern `v*.*.*`
- **Solution**: Ensure tag starts with 'v' and follows semantic versioning

## Best Practices

1. **Test Locally First**
   ```bash
   make test
   make docker-build
   ```

2. **Use Semantic Versioning**
   - `v1.0.0` → `v1.0.1` (patch: bug fixes)
   - `v1.0.0` → `v1.1.0` (minor: new features)
   - `v1.0.0` → `v2.0.0` (major: breaking changes)

3. **Check Pipeline Status**
   - Monitor GitLab CI/CD pipelines
   - Check logs for any issues
   - Verify images are published correctly

4. **Update Documentation**
   - Update `CHANGELOG.md` for each release
   - Update `README.md` if needed
   - Include breaking changes in release notes

## Container Registry Access

### Public Access
Images are available at:
```
registry.gitlab.com/your-username/trackmaster:latest
```

### Private Registry Authentication
```bash
# Login to GitLab registry
docker login registry.gitlab.com

# Use personal access token or deploy token
Username: your-username
Password: your-token
```

## Monitoring Deployments

### Health Checks
All published images include health checks:
```bash
# Container will report healthy when ready
docker run --health-timeout=30s registry.gitlab.com/your-username/trackmaster:latest
```

### Version Verification
```bash
# Check running version
curl http://localhost:8000/health | jq '.version'
```

## Support

For issues with the CI/CD pipeline:
1. Check GitLab CI/CD pipeline logs
2. Verify tag format matches `v*.*.*`
3. Ensure GitLab Container Registry is enabled
4. Check project permissions for registry access
