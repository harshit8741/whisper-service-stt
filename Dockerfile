# Use Python 3.10 slim image for smaller footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies (make sure numpy is there)
RUN pip install --no-cache-dir -r requirements.txt

# OPTIONAL: Pre-download the Whisper model (comment this if Railway builds timeout)
# RUN python3 -c "import whisper; whisper.load_model('base')"

# Copy the FastAPI application
COPY main.py /app/main.py

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
