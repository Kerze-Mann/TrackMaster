#!/bin/bash

# GitHub Actions helper script for TrackMaster
# Provides convenient functions for CI/CD operations

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

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is not installed. Please install it first: https://cli.github.com/"
    fi
}

# Check if user is authenticated
check_auth() {
    if ! gh auth status &> /dev/null; then
        error "You are not authenticated with GitHub CLI. Run 'gh auth login' first."
    fi
}

# Validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        error "Version must follow semantic versioning format (e.g., 1.1.0)"
    fi
}

# Create and push tag
create_tag() {
    local version=$1
    validate_version "$version"
    
    info "Creating and pushing tag v$version..."
    
    # Update version first
    ./scripts/update_version.sh "$version"
    
    # Commit changes
    git add .
    git commit -m "Bump version to $version" || warning "No changes to commit"
    
    # Create and push tag
    git tag "v$version"
    git push origin "v$version"
    
    success "Tag v$version created and pushed"
    success "GitHub Actions workflow will be triggered automatically"
}

# Trigger workflow manually
trigger_workflow() {
    local version=$1
    validate_version "$version"
    
    info "Triggering GitHub Actions workflow for version $version..."
    gh workflow run build-and-publish.yml -f version="$version"
    success "Workflow triggered successfully"
}

# Check workflow status
check_status() {
    info "Recent GitHub Actions runs:"
    gh run list -w build-and-publish.yml -L 5
}

# Watch workflow run
watch_workflow() {
    local run_id=$1
    if [ -z "$run_id" ]; then
        # Get latest run
        run_id=$(gh run list -w build-and-publish.yml -L 1 --json databaseId --jq '.[0].databaseId')
    fi
    
    info "Watching workflow run $run_id..."
    gh run watch "$run_id"
}

# Show help
show_help() {
    echo "TrackMaster GitHub Actions Helper"
    echo "================================="
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  tag <version>      Create and push version tag (triggers workflow)"
    echo "  trigger <version>  Manually trigger workflow"
    echo "  status             Show recent workflow runs"
    echo "  watch [run_id]     Watch workflow run (latest if no ID provided)"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 tag 1.1.0       # Create v1.1.0 tag and trigger workflow"
    echo "  $0 trigger 1.1.0   # Manually trigger workflow for version 1.1.0"
    echo "  $0 status          # Show recent runs"
    echo "  $0 watch           # Watch latest run"
    echo "  $0 watch 123456    # Watch specific run"
}

# Main command handling
main() {
    check_gh_cli
    check_auth
    
    case "${1:-help}" in
        "tag")
            if [ -z "$2" ]; then
                error "Version required. Usage: $0 tag <version>"
            fi
            create_tag "$2"
            ;;
        "trigger")
            if [ -z "$2" ]; then
                error "Version required. Usage: $0 trigger <version>"
            fi
            trigger_workflow "$2"
            ;;
        "status")
            check_status
            ;;
        "watch")
            watch_workflow "$2"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            error "Unknown command: $1. Use '$0 help' for usage information."
            ;;
    esac
}

# Run main function with all arguments
main "$@"
