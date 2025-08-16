#!/usr/bin/env python3

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import warnings
import tempfile
import os
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Whisper Transcription Service",
    description="A FastAPI microservice for audio transcription using OpenAI Whisper",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to hold the model (loaded once at startup)
model = None

@app.on_event("startup")
async def startup_event():
    """Load the Whisper model on startup to avoid loading delay on first request"""
    global model
    try:
        warnings.filterwarnings("ignore")
        logger.info("Loading Whisper model...")
        model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Whisper Transcription Service is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "whisper-transcription",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict:
    """
    Transcribe an audio file using Whisper
    
    Args:
        file: Audio file (supports mp3, wav, webm, m4a, ogg, flac)
    
    Returns:
        JSON response with transcription, language, and success status
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Whisper model not loaded")
    
    # Validate file type
    allowed_types = [
        "audio/mpeg", "audio/wav", "audio/webm", "audio/mp4", 
        "audio/ogg", "audio/flac", "audio/x-flac"
    ]
    allowed_extensions = [".mp3", ".wav", ".webm", ".m4a", ".ogg", ".flac"]
    
    if (file.content_type not in allowed_types and 
        not any(file.filename.lower().endswith(ext) for ext in allowed_extensions)):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload an audio file (mp3, wav, webm, m4a, ogg, flac)"
        )
    
    # Create temporary file to store uploaded audio
    temp_file = None
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Create a temporary file with the original extension
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".tmp"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.write(contents)
        temp_file.close()
        
        logger.info(f"Transcribing file: {file.filename} (size: {len(contents)} bytes)")
        
        # Transcribe the audio file
        result = model.transcribe(temp_file.name)
        
        # Return the transcription result
        response = {
            "transcription": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "success": True,
            "filename": file.filename
        }
        
        logger.info(f"Transcription completed for {file.filename}")
        return response
        
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during transcription: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)