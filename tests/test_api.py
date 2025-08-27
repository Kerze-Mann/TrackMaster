#!/usr/bin/env python3
"""
Test script for TrackMaster API
"""

import requests
import numpy as np
import soundfile as sf
import tempfile
import os
import sys

def create_test_audio(duration=5, sample_rate=44100):
    """Create a simple test audio file"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a simple sine wave with some harmonics
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # A4 note
    audio += 0.1 * np.sin(2 * np.pi * 880 * t)  # A5 note
    audio += 0.05 * np.sin(2 * np.pi * 1320 * t)  # E6 note
    return audio, sample_rate

def test_api(server_url="http://localhost:8000"):
    """Test the TrackMaster API"""
    
    print("🎵 TrackMaster API Test")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Create test audio file
    print("\n2. Creating test audio file...")
    audio, sr = create_test_audio()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        sf.write(temp_file.name, audio, sr)
        test_file_path = temp_file.name
    
    print(f"✅ Test audio created: {test_file_path}")
    
    # Test mastering endpoint
    print("\n3. Testing mastering endpoint...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {'target_lufs': -16.0}
            
            print("   Uploading and processing...")
            response = requests.post(f"{server_url}/master", files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Mastering completed successfully")
                
                # Save the result
                output_path = "test_mastered_output.wav"
                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)
                
                print(f"   Mastered file saved: {output_path}")
                
                # Verify the output file
                try:
                    mastered_audio, mastered_sr = sf.read(output_path)
                    print(f"   Output audio shape: {mastered_audio.shape}")
                    print(f"   Output sample rate: {mastered_sr}")
                    print(f"   Output peak level: {np.max(np.abs(mastered_audio)):.3f}")
                except Exception as e:
                    print(f"   Warning: Could not analyze output file: {e}")
                
            else:
                print(f"❌ Mastering failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Mastering error: {e}")
        return False
    finally:
        # Cleanup test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing server at: {server_url}")
    success = test_api(server_url)
    
    if not success:
        sys.exit(1)
