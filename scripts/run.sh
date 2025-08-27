#!/bin/bash

# TrackMaster - Build and Run Script

set -e

echo "🎵 TrackMaster Audio Mastering Server"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker environment ready"

# Create directories for volumes
mkdir -p uploads outputs

echo "📁 Created upload and output directories"

# Build and start the service
echo "🔨 Building and starting TrackMaster..."
$COMPOSE_CMD up --build -d

echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if service is running
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ TrackMaster is running successfully!"
    echo ""
    echo "🌐 Server is available at: http://localhost:8000"
    echo "📊 Health check: http://localhost:8000/health"
    echo "📖 API docs: http://localhost:8000/docs"
    echo ""
    echo "🛠️  Usage examples:"
    echo "   # Upload and master an audio file:"
    echo "   curl -X POST \"http://localhost:8000/master\" \\"
    echo "        -F \"file=@your_audio.wav\" \\"
    echo "        -F \"target_lufs=-14.0\" \\"
    echo "        --output mastered_output.wav"
    echo ""
    echo "📋 To view logs:"
    echo "   $COMPOSE_CMD logs -f"
    echo ""
    echo "🛑 To stop the service:"
    echo "   $COMPOSE_CMD down"
else
    echo "❌ Service failed to start. Check logs:"
    $COMPOSE_CMD logs
    exit 1
fi
