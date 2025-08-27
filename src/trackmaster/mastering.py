"""
Audio mastering engine for TrackMaster.

This module contains the core AI-powered audio processing functionality.
"""

import librosa
import numpy as np
from scipy import signal
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AudioMasteringEngine:
    """AI-based audio mastering engine"""
    
    def __init__(self, sample_rate: int = 44100, target_lufs: float = -14.0):
        """
        Initialize the mastering engine.
        
        Args:
            sample_rate: Target sample rate for processing
            target_lufs: Target loudness in LUFS
        """
        self.sample_rate = sample_rate
        self.target_lufs = target_lufs
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return audio data and sample rate.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            Exception: If audio file cannot be loaded
        """
        try:
            # Use librosa for robust audio loading
            audio, sr = librosa.load(file_path, sr=None)
            logger.info(f"Loaded audio: shape={audio.shape}, sr={sr}")
            return audio, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise Exception(f"Unable to load audio file: {e}")
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping.
        
        Args:
            audio: Input audio array
            
        Returns:
            Normalized audio array
        """
        peak = np.max(np.abs(audio))
        if peak > 0:
            return audio / peak * 0.95  # Leave some headroom
        return audio
    
    def apply_eq(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply intelligent EQ curve.
        
        Args:
            audio: Input audio array
            sr: Sample rate
            
        Returns:
            EQ-processed audio array
        """
        # Design a gentle EQ curve for mastering
        # High-pass filter to remove sub-sonic frequencies
        sos_hp = signal.butter(2, 30, btype='highpass', fs=sr, output='sos')
        audio = signal.sosfilt(sos_hp, audio)
        
        # Gentle high-frequency boost for presence
        sos_hf = signal.butter(2, [8000, 16000], btype='bandpass', fs=sr, output='sos')
        hf_boost = signal.sosfilt(sos_hf, audio) * 0.1
        audio = audio + hf_boost
        
        return audio
    
    def apply_compression(self, audio: np.ndarray, threshold: float = 0.7, ratio: float = 3.0) -> np.ndarray:
        """
        Apply dynamic range compression.
        
        Args:
            audio: Input audio array
            threshold: Compression threshold (0.0 to 1.0)
            ratio: Compression ratio
            
        Returns:
            Compressed audio array
        """
        # Simple compression algorithm
        compressed = np.copy(audio)
        
        # Find samples above threshold
        above_threshold = np.abs(audio) > threshold
        
        # Apply compression to samples above threshold
        compressed[above_threshold] = (
            np.sign(audio[above_threshold]) * 
            (threshold + (np.abs(audio[above_threshold]) - threshold) / ratio)
        )
        
        return compressed
    
    def apply_limiter(self, audio: np.ndarray, ceiling: float = 0.95) -> np.ndarray:
        """
        Apply brick-wall limiter.
        
        Args:
            audio: Input audio array
            ceiling: Maximum allowed peak level
            
        Returns:
            Limited audio array
        """
        return np.clip(audio, -ceiling, ceiling)
    
    def calculate_lufs(self, audio: np.ndarray, sr: int) -> float:
        """
        Calculate LUFS (Loudness Units Full Scale).
        
        Args:
            audio: Input audio array
            sr: Sample rate
            
        Returns:
            Estimated LUFS value
        """
        # Simplified LUFS calculation
        # In a real implementation, you'd use a proper LUFS meter
        rms = np.sqrt(np.mean(audio**2))
        lufs_estimate = 20 * np.log10(rms) - 0.691
        return lufs_estimate
    
    def loudness_normalize(self, audio: np.ndarray, sr: int, target_lufs: float = None) -> np.ndarray:
        """
        Normalize audio to target LUFS.
        
        Args:
            audio: Input audio array
            sr: Sample rate
            target_lufs: Target loudness level (uses instance default if None)
            
        Returns:
            Loudness-normalized audio array
        """
        if target_lufs is None:
            target_lufs = self.target_lufs
            
        current_lufs = self.calculate_lufs(audio, sr)
        gain_db = target_lufs - current_lufs
        gain_linear = 10**(gain_db / 20)
        
        normalized = audio * gain_linear
        
        # Prevent clipping
        peak = np.max(np.abs(normalized))
        if peak > 0.95:
            normalized = normalized / peak * 0.95
            
        return normalized
    
    def master_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply complete mastering chain.
        
        Args:
            audio: Input audio array
            sr: Sample rate
            
        Returns:
            Mastered audio array
        """
        logger.info("Starting mastering process...")
        
        # Ensure mono or stereo
        if len(audio.shape) > 1 and audio.shape[0] > 2:
            audio = audio[:2]  # Take first 2 channels
        
        # If mono, ensure it's 1D
        if len(audio.shape) == 2 and audio.shape[0] == 1:
            audio = audio[0]
        
        # Resample to standard rate if needed
        if sr != self.sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            sr = self.sample_rate
        
        original_shape = audio.shape
        
        # Process each channel separately if stereo
        if len(original_shape) == 2:
            processed_channels = []
            for channel in range(original_shape[0]):
                ch_audio = audio[channel]
                ch_audio = self.apply_eq(ch_audio, sr)
                ch_audio = self.apply_compression(ch_audio)
                ch_audio = self.loudness_normalize(ch_audio, sr)
                ch_audio = self.apply_limiter(ch_audio)
                processed_channels.append(ch_audio)
            audio = np.array(processed_channels)
        else:
            # Mono processing
            audio = self.apply_eq(audio, sr)
            audio = self.apply_compression(audio)
            audio = self.loudness_normalize(audio, sr)
            audio = self.apply_limiter(audio)
        
        logger.info("Mastering process completed")
        return audio
