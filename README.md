# Whisper Transcription Microservice

A FastAPI-based microservice for audio transcription using OpenAI Whisper.

## Features

- RESTful API for audio transcription
- Support for multiple audio formats (MP3, WAV, WebM, M4A, OGG, FLAC)
- Dockerized deployment
- Health check endpoints
- CORS support for web applications

## API Endpoints

### POST /transcribe
Transcribe an audio file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Audio file as form data with key 'file'

**Response:**
```json
{
  "transcription": "Your transcribed text here",
  "language": "en",
  "success": true,
  "filename": "audio.mp3"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "whisper-transcription",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### GET /
Basic status endpoint.

**Response:**
```json
{
  "message": "Whisper Transcription Service is running",
  "status": "healthy"
}
```

## Development

### Local Development
```bash
pip install -r requirements.txt
python main.py
```

### Docker Development
```bash
# Build the image
docker build -t whisper-service .

# Run the container
docker run -p 8000:8000 whisper-service
```

### Testing
```bash
# Test with curl
curl -X POST "http://localhost:8000/transcribe" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-audio-file.mp3"
```

## Configuration

The service runs on port 8000 by default. You can modify this in the `main.py` file or by overriding the CMD in Docker.

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- WebM (.webm)
- M4A (.m4a)
- OGG (.ogg)
- FLAC (.flac)