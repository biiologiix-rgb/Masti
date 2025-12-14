# Use Python 3.10 (stable + compatible with dlib & face_recognition)
FROM python:3.10-slim-bullseye

# Install system dependencies for dlib, face_recognition & OpenCV
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose Render's default port
EXPOSE 10000

# Start Gunicorn (Render injects PORT automatically)
CMD gunicorn run:app --bind 0.0.0.0:$PORT
