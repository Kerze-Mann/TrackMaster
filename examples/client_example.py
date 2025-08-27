#!/usr/bin/env python3
"""
Example client for TrackMaster API
Usage: python client_example.py input_audio.wav [target_lufs]
"""

import requests
import sys
import os
from pathlib import Path

def master_audio_file(input_file, output_file=None, target_lufs=-14.0, server_url="http://localhost:8000"):
    """
    Master an audio file using TrackMaster API
    
    Args:
        input_file (str): Path to input audio file
        output_file (str): Path for output file (optional)
        target_lufs (float): Target loudness in LUFS
        server_url (str): TrackMaster server URL
    """
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        input_path = Path(input_file)
        output_file = f"mastered_{input_path.stem}.wav"
    
    print(f"🎵 Mastering: {input_file}")
    print(f"📊 Target LUFS: {target_lufs}")
    print(f"💾 Output: {output_file}")
    print(f"🌐 Server: {server_url}")
    print("-" * 50)
    
    try:
        # Check server health
        print("🏥 Checking server health...")
        health_response = requests.get(f"{server_url}/health", timeout=10)
        if health_response.status_code != 200:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return False
        print("✅ Server is healthy")
        
        # Upload and process file
        print("📤 Uploading and processing file...")
        with open(input_file, 'rb') as f:
            files = {'file': f}
            data = {'target_lufs': target_lufs}
            
            response = requests.post(
                f"{server_url}/master", 
                files=files, 
                data=data,
                timeout=300  # 5 minutes timeout for processing
            )
        
        if response.status_code == 200:
            # Save the mastered file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Mastering completed successfully!")
            print(f"📁 Output saved to: {output_file}")
            
            # Get file size info
            input_size = os.path.getsize(input_file)
            output_size = os.path.getsize(output_file)
            print(f"📊 Input size: {input_size:,} bytes")
            print(f"📊 Output size: {output_size:,} bytes")
            
            return True
        else:
            print(f"❌ Mastering failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The file might be too large or the server is overloaded.")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {server_url}")
        print("Make sure the TrackMaster server is running.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python client_example.py <input_audio_file> [target_lufs] [server_url]")
        print("Example: python client_example.py my_song.wav -16.0")
        sys.exit(1)
    
    input_file = sys.argv[1]
    target_lufs = float(sys.argv[2]) if len(sys.argv) > 2 else -14.0
    server_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
    
    success = master_audio_file(input_file, target_lufs=target_lufs, server_url=server_url)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
