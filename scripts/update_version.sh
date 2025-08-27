#!/bin/bash

# Version management script for TrackMaster
# Usage: ./scripts/update_version.sh <version>

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.1.0"
    exit 1
fi

VERSION=$1

# Validate version format (semantic versioning)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must follow semantic versioning format (e.g., 1.1.0)"
    exit 1
fi

echo "Updating TrackMaster to version $VERSION..."

# Update version in pyproject.toml
sed -i.bak "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
echo "✅ Updated pyproject.toml"

# Update version in setup.py
sed -i.bak "s/version=\"[^\"]*\"/version=\"$VERSION\"/" setup.py
echo "✅ Updated setup.py"

# Update version in __init__.py
sed -i.bak "s/__version__ = .*/__version__ = \"$VERSION\"/" src/trackmaster/__init__.py
echo "✅ Updated src/trackmaster/__init__.py"

# Clean up backup files
rm -f pyproject.toml.bak setup.py.bak src/trackmaster/__init__.py.bak

echo ""
echo "🎉 Version updated to $VERSION"
echo ""
echo "Next steps:"
echo "1. Commit your changes:"
echo "   git add ."
echo "   git commit -m \"Bump version to $VERSION\""
echo ""
echo "2. Create and push the tag:"
echo "   git tag v$VERSION"
echo "   git push origin v$VERSION"
echo ""
echo "3. GitLab CI will automatically:"
echo "   - Build Docker image with version $VERSION"
echo "   - Publish to GitLab Container Registry"
echo "   - Create a GitLab release"
