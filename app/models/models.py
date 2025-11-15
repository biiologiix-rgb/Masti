from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'attendance_student'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    roll = db.Column(db.Integer, nullable=False)

    # auth
    password_hash = db.Column(db.String(200), nullable=True)

    # face & meta
    image_path = db.Column(db.String(300))
    field = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    face_encoding = db.Column(db.PickleType)  # numpy array

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(128), nullable=True)

    # helpers
    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('attendance_student.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), default='Present')
    field = db.Column(db.String(100))
    course = db.Column(db.String(100))

    student = db.relationship('User', backref='attendances')


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
