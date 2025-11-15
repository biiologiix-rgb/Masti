from flask import Blueprint, request, jsonify
from datetime import datetime
import base64
import re
from io import BytesIO

import numpy as np
from PIL import Image
import cv2
import face_recognition

from app.extensions import db
from app.models.models import User, Attendance

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/scan-face', methods=['POST'])
def scan_face():
    data = request.get_json()

    field = data.get('field')
    course = data.get('course')

    image_data = re.sub(r'^data:image/.+;base64,', '', data.get('image', ''))
    try:
        img_bytes = base64.b64decode(image_data)
    except Exception:
        return jsonify({'status': 'bad-image'}), 400

    img = Image.open(BytesIO(img_bytes)).convert('RGB')
    img_np = np.array(img)
    # img_np = cv2.resize(img_np, (0, 0), fx=0.5, fy=0.5)
    img_np = cv2.resize(img_np, (min(img_np.shape[1], 300), min(img_np.shape[0], 300)))

    face_encodings = face_recognition.face_encodings(img_np)
    if not face_encodings:
        return jsonify({'status': 'no-face'})

    scanned_encoding = face_encodings[0]

    # Filter only users for the selected field/course
    users = db.session.query(User).filter_by(field=field, course=course).all()

    for user in users:
        if user.face_encoding is None:
            continue
        known_encoding = np.frombuffer(user.face_encoding, dtype=np.float64)
        match = face_recognition.compare_faces([known_encoding], scanned_encoding, tolerance=0.6)[0]
        if match:
            return jsonify({
                'status': 'match',
                'username': user.username,
                'roll': user.roll,
                'field': user.field,
                'course': user.course,
                'user_id': user.id
            })

    return jsonify({'status': 'no-match'})


@attendance_bp.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    import pytz
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    today = now.date()
    user_id = data['user_id']
    field = data.get('field')
    course = data.get('course')

    existing = db.session.query(Attendance).filter(
        Attendance.student_id == user_id,
        Attendance.field == field,
        Attendance.course == course,
        db.func.date(Attendance.date) == today
    ).first()

    if existing:
        return jsonify({'status': 'already_marked', 'message': 'Attendance already marked for today.'})

    present_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    late_time = now.replace(hour=11, minute=30, second=0, microsecond=0)

    if now <= present_time:
        status = '✅Present'
    elif now <= late_time:
        status = '⏰Present-Late'
    else:
        return jsonify({'status': 'closed', 'message': 'Attendance window is closed. You are marked absent.'})

    new_record = Attendance(
        student_id=user_id,
        date=datetime.utcnow(),
        status=status,
        field=field,
        course=course
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'status': 'marked'})