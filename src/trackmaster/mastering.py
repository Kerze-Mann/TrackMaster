"""
Audio mastering engine for TrackMaster.

This module contains the core AI-powered audio processing functionality.
"""

import librosa
import numpy as np
from scipy import signal
import logging
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)


class ReferenceAnalyzer:
    """Analyzes reference tracks to extract mastering characteristics"""
    
    @staticmethod
    def analyze_reference(audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze reference track to extract mastering characteristics.
        
        Args:
            audio: Reference audio array
            sr: Sample rate
            
        Returns:
            Dictionary containing reference characteristics
        """
        # Ensure mono for analysis
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=0)
        
        # Calculate LUFS
        rms = np.sqrt(np.mean(audio**2))
        lufs = 20 * np.log10(rms + 1e-10) - 0.691
        
        # Dynamic range analysis
        dynamic_range = ReferenceAnalyzer._calculate_dynamic_range(audio)
        
        # Spectral characteristics
        spectral_features = ReferenceAnalyzer._analyze_spectrum(audio, sr)
        
        # Peak analysis
        peak_level = np.max(np.abs(audio))
        
        return {
            "target_lufs": lufs,
            "dynamic_range": dynamic_range,
            "peak_level": peak_level,
            "spectral_centroid": spectral_features["spectral_centroid"],
            "spectral_rolloff": spectral_features["spectral_rolloff"],
            "high_freq_energy": spectral_features["high_freq_energy"],
            "low_freq_energy": spectral_features["low_freq_energy"],
            "compression_ratio": ReferenceAnalyzer._estimate_compression_ratio(audio)
        }
    
    @staticmethod
    def _calculate_dynamic_range(audio: np.ndarray) -> float:
        """Calculate dynamic range (difference between loud and quiet parts)"""
        # Use percentiles to measure dynamic range
        loud_level = np.percentile(np.abs(audio), 95)
        quiet_level = np.percentile(np.abs(audio), 10)
        dr = 20 * np.log10((loud_level + 1e-10) / (quiet_level + 1e-10))
        return max(0.0, min(40.0, dr))  # Clamp between 0-40 dB
    
    @staticmethod
    def _analyze_spectrum(audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze spectral characteristics of the reference"""
        # Calculate spectral features using librosa
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0].mean()
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0].mean()
        
        # Calculate frequency energy distribution
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Define frequency bands
        low_freq_mask = freqs < 500
        high_freq_mask = freqs > 5000
        
        low_freq_energy = np.mean(magnitude[low_freq_mask])
        high_freq_energy = np.mean(magnitude[high_freq_mask])
        
        return {
            "spectral_centroid": spectral_centroid,
            "spectral_rolloff": spectral_rolloff,
            "high_freq_energy": float(high_freq_energy),
            "low_freq_energy": float(low_freq_energy)
        }
    
    @staticmethod
    def _estimate_compression_ratio(audio: np.ndarray) -> float:
        """Estimate compression ratio based on dynamic characteristics"""
        # Calculate ratio of peak to RMS as compression indicator
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio**2))
        
        if rms > 0:
            peak_to_rms = peak / rms
            # Convert to estimated compression ratio (1.0 = no compression, higher = more compression)
            compression_ratio = max(1.0, min(10.0, 15.0 / peak_to_rms))
        else:
            compression_ratio = 3.0  # Default
            
        return compression_ratio


