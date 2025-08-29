#!/usr/bin/env python3
"""
TrackMaster Client Example with Reference Track Support

This script demonstrates how to use the TrackMaster API for audio mastering
with both standard and reference-based mastering.
"""

import requests
import argparse
from pathlib import Path


def master_audio_standard(server_url: str, input_file: str, target_lufs: float = -14.0, output_file: str = None):
    """
    Master audio using standard mastering (no reference track).
    
    Args:
        server_url: TrackMaster server URL
        input_file: Path to input audio file
        target_lufs: Target loudness in LUFS
        output_file: Output filename (optional)
    """
    endpoint = f"{server_url}/master"
    
    # Prepare files and data
    files = {'file': open(input_file, 'rb')}
    data = {'target_lufs': target_lufs}
    
    try:
        print(f"🎵 Mastering {input_file} (standard mastering, target: {target_lufs} LUFS)...")
        response = requests.post(endpoint, files=files, data=data)
        
        if response.status_code == 200:
            # Determine output filename
            if not output_file:
                base_name = Path(input_file).stem
                output_file = f"mastered_{base_name}.wav"
            
            # Save the mastered audio
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # Print response headers for info
            session_id = response.headers.get('X-Session-ID', 'unknown')
            mastering_mode = response.headers.get('X-Mastering-Mode', 'unknown')
            
            print(f"✅ Standard mastering completed!")
            print(f"   Output: {output_file}")
            print(f"   Session ID: {session_id}")
            print(f"   Mode: {mastering_mode}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        files['file'].close()


def master_audio_with_reference(server_url: str, input_file: str, reference_file: str, output_file: str = None):
    """
    Master audio using reference track matching.
    
    Args:
        server_url: TrackMaster server URL
        input_file: Path to input audio file
        reference_file: Path to reference audio file
        output_file: Output filename (optional)
    """
    endpoint = f"{server_url}/master"
    
    # Prepare files
    files = {
        'file': open(input_file, 'rb'),
        'reference_file': open(reference_file, 'rb')
    }
    
    try:
        print(f"🎵 Mastering {input_file} with reference {reference_file}...")
        response = requests.post(endpoint, files=files)
        
        if response.status_code == 200:
            # Determine output filename
            if not output_file:
                base_name = Path(input_file).stem
                ref_name = Path(reference_file).stem
                output_file = f"mastered_{base_name}_ref-{ref_name}.wav"
            
            # Save the mastered audio
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # Print response headers for info
            session_id = response.headers.get('X-Session-ID', 'unknown')
            mastering_mode = response.headers.get('X-Mastering-Mode', 'unknown')
            reference_used = response.headers.get('X-Reference-Used', 'false')
            
            print(f"✅ Reference-based mastering completed!")
            print(f"   Output: {output_file}")
            print(f"   Session ID: {session_id}")
            print(f"   Mode: {mastering_mode}")
            print(f"   Reference used: {reference_used}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        files['file'].close()
        files['reference_file'].close()


def check_server_health(server_url: str):
    """Check if the TrackMaster server is running."""
    try:
        response = requests.get(f"{server_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"🟢 Server is healthy!")
            print(f"   Service: {health_data.get('service', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
            print(f"   Supported formats: {health_data.get('supported_formats', [])}")
            return True
        else:
            print(f"🔴 Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"🔴 Cannot reach server: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="TrackMaster Client with Reference Track Support")
    parser.add_argument("input_file", help="Input audio file to master")
    parser.add_argument("--server", default="http://localhost:8000", help="TrackMaster server URL")
    parser.add_argument("--reference", help="Reference track file for matching characteristics")
    parser.add_argument("--target-lufs", type=float, default=-14.0, 
                       help="Target LUFS for standard mastering (ignored with reference)")
    parser.add_argument("--output", help="Output filename (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input_file).exists():
        print(f"❌ Input file not found: {args.input_file}")
        return
    
    # Check if reference file exists (if specified)
    if args.reference and not Path(args.reference).exists():
        print(f"❌ Reference file not found: {args.reference}")
        return
    
    print("🎛️  TrackMaster Client - AI Audio Mastering")
    print("=" * 45)
    
    # Check server health
    if not check_server_health(args.server):
        return
    
    print()
    
    # Perform mastering
    if args.reference:
        master_audio_with_reference(args.server, args.input_file, args.reference, args.output)
    else:
        master_audio_standard(args.server, args.input_file, args.target_lufs, args.output)


if __name__ == "__main__":
    main()
