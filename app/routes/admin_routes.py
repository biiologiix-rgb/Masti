from flask import (
    Blueprint, render_template, send_file, request, redirect, url_for,
    session, flash, jsonify, current_app, make_response
)
from functools import wraps
from datetime import datetime
from datetime import date as dt_date
import os
from io import BytesIO
import cloudinary
import cloudinary.uploader
from app.extensions import db
from app.models.models import User, Admin, Attendance

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Admin-only decorator (session-based)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('admin.login'))
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return decorated_function


@admin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = db.session.query(Admin).filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            response = make_response(redirect(url_for('admin.dashboard')))
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            return response
        else:
            flash('Invalid username or password.', 'danger')

    response = make_response(render_template('admin/admin_login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@admin_bp.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('admin.login')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    flash('Logged out successfully.', 'success')
    return response


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    response = make_response(render_template('admin/admin_dashboard.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@admin_bp.route('/students', methods=['GET', 'POST'])
@admin_required
def manage_students():
    selected_field = request.form.get('field') if request.method == 'POST' else ''
    selected_course = request.form.get('course') if request.method == 'POST' else ''
    selected_date = request.form.get('date') if request.method == 'POST' else dt_date.today().strftime('%Y-%m-%d')

    fields = [f[0] for f in db.session.query(User.field).distinct().all()]
    if selected_field:
        courses = [c[0] for c in db.session.query(User.course).filter_by(field=selected_field).distinct().all()]
    else:
        courses = [c[0] for c in db.session.query(User.course).distinct().all()]

    query = db.session.query(User)
    if selected_field:
        query = query.filter_by(field=selected_field)
    if selected_course:
        query = query.filter_by(course=selected_course)
    if selected_date:
        query = query.filter(db.func.date(User.created_at) == selected_date)

    students = query.order_by(User.roll.asc()).all()

    return render_template(
        'admin/manage_students.html',
        students=students,
        fields=fields,
        courses=courses,
        selected_field=selected_field,
        selected_course=selected_course,
        selected_date=selected_date,
        today=dt_date.today().strftime("%Y-%m-%d")
    )


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        roll = request.form.get('roll')
        field = request.form.get('field')
        course = request.form.get('course')
        new_student = User(username=username, email=email, roll=roll, field=field, course=course)
        db.session.add(new_student)
        db.session.commit()
        flash("Student added!", "success")
        return redirect(url_for('admin.manage_students'))
    return render_template('admin/add_student.html')

@admin_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(user_id):
    student = db.session.get(User, user_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('admin.manage_students'))

    if request.method == 'POST':
        student.username = request.form.get('username')
        student.email = request.form.get('email')
        student.roll = request.form.get('roll')
        student.field = request.form.get('field')
        student.course = request.form.get('course')

        # ✅ Cloudinary Upload
        photo = request.files.get('photo')
        if photo and photo.filename:
            upload_result = cloudinary.uploader.upload(
                photo,
                folder="attendance/faces",
                public_id=f"{student.username}-{student.roll}",
                overwrite=True
            )
            student.image_path = upload_result.get("secure_url")  # save cloud URL

        db.session.commit()
        flash("Student updated!", "success")
        return redirect(url_for('admin.manage_students'))

    return render_template('admin/edit_student.html', student=student)


@admin_bp.route('/students/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_student(user_id):
    student = db.session.get(User, user_id)
    if not student:
        return redirect(url_for('admin.manage_students'))
    db.session.query(Attendance).filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("Student and their attendance deleted!", "danger")
    return redirect(url_for('admin.manage_students'))


@admin_bp.route('/attendance-viewer', methods=['GET', 'POST'])
@admin_required
def attendance_viewer():
    fields = [f[0] for f in db.session.query(User.field).distinct().all()]
    selected_field = request.form.get('field') if request.method == 'POST' else ''
    selected_course = request.form.get('course') if request.method == 'POST' else ''
    selected_student = request.form.get('student') if request.method == 'POST' else ''
    selected_date = request.form.get('date') if request.method == 'POST' else ''

    if selected_field:
        courses = [c[0] for c in db.session.query(User.course).filter_by(field=selected_field).distinct().all()]
    else:
        courses = [c[0] for c in db.session.query(User.course).distinct().all()]

    students_query = db.session.query(User)
    if selected_field:
        students_query = students_query.filter_by(field=selected_field)
    if selected_course:
        students_query = students_query.filter_by(course=selected_course)
    students = students_query.all()

    attendance_records = db.session.query(Attendance)
    if selected_field or selected_course:
        attendance_records = attendance_records.join(User)
    if selected_field:
        attendance_records = attendance_records.filter(User.field == selected_field)
    if selected_course:
        attendance_records = attendance_records.filter(User.course == selected_course)
    if selected_student:
        attendance_records = attendance_records.filter(Attendance.student_id == selected_student)
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            attendance_records = attendance_records.filter(db.func.date(Attendance.date) == date_obj.date())
        except Exception:
            pass

    attendance_records = attendance_records.all()

    return render_template(
        'admin/attendance_viewer.html',
        attendance_records=attendance_records,
        students=students,
        fields=fields,
        courses=courses,
        selected_student=selected_student,
        selected_field=selected_field,
        selected_course=selected_course,
        selected_date=selected_date
    )


@admin_bp.route('/export_attendance/pdf')
@admin_required
def export_attendance_pdf():
    # Import lazily so lack of dependency won't crash the app
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas as pdf_canvas
    except Exception:
        return "PDF export not available (missing 'reportlab').", 501

    field = request.args.get('field')
    course = request.args.get('course')
    date_str = request.args.get('date')

    records_q = db.session.query(Attendance).join(User)
    if field:
        records_q = records_q.filter(User.field == field)
    if course:
        records_q = records_q.filter(User.course == course)
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            records_q = records_q.filter(db.func.date(Attendance.date) == date_obj)
        except Exception:
            pass

    records = records_q.order_by(Attendance.date.asc()).all()
    if not records:
        return "No attendance data found for the selected criteria.", 404

    buffer = BytesIO()
    pdf = pdf_canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("Attendance Report")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, height - 50, "Attendance Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Field: {field or 'All'}")
    pdf.drawString(250, height - 80, f"Course: {course or 'All'}")
    pdf.drawString(450, height - 80, f"Date: {date_str or 'All Dates'}")

    y = height - 120
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Student")
    pdf.drawString(220, y, "Roll")
    pdf.drawString(320, y, "Field")
    pdf.drawString(400, y, "Course")
    pdf.drawString(480, y, "Date")
    pdf.drawString(550, y, "Status")

    pdf.setFont("Helvetica", 10)
    y -= 18

    for rec in records:
        if rec.student:
            pdf.drawString(50, y, str(rec.student.username))
            pdf.drawString(220, y, str(rec.student.roll))
            pdf.drawString(320, y, str(rec.student.field))
            pdf.drawString(400, y, str(rec.student.course))
            pdf.drawString(480, y, rec.date.strftime("%Y-%m-%d %H:%M"))
            pdf.drawString(550, y, str(rec.status))
            y -= 15
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 10)

    pdf.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"attendance_report_{date_str or 'all'}.pdf",
        mimetype='application/pdf'
    )


@admin_bp.route('/registered-students', methods=['GET', 'POST'])
@admin_required
def registered_students():
    fields = [f[0] for f in db.session.query(User.field).distinct().all()]
    selected_field = request.form.get('field') if request.method == 'POST' else ''
    selected_course = request.form.get('course') if request.method == 'POST' else ''
    selected_date = request.form.get('date') if request.method == 'POST' else dt_date.today().strftime('%Y-%m-%d')

    if selected_field:
        courses = [c[0] for c in db.session.query(User.course).filter_by(field=selected_field).distinct().all()]
    else:
        courses = [c[0] for c in db.session.query(User.course).distinct().all()]

    students_query = db.session.query(User)
    if selected_field:
        students_query = students_query.filter_by(field=selected_field)
    if selected_course:
        students_query = students_query.filter_by(course=selected_course)
    if selected_date:
        students_query = students_query.filter(db.func.date(User.created_at) == selected_date)
    students = students_query.all()

    return render_template(
        'admin/registered_students.html',
        students=students,
        fields=fields,
        courses=courses,
        selected_field=selected_field,
        selected_course=selected_course,
        selected_date=selected_date,
        today=dt_date.today().strftime("%Y-%m-%d")
    )


@admin_bp.route('/export-attendance/<format>')
@admin_required
def export_attendance(format):
    import io, csv
    from flask import Response

    date_str = request.args.get('date')
    field = request.args.get('field')
    course = request.args.get('course')

    query = db.session.query(Attendance).join(User)
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Attendance.date) == date_obj)
        except ValueError:
            pass
    if field:
        query = query.filter(User.field == field)
    if course:
        query = query.filter(User.course == course)

    attendance_records = query.all()

    if format == 'csv':
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Student', 'Roll', 'Field', 'Course', 'Date', 'Status'])
        for r in attendance_records:
            if r.student:
                cw.writerow([
                    r.student.username,
                    r.student.roll,
                    r.student.field,
                    r.student.course,
                    r.date.strftime('%Y-%m-%d %H:%M'),
                    r.status
                ])
        output = si.getvalue()
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=attendance_{date_str or 'all'}.csv"}
        )
    else:
        return "Invalid format", 400


