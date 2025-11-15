# Use Python 3.9 (compatible with dlib & face_recognition)
FROM python:3.9-slim-bullseye

# Install system dependencies for dlib & face_recognition
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Expose port (Railway overrides with $PORT)
EXPOSE 5000

# Start Gunicorn server
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000"]
