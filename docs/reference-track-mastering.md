# Reference Track Mastering

TrackMaster now supports reference track mastering, allowing you to match the sonic characteristics of a professionally mastered reference track.

## Overview

Reference track mastering analyzes the spectral, dynamic, and loudness characteristics of a reference track and applies similar processing to your input audio. This ensures consistency with professionally mastered tracks or allows you to match a specific sound aesthetic.

## How It Works

### 1. Reference Analysis
When a reference track is provided, TrackMaster analyzes:

- **Loudness (LUFS)**: Target loudness level
- **Dynamic Range**: Compression characteristics
- **Spectral Balance**: High and low frequency energy distribution
- **Peak Levels**: Maximum signal level
- **Compression Ratio**: Estimated compression characteristics

### 2. Adaptive Processing
The mastering chain adapts based on reference characteristics:

- **EQ Matching**: Adjusts frequency balance to match reference
- **Dynamic Processing**: Applies compression ratios derived from reference
- **Loudness Targeting**: Matches reference LUFS instead of default -14.0

### 3. Fallback Behavior
If no reference is provided, TrackMaster uses standard mastering with configurable target LUFS.

## API Usage

### Standard Mastering (No Reference)
```bash
curl -X POST "http://localhost:8000/master" \
     -F "file=@input.wav" \
     -F "target_lufs=-14.0" \
     --output mastered_output.wav
```

### Reference-Based Mastering
```bash
curl -X POST "http://localhost:8000/master" \
     -F "file=@input.wav" \
     -F "reference_file=@reference.wav" \
     --output mastered_output.wav
```

**Note**: When using a reference file, the `target_lufs` parameter is ignored as the reference track's loudness is used instead.

## Client Examples

### Python Client
```python
import requests

# Standard mastering
with open('input.wav', 'rb') as f:
    files = {'file': f}
    data = {'target_lufs': -14.0}
    response = requests.post('http://localhost:8000/master', files=files, data=data)

# Reference-based mastering
with open('input.wav', 'rb') as input_file, \
     open('reference.wav', 'rb') as ref_file:
    files = {'file': input_file, 'reference_file': ref_file}
    response = requests.post('http://localhost:8000/master', files=files)
```

### Command Line Client
```bash
# Standard mastering
python examples/client_reference_example.py input.wav --target-lufs -16.0

# Reference-based mastering  
python examples/client_reference_example.py input.wav --reference reference.wav
```

## Response Headers

TrackMaster provides additional information in response headers:

- `X-Session-ID`: Unique session identifier
- `X-Mastering-Mode`: Either "standard" or "reference-based"
- `X-Reference-Used`: "true" if reference was provided and used

## Supported Reference Formats

Reference files support the same formats as input files:
- WAV (recommended for best analysis)
- MP3
- FLAC  
- M4A

## Best Practices

### Choosing Reference Tracks
1. **Genre Matching**: Use references from the same or similar genre
2. **Professional Masters**: Use commercially released, professionally mastered tracks
3. **Similar Instrumentation**: Choose references with similar frequency content
4. **Target Platform**: Match reference to intended playback platform (streaming, CD, etc.)

### Quality Considerations
- **Use High-Quality References**: WAV or FLAC preferred over MP3
- **Full-Length Tracks**: Avoid short clips that may not represent the full master
- **Avoid Over-Processed**: References that are too heavily compressed may lead to poor results

### When to Use Reference Mastering
- ✅ **Matching Album Consistency**: Ensure all tracks in an album have similar characteristics
- ✅ **Genre Standards**: Match established sonic conventions for your genre  
- ✅ **Client Requests**: When clients provide specific reference material
- ✅ **Streaming Optimization**: Match references optimized for streaming platforms

### When to Use Standard Mastering
- ✅ **Creative Independence**: When developing your own unique sound
- ✅ **No Suitable Reference**: When you can't find an appropriate reference track
- ✅ **Standard Targets**: When aiming for broadcast/streaming standard (-14 LUFS)

## Technical Details

### Reference Analysis Algorithm
```python
# Extracted characteristics include:
{
    "target_lufs": -12.5,           # Reference loudness
    "dynamic_range": 8.2,           # Dynamic range in dB
    "peak_level": 0.95,             # Maximum peak level
    "spectral_centroid": 2847.3,    # Spectral center frequency
    "spectral_rolloff": 8245.1,     # High frequency rolloff
    "high_freq_energy": 0.23,       # High frequency content
    "low_freq_energy": 0.45,        # Low frequency content  
    "compression_ratio": 4.2        # Estimated compression
}
```

### Processing Adaptations
1. **EQ Adjustments**: 
   - High frequency boost/cut based on spectral analysis
   - Low frequency adjustments for balance matching
   
2. **Compression Matching**:
   - Threshold adjusted based on reference dynamic range
   - Ratio derived from reference compression characteristics
   
3. **Loudness Targeting**:
   - Target LUFS set to reference level
   - Peak limiting maintains headroom

## Limitations

- **Genre Differences**: References from very different genres may not work well
- **Quality Dependency**: Poor quality references will lead to suboptimal results  
- **Algorithm Approximations**: Spectral and dynamic analysis uses simplified algorithms
- **No Stereo Width Matching**: Currently doesn't analyze or match stereo field characteristics

## Future Enhancements

Planned improvements for reference track mastering:

- 🔄 **Improved Spectral Analysis**: More sophisticated frequency matching
- 🔄 **Stereo Field Matching**: Analyze and match stereo width characteristics  
- 🔄 **Multi-Reference Support**: Blend characteristics from multiple references
- 🔄 **Genre-Specific Presets**: Pre-analyzed reference characteristics for common genres
- 🔄 **Machine Learning**: AI-powered characteristic extraction and matching

## Examples

### Album Mastering Workflow
```bash
# Master all tracks with the same reference for consistency
for track in *.wav; do
    python examples/client_reference_example.py "$track" \
        --reference "lead_single_master.wav" \
        --output "mastered_${track}"
done
```

### A/B Testing
```bash
# Compare standard vs reference mastering
python examples/client_reference_example.py input.wav \
    --output mastered_standard.wav

python examples/client_reference_example.py input.wav \
    --reference professional_reference.wav \
    --output mastered_reference.wav
```

This feature significantly enhances TrackMaster's capabilities by providing professional-grade reference matching for consistent, high-quality masters.
