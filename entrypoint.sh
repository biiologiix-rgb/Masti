#!/usr/bin/env bash
set -e

# Default PORT locally; Railway provides PORT automatically
export PORT="${PORT:-8000}"

# Gunicorn: 2 workers keeps memory low; thread worker helps with I/O
exec gunicorn -w 2 -k gthread -b 0.0.0.0:${PORT} run:app
