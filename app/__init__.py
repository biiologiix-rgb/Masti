import os
from pathlib import Path
from datetime import datetime, date as dt_date
import cloudinary.api
import os
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import base64
import io
from PIL import Image
import numpy as np
import face_recognition
import traceback

from flask import (
    Flask, render_template, redirect, url_for, request, flash,
    send_from_directory, jsonify, session, make_response, current_app
)
from flask_login import LoginManager
import pytz
import re
import random
import smtplib
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler

from app.extensions import db


# -----------------------
# Email helpers
# -----------------------
def send_verification_email(to_email, code):
    """Send verification email with security enhancements"""
    msg = MIMEText(f"Your verification code is: {code}")
    msg['Subject'] = "Your Email Verification Code"
    msg['From'] = os.environ.get('EMAIL_SENDER')
    msg['To'] = to_email

    try:
        with smtplib.SMTP(os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
                          int(os.environ.get('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.environ.get('EMAIL_SENDER'), os.environ.get('EMAIL_PASSWORD'))
            server.sendmail(os.environ.get('EMAIL_SENDER'), [to_email], msg.as_string())
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {str(e)}")


def send_absent_email(to_email, student_name, date_str):
    """Send absence notification email"""
    msg = MIMEText(
        f"Dear {student_name},\n\nYou have been marked as ABSENT for {date_str}.\n\n- Attendance Team"
    )
    msg['Subject'] = f"Absence Notification for {date_str}"
    msg['From'] = os.environ.get('EMAIL_SENDER')
    msg['To'] = to_email

    try:
        with smtplib.SMTP(os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
                          int(os.environ.get('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.environ.get('EMAIL_SENDER'), os.environ.get('EMAIL_PASSWORD'))
            server.sendmail(os.environ.get('EMAIL_SENDER'), [to_email], msg.as_string())
    except Exception as e:
        current_app.logger.error(f"Failed to send absent email: {str(e)}")


def create_app():
    # Import config after app module path is established
    from app import config

    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

    # --- Core config ---
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Cloudinary config (read from environment / Railway variables) ---
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )

    # Local file storage (still used for fallbacks if you want)
    app.config['UPLOAD_FOLDER'] = str(Path(app.root_path) / "faces")
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    # Init extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    # Import models AFTER db.init_app
    from app.models.models import User, Attendance , Student

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.attendance_scan import attendance_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)

    # Create tables on boot (works locally; on hosted Postgres it's fine too)
    with app.app_context():
        db.create_all()

    # --------- Health check (DB ping) ----------
    @app.route("/health")
    def health_check():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected", "timestamp": datetime.utcnow().isoformat()}), 200
        except Exception as e:
            current_app.logger.error(f"Health check failure: {e}")
            return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500

    # --------- Core routes ----------
    @app.route('/')
    def home():
        response = make_response(render_template('home.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/faces/<filename>')
    def serve_face(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/dashboard')
    def dashboard():
        date_str = request.args.get('date')
        filter_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
        users = db.session.query(User).filter(
            db.func.date(User.created_at) == filter_date
        ).order_by(User.created_at.desc()).all()

        return render_template(
            'dashboard.html',
            users=users,
            selected_date=filter_date.strftime("%Y-%m-%d"),
            today=dt_date.today().strftime("%Y-%m-%d")
        )

    @app.route('/register', methods=['GET'])
    @app.route('/register.html')
    def register():
        return render_template('register.html')

    # --- Email verification with code ---
    @app.route('/send-verification-code', methods=['POST'])
    def send_verification_code_route():
        email = request.form.get('email')
        code = str(random.randint(100000, 999999))
        session['email_verification_code'] = code
        session['email_to_verify'] = email
        send_verification_email(email, code)
        return jsonify({'success': True, 'message': 'Verification code sent to your email.'})

    @app.route('/verify-code', methods=['POST'])
    def verify_code():
        code = request.form.get('code')
        if code == session.get('email_verification_code'):
            session['email_verified'] = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid verification code.'})

    from app.vision.camera import capture_and_store_face

    @app.route('/register-face', methods=['POST'])
    def register_face():
        try:
            if not session.get('email_verified'):
                return jsonify(success=False, message="Please verify your email before registering your face.")

            # --- Validate inputs ---
            username = (request.form.get('username') or "").strip().title()
            if not username or not re.fullmatch(r'[A-Za-z ]{1,20}', username):
                return jsonify(success=False, message="Name can only contain letters and spaces (max 20).")

            try:
                roll = int(request.form.get('roll', ''))
                if roll <= 0:
                    raise ValueError()
            except ValueError:
                return jsonify(success=False, message="Roll number must be a positive integer.")

            email = (request.form.get('email') or "").strip()
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', email):
                return jsonify(success=False, message="Enter a valid email that starts with a letter.")

            if db.session.query(User).filter_by(email=email).first():
                return jsonify(success=False, message="This email is already registered.")

            field  = request.form.get('field')
            course = request.form.get('course')
            image_data = request.form.get('image')
            if not image_data or not image_data.startswith('data:image'):
                return jsonify(success=False, message="No image captured. Please click Capture Face before submitting.")

            # --- Decode base64 image -> bytes ---
            try:
                header, b64data = image_data.split(',', 1)
                image_bytes = base64.b64decode(b64data)
            except Exception:
                return jsonify(success=False, message="Invalid image data. Try capturing again.")

            # --- Face encoding (no local file writes) ---
            image_stream = io.BytesIO(image_bytes)
            pil = Image.open(image_stream).convert("RGB")
            rgb = np.array(pil)
            encodings = face_recognition.face_encodings(rgb)
            if not encodings:
                return jsonify(success=False, message="Face not detected clearly. Please try again.")
            encoding = encodings[0].tobytes()

            # --- Upload straight to Cloudinary ---
            # Ensure the stream is at the beginning before upload
            image_stream.seek(0)
            safe_username = re.sub(r'[^A-Za-z0-9_-]', '', username)   # keep only letters, digits, _ and -
            public_id = f"attendance/faces/{safe_username}-{roll}"

            upload_result = cloudinary.uploader.upload(
                image_stream,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            image_url = upload_result.get("secure_url")
            if not image_url:
                return jsonify(success=False, message="Upload failed: no URL returned from Cloudinary.")

            # --- Save user ---
            new_user = User(
                username=username,
                roll=roll,
                email=email,
                field=field,
                course=course,
                image_path=image_url,      # store Cloudinary URL only
                face_encoding=encoding,
                is_email_verified=True,
                email_verification_token=None
            )
            db.session.add(new_user)
            db.session.commit()

            # clear verification state
            for k in ('email_verification_code', 'email_to_verify', 'email_verified'):
                session.pop(k, None)

            return jsonify(success=True, message=f"{username} registered successfully!", redirect=url_for('dashboard'))

        except Exception as e:
                traceback.print_exc()
                return jsonify(success=False, message=f"Error: {str(e)}")

        # except Exception as e:
        #     current_app.logger.exception(f"Registration error: {e}")
        #     return jsonify(success=False, message=f"Unexpected error occurred. Try again.", redirect=url_for('register'))
    @app.route('/check-duplicate', methods=['POST'])
    def check_duplicate():
        username = request.form.get('username', '').strip()
        roll = request.form.get('roll', '').strip()
        email = request.form.get('email', '').strip()
        course = request.form.get('course', '').strip()
        if username and User.query.filter_by(username=username).first():
            return jsonify({'exists': True, 'field': 'username', 'message': 'This name is already registered.'})
        if roll and course and User.query.filter_by(roll=roll, course=course).first():
            return jsonify({'exists': True, 'field': 'roll', 'message': 'This roll number is already registered in this course.'})
        if email and User.query.filter_by(email=email).first():
            return jsonify({'exists': True, 'field': 'email', 'message': 'This email is already registered.'})
        return jsonify({'exists': False})
    # Utilities for Jinja
    @app.route('/attendance-dashboard/<field>/<course>')
    def attendance_dashboard(field, course):
        date_str = request.args.get('date')
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                filter_date = dt_date.today()
        else:
            filter_date = dt_date.today()

        users = User.query.filter_by(field=field, course=course).order_by(User.roll.asc()).all()
        attendance_records = Attendance.query.filter(
            Attendance.student_id.in_([u.id for u in users]),
            db.func.date(Attendance.date) == filter_date
        ).all()
        attendance_dict = {}
        for record in attendance_records:
            attendance_dict[record.student_id] = record
        return render_template(
            'attendance_dashboard.html',
            users=users,
            attendance_records=attendance_records,
            attendance_dict=attendance_dict,
            field=field,
            course=course,
            selected_date=filter_date.strftime("%Y-%m-%d"),
            today=dt_date.today().strftime("%Y-%m-%d")
        )

    def format_local_time(dt, tz_name='Asia/Kolkata', fmt='%Y-%m-%d %H:%M'):
        if not dt:
            return ''
        utc = pytz.utc
        local_tz = pytz.timezone(tz_name)
        if dt.tzinfo is None:
            dt = utc.localize(dt)
        local_dt = dt.astimezone(local_tz)
        return local_dt.strftime(fmt)

    app.jinja_env.filters['format_local_time'] = format_local_time

    # -------- Optional in-app scheduler (avoid on Render) --------
    if os.environ.get("ENABLE_SCHEDULER") == "true":
        def mark_absent_students(field, course, on_date=None):
            from app.models.models import User, Attendance  # local import
            if not on_date:
                on_date = datetime.utcnow().date()

            # with db.session.begin():
                users = db.session.query(User).filter_by(field=field, course=course).all()
                present_ids = {
                    r.student_id for r in db.session.query(Attendance).filter(
                        Attendance.field == field,
                        Attendance.course == course,
                        db.func.date(Attendance.date) == on_date,
                        Attendance.status.in_(['✅Present', '⏰Present-Late'])
                    )
                }
                for user in users:
                    if user.id not in present_ids:
                        absent_record = Attendance(
                            student_id=user.id,
                            date=datetime.utcnow(),
                            status='❌Absent',
                            field=field,
                            course=course
                        )
                        db.session.add(absent_record)
                        try:
                            send_absent_email(user.email, user.username, on_date.strftime('%Y-%m-%d'))
                        except Exception as e:
                            current_app.logger.error(f"Failed to send email to {user.email}: {str(e)}")
                db.session.commit()

        def run_absent_job():
            from app.models.models import User
            with app.app_context():
                fields_courses = db.session.query(User.field, User.course).distinct().all()
                for field, course in fields_courses:
                    mark_absent_students(field, course)

        scheduler = BackgroundScheduler()
        scheduler.add_job(run_absent_job, 'cron', hour=11, minute=31, timezone='Asia/Kolkata')
        scheduler.start()

    return app