@admin_bp.route('/manage-attendance', methods=['GET', 'POST'])
@admin_required
def manage_attendance():
    fields = db.session.query(User.field).distinct().all()
    selected_field = request.form.get('field') if request.method == 'POST' else ''
    selected_course = request.form.get('course') if request.method == 'POST' else ''
    selected_date = request.form.get('date') if request.method == 'POST' else dt_date.today().strftime('%Y-%m-%d')

    if selected_field:
        courses = db.session.query(User.course).filter_by(field=selected_field).distinct().all()
    else:
        courses = db.session.query(User.course).distinct().all()

    students_query = db.session.query(User)
    if selected_field:
        students_query = students_query.filter_by(field=selected_field)
    if selected_course:
        students_query = students_query.filter_by(course=selected_course)
    students = students_query.all()

    attendance_records = db.session.query(Attendance).filter(
        Attendance.student_id.in_([s.id for s in students]),
        db.func.date(Attendance.date) == selected_date
    ).all()
    attendance_dict = {r.student_id: r for r in attendance_records}

    present_count = sum(1 for r in attendance_records if r.status == '✅Present')
    late_count = sum(1 for r in attendance_records if r.status == '⏰Present-Late')
    absent_count = len(students) - present_count - late_count

    return render_template(
        'admin/manage_attendance.html',
        students=students,
        attendance_dict=attendance_dict,
        fields=fields,
        courses=courses,
        selected_field=selected_field,
        selected_course=selected_course,
        selected_date=selected_date,
        today=dt_date.today().strftime("%Y-%m-%d"),
        present_count=present_count,
        late_count=late_count,
        absent_count=absent_count
    )


