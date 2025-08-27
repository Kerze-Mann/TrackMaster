"""
Configuration settings for TrackMaster.
"""

import os
from pathlib import Path
from typing import List


class Settings:
    """Application settings and configuration."""
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Audio processing settings
    DEFAULT_SAMPLE_RATE: int = 44100
    DEFAULT_TARGET_LUFS: float = -14.0
    
    # File handling
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "/tmp/outputs"))
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default
    
    # Supported file formats
    SUPPORTED_EXTENSIONS: List[str] = [".wav", ".mp3", ".flac", ".m4a"]
    
    # Mastering parameters
    COMPRESSION_THRESHOLD: float = 0.7
    COMPRESSION_RATIO: float = 3.0
    LIMITER_CEILING: float = 0.95
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Initialize settings and create required directories."""
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.OUTPUT_DIR.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
