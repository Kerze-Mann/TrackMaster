#!/usr/bin/env python3
"""
Test script for reference track mastering functionality
"""

import numpy as np
import soundfile as sf
import tempfile
import os
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from trackmaster.mastering import AudioMasteringEngine


def create_test_audio(duration=3.0, sample_rate=44100, frequency=440.0):
    """Create a simple test audio signal"""
    t = np.linspace(0, duration, int(duration * sample_rate))
    # Create a simple tone with some harmonics
    audio = (np.sin(2 * np.pi * frequency * t) * 0.5 + 
             np.sin(2 * np.pi * frequency * 2 * t) * 0.2 +
             np.sin(2 * np.pi * frequency * 3 * t) * 0.1)
    return audio


def test_reference_mastering():
    """Test the reference track mastering functionality"""
    print("🧪 Testing Reference Track Mastering")
    print("=" * 40)
    
    # Create mastering engine
    engine = AudioMasteringEngine()
    
    # Create test audio signals
    print("📢 Creating test audio signals...")
    
    # Input audio (needs mastering)
    input_audio = create_test_audio(duration=2.0, frequency=440.0) * 0.3  # Quiet
    
    # Reference audio (well-mastered)
    reference_audio = create_test_audio(duration=2.0, frequency=440.0) * 0.8  # Louder
    
    sample_rate = 44100
    
    # Test 1: Standard mastering (no reference)
    print("\n🎵 Test 1: Standard mastering...")
    mastered_standard = engine.master_audio(input_audio.copy(), sample_rate)
    
    standard_lufs = engine.calculate_lufs(mastered_standard, sample_rate)
    print(f"   Standard mastering LUFS: {standard_lufs:.1f}")
    
    # Test 2: Reference-based mastering
    print("\n🎯 Test 2: Reference-based mastering...")
    mastered_reference = engine.master_audio(
        input_audio.copy(), sample_rate,
        reference_audio=reference_audio, reference_sr=sample_rate
    )
    
    reference_lufs = engine.calculate_lufs(mastered_reference, sample_rate)
    print(f"   Reference-based mastering LUFS: {reference_lufs:.1f}")
    
    # Test 3: Analyze reference characteristics
    print("\n🔍 Test 3: Reference analysis...")
    ref_params = engine.analyze_reference(reference_audio, sample_rate)
    print(f"   Reference LUFS: {ref_params['target_lufs']:.1f}")
    print(f"   Reference Dynamic Range: {ref_params['dynamic_range']:.1f} dB")
    print(f"   Reference Compression Ratio: {ref_params['compression_ratio']:.1f}")
    print(f"   Reference Peak Level: {ref_params['peak_level']:.3f}")
    
    # Save test files for manual inspection
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save test files
        sf.write(temp_path / "input.wav", input_audio, sample_rate)
        sf.write(temp_path / "reference.wav", reference_audio, sample_rate)
        sf.write(temp_path / "mastered_standard.wav", mastered_standard, sample_rate)
        sf.write(temp_path / "mastered_reference.wav", mastered_reference, sample_rate)
        
        print(f"\n📁 Test files saved to: {temp_dir}")
        print("   - input.wav (original)")
        print("   - reference.wav (reference track)")
        print("   - mastered_standard.wav (standard mastering)")
        print("   - mastered_reference.wav (reference-based mastering)")
        
        # Keep temp directory for manual inspection
        input("Press Enter to continue (files will be deleted)...")
    
    print("\n✅ Reference mastering test completed!")
    print(f"Standard mastering produced: {standard_lufs:.1f} LUFS")
    print(f"Reference mastering produced: {reference_lufs:.1f} LUFS")
    
    # Basic validation
    if abs(reference_lufs - ref_params['target_lufs']) < 2.0:
        print("✅ Reference matching appears to be working correctly!")
    else:
        print("⚠️  Reference matching may need adjustment")


if __name__ == "__main__":
    test_reference_mastering()
