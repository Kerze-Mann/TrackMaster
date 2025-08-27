#!/bin/bash

# Quick status checker for GitHub Actions (no GitHub CLI required)
# This script provides basic status information using git and web links

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get repository info from git
get_repo_info() {
    local origin_url=$(git config --get remote.origin.url)
    if [[ $origin_url =~ github\.com[:/]([^/]+)/([^./]+) ]]; then
        REPO_OWNER="${BASH_REMATCH[1]}"
        REPO_NAME="${BASH_REMATCH[2]}"
        echo "$REPO_OWNER/$REPO_NAME"
    else
        echo "unknown"
    fi
}

# Get latest tags
get_latest_tags() {
    info "Recent version tags:"
    git tag --sort=-version:refname | grep '^v[0-9]' | head -5 || echo "No version tags found"
}

# Main status function
show_status() {
    local repo=$(get_repo_info)
    
    echo "TrackMaster GitHub Actions Status"
    echo "=================================="
    echo ""
    
    info "Repository: $repo"
    echo ""
    
    get_latest_tags
    echo ""
    
    if command -v gh >/dev/null 2>&1; then
        success "GitHub CLI is available"
        info "Checking recent workflow runs..."
        gh run list -w build-and-publish.yml -L 5 2>/dev/null || warning "No workflows found or not authenticated"
    else
        warning "GitHub CLI not installed"
        info "Install with: brew install gh"
    fi
    
    echo ""
    info "Manual links:"
    echo "📋 Actions: https://github.com/$repo/actions"
    echo "🏷️  Releases: https://github.com/$repo/releases"
    echo "📦 Packages: https://github.com/$repo/pkgs/container/trackmaster"
    echo ""
    
    success "Use 'make tag VERSION=x.y.z' to create new releases"
}

# Run status check
show_status
