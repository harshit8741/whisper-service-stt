#!/usr/bin/env python3

import sys
import os
import whisper
import warnings
import json

def main():
    if len(sys.argv) != 2:
        error_response = {
            "error": "Usage: python transcribe.py <audio_file_path>",
            "success": False
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)
    
    audio_file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        error_response = {
            "error": f"Audio file '{audio_file_path}' not found",
            "success": False
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Suppress warnings for cleaner output
        warnings.filterwarnings("ignore")
        
        # Load Whisper model (base for performance)
        model = whisper.load_model("base")
        
        # Transcribe the audio file
        result = model.transcribe(audio_file_path)
        
        # Output JSON response to stdout
        response = {
            "transcription": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "success": True
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            "error": f"Error during transcription: {str(e)}",
            "success": False
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()