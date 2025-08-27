"""
Tests for TrackMaster package initialization.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_package_import():
    """Test that the main package can be imported."""
    try:
        import trackmaster
        assert trackmaster.__version__ == "1.0.0"
        assert hasattr(trackmaster, "AudioMasteringEngine")
        assert hasattr(trackmaster, "create_app")
    except ImportError as e:
        assert False, f"Failed to import trackmaster package: {e}"


def test_mastering_engine_import():
    """Test that AudioMasteringEngine can be imported."""
    try:
        from trackmaster.mastering import AudioMasteringEngine
        engine = AudioMasteringEngine()
        assert engine.sample_rate == 44100
        assert engine.target_lufs == -14.0
    except ImportError as e:
        assert False, f"Failed to import AudioMasteringEngine: {e}"


def test_api_import():
    """Test that API module can be imported."""
    try:
        from trackmaster.api import create_app
        app = create_app()
        assert app is not None
    except ImportError as e:
        assert False, f"Failed to import API module: {e}"


def test_config_import():
    """Test that config module can be imported."""
    try:
        from trackmaster.config import settings
        assert settings.DEFAULT_SAMPLE_RATE == 44100
        assert settings.DEFAULT_TARGET_LUFS == -14.0
    except ImportError as e:
        assert False, f"Failed to import config module: {e}"
