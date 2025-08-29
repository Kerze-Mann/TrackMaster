# Optimized multi-stage Dockerfile for TrackMaster
# This reduces image size significantly by removing PyTorch and using multi-stage build

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY pyproject.toml .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install optimized requirements (without PyTorch)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and install package
COPY src/ ./src/
RUN pip install -e .

# Stage 2: Production image
FROM python:3.11-slim

# Build argument for version
ARG VERSION=1.0.0
ENV TRACKMASTER_VERSION=$VERSION

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy only the application code
COPY --from=builder /app/src ./src

# Create directories for temporary files
RUN mkdir -p /tmp/uploads /tmp/outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r trackmaster && useradd -r -g trackmaster trackmaster
RUN chown -R trackmaster:trackmaster /app /tmp/uploads /tmp/outputs
USER trackmaster

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["trackmaster"]
