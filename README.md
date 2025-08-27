# TrackMaster

AI-powered audio mastering server that accepts WAV and MP3 files, performs intelligent mastering, and returns professionally mastered tracks.

## Features

- 🎵 **Multi-format Support**: WAV, MP3, FLAC, M4A
- 🤖 **AI-Powered Mastering**: Intelligent EQ, compression, and loudness normalization
- 🐳 **Docker Ready**: Easy deployment with Docker containers
- 📊 **Industry Standards**: LUFS-based loudness normalization (-14 LUFS default)
- 🔄 **RESTful API**: Simple HTTP endpoints for integration
- 📈 **Health Monitoring**: Built-in health checks and logging
- 🐍 **Modern Python**: Proper package structure with setup.py and pyproject.toml
- 🚀 **CI/CD Ready**: GitHub Actions workflow for automated Docker builds and publishing

## Project Structure

```
TrackMaster/
├── src/
│   └── trackmaster/          # Main package
│       ├── __init__.py       # Package initialization
│       ├── api.py           # FastAPI application
│       ├── mastering.py     # Audio mastering engine
│       ├── config.py        # Configuration settings
│       ├── utils.py         # Utility functions
│       └── main.py          # Main entry point
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_package.py
│   └── test_api.py
├── examples/                # Usage examples
│   └── client_example.py
├── scripts/                 # Utility scripts
│   └── run.sh
├── docs/                    # Documentation
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Modern Python packaging
├── setup.py               # Package setup
├── Makefile               # Development commands
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

## Mastering Chain

The AI mastering engine applies the following processing chain:

1. **EQ Processing**: High-pass filtering and presence enhancement
2. **Dynamic Compression**: Intelligent compression with configurable ratio
3. **Loudness Normalization**: LUFS-based loudness matching for streaming platforms
4. **Brick-wall Limiting**: Peak limiting to prevent clipping

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Kerze-Mann/TrackMaster.git
cd TrackMaster

# Install the package
pip install -e .

# Or install with development dependencies
make install-dev
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t trackmaster .
docker run -p 8000:8000 trackmaster
```

## Quick Start

### Development Server

```bash
# Start the development server
make dev

# Or directly
python -m trackmaster.main
```

### Docker Deployment

```bash
# Using the convenience script
./scripts/run.sh

# Or using make
make docker-compose-up
```

The server will be available at: `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /health
```

### Master Audio File
```bash
POST /master
```

**Parameters:**
- `file`: Audio file (multipart/form-data)
- `target_lufs`: Target loudness in LUFS (optional, default: -14.0)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/master" \
     -F "file=@your_audio_file.wav" \
     -F "target_lufs=-16.0" \
     --output mastered_output.wav
```

**Example using Python:**
```python
import requests

with open('input.wav', 'rb') as f:
    files = {'file': f}
    data = {'target_lufs': -14.0}
    response = requests.post('http://localhost:8000/master', files=files, data=data)
    
    if response.status_code == 200:
        with open('mastered_output.wav', 'wb') as output:
            output.write(response.content)
```

### Cleanup Session
```bash
DELETE /cleanup/{session_id}
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Start development server
make dev
```

### Available Make Commands

- `make install` - Install the package
- `make install-dev` - Install with development dependencies
- `make test` - Run tests
- `make format` - Format code with black and isort
- `make lint` - Run linting checks
- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container
- `make clean` - Clean build artifacts

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=trackmaster --cov-report=html

# Or using make
make test
```

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

## Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `UPLOAD_DIR`: Upload directory (default: /tmp/uploads)
- `OUTPUT_DIR`: Output directory (default: /tmp/outputs)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 100MB)

### Mastering Parameters

You can customize the mastering process by modifying the `AudioMasteringEngine` class:

- `target_lufs`: Target loudness level (default: -14.0 LUFS)
- `compression_threshold`: Compression threshold (default: 0.7)
- `compression_ratio`: Compression ratio (default: 3.0)
- `limiter_ceiling`: Limiter ceiling (default: 0.95)

## Supported Formats

### Input Formats
- WAV (recommended for best quality)
- MP3
- FLAC
- M4A

### Output Format
- WAV (44.1kHz, 16/24-bit)

## Deployment & CI/CD

### Automated Deployment with GitHub Actions

TrackMaster includes a complete GitHub Actions workflow for automated building and publishing:

```bash
# Update version and trigger deployment
make version VERSION=1.1.0
make tag VERSION=1.1.0

# Or manually trigger workflow
make gh-dispatch VERSION=1.1.0

# Check workflow status
make gh-status
```

This automatically:
- ✅ Updates version in all source files  
- ✅ Builds Docker image with proper tags
- ✅ Publishes to GitHub Container Registry (ghcr.io)
- ✅ Creates GitHub release with documentation
- ✅ Tests the built image before publishing
- ✅ Generates artifact attestation for security

### Using Published Images

```bash
# Pull specific version
docker pull ghcr.io/your-username/trackmaster:1.1.0

# Pull latest release
docker pull ghcr.io/your-username/trackmaster:latest

# Run with version
docker run -p 8000:8000 ghcr.io/your-username/trackmaster:1.1.0
```

### Workflow Triggers

The GitHub Actions workflow is triggered by:
- **Tag push**: Create and push a version tag (e.g., `v1.1.0`)
- **Manual dispatch**: Trigger workflow manually with GitHub CLI or web interface

## Docker Deployment

### Production Deployment

```bash
# Build the image
docker build -t trackmaster .

# Run with custom configuration
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e MAX_FILE_SIZE=52428800 \
  -v ./uploads:/tmp/uploads \
  -v ./outputs:/tmp/outputs \
  trackmaster
```

### Docker Compose

```yaml
version: '3.8'
services:
  trackmaster:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./uploads:/tmp/uploads
      - ./outputs:/tmp/outputs
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`make install-dev`)
4. Make your changes
5. Run tests (`make test`)
6. Format code (`make format`)
7. Run linting (`make lint`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Memory Errors**: Reduce file size or increase container memory
2. **Format Errors**: Ensure file format is supported
3. **Performance Issues**: Check CPU and memory availability
4. **Import Errors**: Make sure package is installed (`pip install -e .`)

### Logs

View application logs:
```bash
# Docker logs
docker-compose logs -f trackmaster

# Direct logs
python -m trackmaster.main
```

### Development Issues

```bash
# Clean build artifacts
make clean

# Reinstall package
pip uninstall trackmaster
make install-dev
```