"""
FastAPI application for TrackMaster audio mastering service.
"""

import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
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
        reference_file: Optional[UploadFile] = File(None),
        target_lufs: Optional[float] = Form(-14.0)
    ):
        """
        Master an audio file using AI-powered processing
        
        - **file**: Audio file to master (WAV, MP3, FLAC, M4A)
        - **reference_file**: Optional reference track to match characteristics (WAV, MP3, FLAC, M4A)
        - **target_lufs**: Target loudness in LUFS (default: -14.0, ignored if reference provided)
        """
        # Validate file types
        allowed_extensions = {".wav", ".mp3", ".flac", ".m4a"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported formats: {', '.join(allowed_extensions)}"
            )
        
        # Validate reference file if provided
        reference_extension = None
        if reference_file and reference_file.filename:
            reference_extension = Path(reference_file.filename).suffix.lower()
            if reference_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported reference file format. Supported formats: {', '.join(allowed_extensions)}"
                )
        
        # Generate unique IDs for files
        session_id = str(uuid.uuid4())
        input_filename = f"{session_id}_input{file_extension}"
        reference_filename = f"{session_id}_reference{reference_extension}" if reference_file else None
        output_filename = f"{session_id}_mastered.wav"
        
        input_path = UPLOAD_DIR / input_filename
        reference_path = UPLOAD_DIR / reference_filename if reference_filename else None
        output_path = OUTPUT_DIR / output_filename
        
        try:
            # Save uploaded input file
            with open(input_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Save reference file if provided
            reference_audio = None
            reference_sr = None
            if reference_file and reference_file.filename:
                with open(reference_path, "wb") as buffer:
                    content = await reference_file.read()
                    buffer.write(content)
                
                # Load reference audio
                reference_audio, reference_sr = mastering_engine.load_audio(str(reference_path))
                logger.info(f"Loaded reference track: {reference_file.filename}")
            
            mastering_mode = "reference-based" if reference_audio is not None else "standard"
            logger.info(f"Processing file: {file.filename} -> {output_filename} ({mastering_mode} mastering)")
            
            # Load and process main audio
            audio, sr = mastering_engine.load_audio(str(input_path))
            
            # Update target LUFS if provided and no reference (reference LUFS takes priority)
            if reference_audio is None:
                mastering_engine.target_lufs = target_lufs
            
            # Apply mastering (with or without reference)
            mastered_audio = mastering_engine.master_audio(
                audio, sr, 
                reference_audio=reference_audio, 
                reference_sr=reference_sr
            )
            
            # Save mastered audio
            sf.write(str(output_path), mastered_audio.T if len(mastered_audio.shape) == 2 else mastered_audio, sr)
            
            logger.info(f"Mastering completed: {output_filename} ({mastering_mode})")
            
            # Prepare response filename
            base_filename = Path(file.filename).stem
            ref_suffix = "_ref-matched" if reference_audio is not None else ""
            response_filename = f"mastered_{base_filename}{ref_suffix}.wav"
            
            # Return the mastered file
            return FileResponse(
                path=str(output_path),
                filename=response_filename,
                media_type="audio/wav",
                headers={
                    "X-Session-ID": session_id,
                    "X-Mastering-Mode": mastering_mode,
                    "X-Reference-Used": "true" if reference_audio is not None else "false"
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
        
        finally:
            # Cleanup input files
            if input_path.exists():
                input_path.unlink()
            if reference_path and reference_path.exists():
                reference_path.unlink()

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
