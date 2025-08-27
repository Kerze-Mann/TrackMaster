"""
Utility functions for TrackMaster.
"""

import logging
import os
from pathlib import Path
from typing import Optional
import uuid


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        UUID string for session identification
    """
    return str(uuid.uuid4())


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate if file has an allowed extension.
    
    Args:
        filename: Name of the file to validate
        allowed_extensions: List of allowed file extensions
        
    Returns:
        True if file extension is allowed, False otherwise
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in allowed_extensions


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def cleanup_old_files(directory: Path, max_age_hours: int = 24) -> int:
    """
    Clean up old files in a directory.
    
    Args:
        directory: Directory to clean up
        max_age_hours: Maximum age of files to keep (in hours)
        
    Returns:
        Number of files deleted
    """
    import time
    
    if not directory.exists():
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except OSError:
                    pass  # File might be in use or already deleted
    
    return deleted_count
