from flask import request, jsonify, session, Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = db.session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        session['user_id'] = user.id
        return jsonify({"success": True, "message": "Login successful."})
    return jsonify({"success": False, "message": "Invalid username or password."}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if db.session.query(User).filter((User.username == username) | (User.email == email)).first():
        return jsonify({"success": False, "message": "Username or email already exists."}), 400

    new_user = User(username=username, email=email, roll=0, field='-', course='-')
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True, "message": "Registration successful! You can now log in."})


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.clear()
    return render_template('home.html')