@admin_bp.route('/attendance/add', methods=['POST'])
@admin_required
def add_attendance():
    student_id = request.form.get('student_id')
    status = request.form.get('status')
    field = request.form.get('field')
    course = request.form.get('course')
    date_str = request.form.get('date')
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    new_record = Attendance(
        student_id=student_id,
        date=date_obj,
        status=status,
        field=field,
        course=course
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/attendance/save', methods=['POST'])
@admin_required
def save_attendance():
    record_id = request.form.get('record_id')
    status = request.form.get('status')
    record = db.session.get(Attendance, record_id)
    if record:
        record.status = status
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@admin_bp.route('/attendance/delete', methods=['POST'])
@admin_required
def delete_attendance():
    record_id = request.form.get('record_id')
    record = db.session.get(Attendance, record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@admin_bp.route('/custom-email', methods=['GET'])
@admin_required
def custom_email_page():
    return render_template('admin/custom_email.html')


@admin_bp.route('/send-custom-email', methods=['POST'])
@admin_required
def send_custom_email():
    from config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT
    import smtplib
    from email.mime.text import MIMEText

    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [email], msg.as_string())
        flash('Email sent successfully!', 'success')
    except Exception as e:
        flash(f'Failed to send email: {e}', 'danger')

    return redirect(url_for('admin.manage_students'))


@admin_bp.route('/send-absent-emails', methods=['POST'])
@admin_required
def send_absent_emails():
    from app import send_absent_email

    date_str = request.form.get('date')
    field = request.form.get('field')
    course = request.form.get('course')
    if not date_str:
        date_str = dt_date.today().strftime('%Y-%m-%d')

    absentees = db.session.query(Attendance).join(User).filter(
        Attendance.status == '❌Absent',
        db.func.date(Attendance.date) == date_str
    )
    if field:
        absentees = absentees.filter(User.field == field)
    if course:
        absentees = absentees.filter(User.course == course)

    absentees = absentees.all()
    count = 0
    for record in absentees:
        try:
            send_absent_email(record.student.email, record.student.username, date_str)
            count += 1
        except Exception as e:
            current_app.logger.error(f"Failed to send absent email to {record.student.email}: {e}")

    return jsonify({'success': True, 'count': count})
