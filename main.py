#!/usr/bin/env python3

import os
import tempfile
import logging
import warnings
from typing import Dict

import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# Logging configuration
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("whisper-service")

# ----------------------------
# FastAPI app initialization
# ----------------------------
app = FastAPI(
    title="Whisper Transcription Service",
    description="A FastAPI microservice for audio transcription using OpenAI Whisper",
    version="1.0.0",
)

# Configure CORS (customize for your frontend domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://yourfrontend.com"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Model initialization
# ----------------------------
model = None


@app.on_event("startup")
async def load_whisper_model():
    """Load the Whisper model once on service startup."""
    global model
    try:
        warnings.filterwarnings("ignore")
        logger.info("Loading Whisper model: base ...")
        model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully ✅")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise RuntimeError("Whisper model could not be loaded") from e


# ----------------------------
# Routes
# ----------------------------
@app.get("/")
async def root() -> Dict:
    """Basic health check endpoint."""
    return {"message": "Whisper Transcription Service is running", "status": "healthy"}


@app.get("/health")
async def health_check() -> Dict:
    """Detailed health check endpoint."""
    return {
        "status": "healthy" if model else "unhealthy",
        "service": "whisper-transcription",
        "model_loaded": model is not None,
        "version": "1.0.0",
    }


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        file: Audio file (supports mp3, wav, webm, m4a, ogg, flac)

    Returns:
        JSON response with transcription and language.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Whisper model not loaded")

    allowed_types = [
        "audio/mpeg",
        "audio/wav",
        "audio/webm",
        "audio/mp4",
        "audio/ogg",
        "audio/flac",
        "audio/x-flac",
    ]
    allowed_extensions = [".mp3", ".wav", ".webm", ".m4a", ".ogg", ".flac"]

    # Validate file type
    if (
        file.content_type not in allowed_types
        and not any(file.filename.lower().endswith(ext) for ext in allowed_extensions)
    ):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a valid audio file (mp3, wav, webm, m4a, ogg, flac).",
        )

    temp_file = None
    try:
        # Save uploaded file to a temporary location
        contents = await file.read()
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".tmp"

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.write(contents)
        temp_file.close()

        logger.info(f"Transcribing file: {file.filename} (size: {len(contents)} bytes)")

        # Transcribe audio
        result = model.transcribe(temp_file.name)

        response = {
            "filename": file.filename,
            "transcription": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "success": True,
        }

        logger.info(f"Transcription completed for {file.filename}")
        return response

    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")

    finally:
        # Ensure temp file cleanup
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception as cleanup_err:
                logger.warning(f"Failed to clean up temporary file: {cleanup_err}")


# ----------------------------
# Run with Uvicorn
# ----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
