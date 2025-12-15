import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Database Configuration
# -------------------------
# Uses PostgreSQL on EC2 if DATABASE_URL is set,
# otherwise falls back to local SQLite (for safety)
SQLALCHEMY_DATABASE_URI = (
    os.getenv("DATABASE_URL", "sqlite:///default.db")
    .replace("postgres://", "postgresql://")
)

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# -------------------------
# Email Configuration
# -------------------------
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

# -------------------------
# Cloudinary Configuration
# -------------------------
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# -------------------------
# Attendance Rules
# -------------------------
ATTENDANCE_THRESHOLD_HOUR = int(
    os.environ.get("ATTENDANCE_THRESHOLD_HOUR", 9)
)
