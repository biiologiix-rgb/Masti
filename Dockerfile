# Use Python 3.9 (best compatibility + lower memory for dlib)
FROM python:3.9-slim-bullseye

# -------------------------------
# 🔧 Reduce memory usage for dlib
# -------------------------------
ENV MAKEFLAGS="-j1"
ENV MAX_JOBS=1
ENV CMAKE_ARGS="-DDLIB_USE_CUDA=0"
ENV PYTHONUNBUFFERED=1

# -------------------------------
# 📦 System dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# 📁 App directory
# -------------------------------
WORKDIR /app

# -------------------------------
# 🐍 Python dependencies
# -------------------------------
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# Install dlib FIRST (single-threaded, no cache)
RUN pip install dlib==19.24.0 --no-cache-dir

# Install remaining requirements
RUN pip install -r requirements.txt --no-cache-dir

# -------------------------------
# 📄 Copy project files
# -------------------------------
COPY . .

# -------------------------------
# 🌐 Expose port (Render provides $PORT)
# -------------------------------
EXPOSE 10000

# -------------------------------
# ▶ Start application
# -------------------------------
CMD gunicorn run:app --bind 0.0.0.0:$PORT
