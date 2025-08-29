"""
TrackMaster - AI-powered audio mastering server

A professional audio mastering service that uses AI to enhance audio files
with intelligent EQ, compression, and loudness normalization.
"""

__version__ = "1.3.0"
__author__ = "TrackMaster Team"
__email__ = "info@trackmaster.com"

from .mastering import AudioMasteringEngine
from .api import create_app

__all__ = ["AudioMasteringEngine", "create_app"]
