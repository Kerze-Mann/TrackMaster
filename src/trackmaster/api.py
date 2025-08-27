"""
FastAPI application for TrackMaster audio mastering service.
"""

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import soundfile as sf
import tempfile
import uuid
from pathlib import Path
import logging
from typing import Optional

from .mastering import AudioMasteringEngine

logger = logging.getLogger(__name__)

# Get version from environment or package
VERSION = os.getenv("TRACKMASTER_VERSION", "1.0.0")

# Create directories for temporary files
UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="TrackMaster AI Audio Mastering Server",
        description="AI-powered audio mastering service for WAV and MP3 files",
        version=VERSION
    )

    # Initialize mastering engine
    mastering_engine = AudioMasteringEngine()

    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {"message": "TrackMaster AI Audio Mastering Server", "status": "running"}

    @app.get("/health")
    async def health_check():
        """Detailed health check"""
        return {
            "status": "healthy",
            "service": "TrackMaster",
            "version": VERSION,
            "supported_formats": ["wav", "mp3", "flac", "m4a"]
        }

    @app.post("/master")
    async def master_audio(
        file: UploadFile = File(...),
        target_lufs: Optional[float] = -14.0
    ):
        """
        Master an audio file using AI-powered processing
        
        - **file**: Audio file (WAV, MP3, FLAC, M4A)
        - **target_lufs**: Target loudness in LUFS (default: -14.0)
        """
        # Validate file type
        allowed_extensions = {".wav", ".mp3", ".flac", ".m4a"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique IDs for files
        session_id = str(uuid.uuid4())
        input_filename = f"{session_id}_input{file_extension}"
        output_filename = f"{session_id}_mastered.wav"
        
        input_path = UPLOAD_DIR / input_filename
        output_path = OUTPUT_DIR / output_filename
        
        try:
            # Save uploaded file
            with open(input_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"Processing file: {file.filename} -> {output_filename}")
            
            # Load and process audio
            audio, sr = mastering_engine.load_audio(str(input_path))
            
            # Update target LUFS if provided
            mastering_engine.target_lufs = target_lufs
            
            # Apply mastering
            mastered_audio = mastering_engine.master_audio(audio, sr)
            
            # Save mastered audio
            sf.write(str(output_path), mastered_audio.T if len(mastered_audio.shape) == 2 else mastered_audio, sr)
            
            logger.info(f"Mastering completed: {output_filename}")
            
            # Return the mastered file
            return FileResponse(
                path=str(output_path),
                filename=f"mastered_{Path(file.filename).stem}.wav",
                media_type="audio/wav",
                headers={"X-Session-ID": session_id}
            )
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
        
        finally:
            # Cleanup input file
            if input_path.exists():
                input_path.unlink()

    @app.delete("/cleanup/{session_id}")
    async def cleanup_session(session_id: str):
        """Clean up files for a specific session"""
        try:
            # Remove output files for this session
            for file_path in OUTPUT_DIR.glob(f"{session_id}_*"):
                file_path.unlink()
            
            return {"message": f"Session {session_id} cleaned up successfully"}
        
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            raise HTTPException(status_code=500, detail="Cleanup failed")

    return app