class AudioMasteringEngine:
    """AI-based audio mastering engine with reference track support"""
    
    def __init__(self, sample_rate: int = 44100, target_lufs: float = -14.0):
        """
        Initialize the mastering engine.
        
        Args:
            sample_rate: Target sample rate for processing
            target_lufs: Target loudness in LUFS (used when no reference provided)
        """
        self.sample_rate = sample_rate
        self.target_lufs = target_lufs
        self.reference_analyzer = ReferenceAnalyzer()
        
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
    
    def analyze_reference(self, reference_audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze reference track to extract mastering targets.
        
        Args:
            reference_audio: Reference audio array
            sr: Sample rate
            
        Returns:
            Dictionary containing reference characteristics
        """
        return self.reference_analyzer.analyze_reference(reference_audio, sr)
    
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
    
    def apply_eq(self, audio: np.ndarray, sr: int, reference_params: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Apply intelligent EQ curve, optionally matching reference characteristics.
        
        Args:
            audio: Input audio array
            sr: Sample rate
            reference_params: Optional reference track characteristics
            
        Returns:
            EQ-processed audio array
        """
        # Design a gentle EQ curve for mastering
        # High-pass filter to remove sub-sonic frequencies
        sos_hp = signal.butter(2, 30, btype='highpass', fs=sr, output='sos')
        audio = signal.sosfilt(sos_hp, audio)
        
        if reference_params:
            # Apply reference-based EQ adjustments
            audio = self._apply_reference_eq(audio, sr, reference_params)
        else:
            # Apply standard mastering EQ
            # Gentle high-frequency boost for presence
            sos_hf = signal.butter(2, [8000, 16000], btype='bandpass', fs=sr, output='sos')
            hf_boost = signal.sosfilt(sos_hf, audio) * 0.1
            audio = audio + hf_boost
        
        return audio
    
    def _apply_reference_eq(self, audio: np.ndarray, sr: int, reference_params: Dict[str, float]) -> np.ndarray:
        """Apply EQ based on reference track spectral characteristics"""
        # Analyze current audio spectrum
        current_spectral = self.reference_analyzer._analyze_spectrum(audio, sr)
        
        # Calculate adjustments needed to match reference
        high_freq_ratio = reference_params["high_freq_energy"] / (current_spectral["high_freq_energy"] + 1e-10)
        low_freq_ratio = reference_params["low_freq_energy"] / (current_spectral["low_freq_energy"] + 1e-10)
        
        # Apply high frequency adjustment
        if high_freq_ratio > 1.2:  # Reference has more high freq energy
            sos_hf = signal.butter(2, [6000, 16000], btype='bandpass', fs=sr, output='sos')
            hf_boost = signal.sosfilt(sos_hf, audio) * min(0.2, (high_freq_ratio - 1.0) * 0.1)
            audio = audio + hf_boost
        elif high_freq_ratio < 0.8:  # Reference has less high freq energy
            sos_hf = signal.butter(2, 8000, btype='lowpass', fs=sr, output='sos')
            audio = signal.sosfilt(sos_hf, audio)
        
        # Apply low frequency adjustment
        if low_freq_ratio > 1.2:  # Reference has more low freq energy
            sos_lf = signal.butter(2, [80, 300], btype='bandpass', fs=sr, output='sos')
            lf_boost = signal.sosfilt(sos_lf, audio) * min(0.15, (low_freq_ratio - 1.0) * 0.1)
            audio = audio + lf_boost
            
        return audio
    
    def apply_compression(self, audio: np.ndarray, threshold: float = 0.7, ratio: float = 3.0, 
                         reference_params: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Apply dynamic range compression, optionally matching reference characteristics.
        
        Args:
            audio: Input audio array
            threshold: Compression threshold (0.0 to 1.0)
            ratio: Compression ratio
            reference_params: Optional reference track characteristics
            
        Returns:
            Compressed audio array
        """
        # Use reference-based compression parameters if available
        if reference_params:
            ratio = reference_params.get("compression_ratio", ratio)
            # Adjust threshold based on reference dynamic range
            ref_dr = reference_params.get("dynamic_range", 20.0)
            threshold = max(0.3, min(0.8, 0.9 - (ref_dr / 40.0)))
            
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
    
    def master_audio(self, audio: np.ndarray, sr: int, reference_audio: Optional[np.ndarray] = None, 
                    reference_sr: Optional[int] = None) -> np.ndarray:
        """
        Apply complete mastering chain, optionally matching a reference track.
        
        Args:
            audio: Input audio array
            sr: Sample rate
            reference_audio: Optional reference track audio array
            reference_sr: Optional reference track sample rate
            
        Returns:
            Mastered audio array
        """
        logger.info("Starting mastering process...")
        
        # Analyze reference track if provided
        reference_params = None
        if reference_audio is not None:
            logger.info("Analyzing reference track...")
            # Resample reference if needed
            if reference_sr != sr:
                reference_audio = librosa.resample(reference_audio, orig_sr=reference_sr, target_sr=sr)
            reference_params = self.analyze_reference(reference_audio, sr)
            logger.info(f"Reference analysis: LUFS={reference_params['target_lufs']:.1f}, "
                       f"DR={reference_params['dynamic_range']:.1f}dB, "
                       f"Compression={reference_params['compression_ratio']:.1f}")
        
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
        
        # Determine target LUFS (reference takes priority)
        target_lufs = reference_params["target_lufs"] if reference_params else self.target_lufs
        
        # Process each channel separately if stereo
        if len(original_shape) == 2:
            processed_channels = []
            for channel in range(original_shape[0]):
                ch_audio = audio[channel]
                ch_audio = self.apply_eq(ch_audio, sr, reference_params)
                ch_audio = self.apply_compression(ch_audio, reference_params=reference_params)
                ch_audio = self.loudness_normalize(ch_audio, sr, target_lufs)
                ch_audio = self.apply_limiter(ch_audio)
                processed_channels.append(ch_audio)
            audio = np.array(processed_channels)
        else:
            # Mono processing
            audio = self.apply_eq(audio, sr, reference_params)
            audio = self.apply_compression(audio, reference_params=reference_params)
            audio = self.loudness_normalize(audio, sr, target_lufs)
            audio = self.apply_limiter(audio)
        
        mastering_mode = "reference-based" if reference_params else "standard"
        logger.info(f"Mastering process completed using {mastering_mode} mastering")
        return audio
