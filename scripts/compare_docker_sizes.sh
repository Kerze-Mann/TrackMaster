#!/bin/bash

# Docker Image Size Comparison Script for TrackMaster
# This script builds both the original and optimized Docker images and compares their sizes

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

# Function to get image size
get_image_size() {
    local image_name=$1
    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "$image_name" | awk '{print $2}' || echo "N/A"
}

# Function to build and measure image
build_and_measure() {
    local dockerfile=$1
    local image_name=$2
    local description=$3
    
    info "Building $description..."
    
    start_time=$(date +%s)
    
    if [ -f "$dockerfile" ]; then
        docker build -f "$dockerfile" -t "$image_name" . > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            end_time=$(date +%s)
            build_time=$((end_time - start_time))
            size=$(get_image_size "$image_name")
            success "$description built successfully in ${build_time}s - Size: $size"
            echo "$size"
        else
            error "Failed to build $description"
        fi
    else
        warning "$dockerfile not found, skipping $description"
        echo "N/A"
    fi
}

# Main comparison
main() {
    echo "TrackMaster Docker Image Size Comparison"
    echo "========================================"
    echo ""
    
    # Remove existing images to ensure clean build
    info "Cleaning up existing images..."
    docker rmi trackmaster:original trackmaster:optimized 2>/dev/null || true
    
    echo ""
    
    # Build original (if backup exists) or current
    if [ -f "Dockerfile.original" ]; then
        original_size=$(build_and_measure "Dockerfile.original" "trackmaster:original" "Original Dockerfile")
    else
        warning "Building with requirements.txt (may include PyTorch)"
        # Temporarily use original requirements for comparison
        if [ -f "requirements.txt" ]; then
            # Check if PyTorch is in requirements.txt
            if grep -q "torch" requirements.txt; then
                original_size=$(build_and_measure "Dockerfile" "trackmaster:original" "Current Dockerfile with PyTorch")
            else
                info "PyTorch not found in requirements.txt, building with current setup"
                original_size=$(build_and_measure "Dockerfile" "trackmaster:original" "Current Dockerfile")
            fi
        else
            original_size="N/A"
        fi
    fi
    
    echo ""
    
    # Build optimized version
    optimized_size=$(build_and_measure "Dockerfile" "trackmaster:optimized" "Optimized Dockerfile")
    
    echo ""
    echo "📊 Size Comparison Results:"
    echo "=========================="
    
    if [ -f "Dockerfile.original" ]; then
        echo "Original (with PyTorch): $original_size"
    else
        echo "Previous build:          $original_size"
    fi
    echo "Optimized (no PyTorch):  $optimized_size"
    
    echo ""
    
    # Show what was optimized
    echo "🔧 Optimizations Applied:"
    echo "========================"
    echo "✅ Removed PyTorch (~2-3GB)"
    echo "✅ Removed torchaudio (~500MB)" 
    echo "✅ Multi-stage build (removes build tools)"
    echo "✅ Smaller base image copies"
    echo "✅ Non-root user for security"
    echo "✅ Cleaned package cache"
    
    echo ""
    echo "📦 Final Image Layers:"
    docker images trackmaster:optimized
    
    echo ""
    success "Image optimization complete!"
    info "You can now use: docker run -p 8000:8000 trackmaster:optimized"
}

# Run the comparison
main "$@"
