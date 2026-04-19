"""
Student Management System - Flask Application (SQLite Version)
Complete web-based academic record system that works out of the box
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import sqlite3
import io
import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'student-management-secret-key-2024'

DATABASE = 'student_management.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'teacher',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            semester INTEGER,
            contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            subject_code TEXT UNIQUE,
            max_marks INTEGER DEFAULT 100
        )
    ''')
    
    # Create grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks REAL NOT NULL,
            exam_type TEXT DEFAULT 'Final',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            UNIQUE(student_id, subject_id, exam_type)
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            marked_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (marked_by) REFERENCES users(id),
            UNIQUE(student_id, date)
        )
    ''')
    
    # Insert default data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_hash = generate_password_hash('admin123')
        teacher_hash = generate_password_hash('teacher123')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('admin', admin_hash, 'admin'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      ('teacher', teacher_hash, 'teacher'))
    
    # Insert default subjects if empty
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        subjects = [
            ('Mathematics', 'MATH101', 100),
            ('Physics', 'PHY101', 100),
            ('Chemistry', 'CHEM101', 100),
            ('English', 'ENG101', 100),
            ('Computer Science', 'CS101', 100),
            ('Biology', 'BIO101', 100)
        ]
        cursor.executemany("INSERT INTO subjects (subject_name, subject_code, max_marks) VALUES (?, ?, ?)", subjects)
    
    # Insert sample students if empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students = [
            ('STD001', 'Alice Johnson', 'alice@student.edu', 'Computer Science', 3, '1234567890'),
            ('STD002', 'Bob Smith', 'bob@student.edu', 'Computer Science', 3, '1234567891'),
            ('STD003', 'Charlie Brown', 'charlie@student.edu', 'Physics', 2, '1234567892'),
            ('STD004', 'Diana Prince', 'diana@student.edu', 'Chemistry', 4, '1234567893'),
            ('STD005', 'Eve Wilson', 'eve@student.edu', 'Mathematics', 2, '1234567894')
        ]
        cursor.executemany("INSERT INTO students (student_id, name, email, department, semester, contact) VALUES (?, ?, ?, ?, ?, ?)", students)
    
    # Insert sample grades if empty
    cursor.execute("SELECT COUNT(*) FROM grades")
    if cursor.fetchone()[0] == 0:
        grades = [
            (1, 1, 85.5, 'Final'), (1, 4, 78.0, 'Final'), (1, 5, 92.0, 'Final'),
            (2, 1, 76.5, 'Final'), (2, 4, 88.0, 'Final'),
            (3, 2, 82.0, 'Final'), (3, 3, 79.5, 'Final'),
            (4, 3, 91.0, 'Final'), (4, 4, 85.0, 'Final'),
            (5, 1, 74.0, 'Final')
        ]
        cursor.executemany("INSERT INTO grades (student_id, subject_id, marks, exam_type) VALUES (?, ?, ?, ?)", grades)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'teacher']:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM students")
        total_students = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM subjects")
        total_subjects = cursor.fetchone()['total']
        
        cursor.execute("SELECT AVG(marks) as avg_marks FROM grades")
        result = cursor.fetchone()
        avg_marks = result['avg_marks'] or 0
        
        today = datetime.date.today().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE date = ? AND status = 'Present'", (today,))
        present_today = cursor.fetchone()['total']
        
        cursor.execute("SELECT * FROM students ORDER BY created_at DESC LIMIT 5")
        recent_students = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_students': total_students,
            'total_subjects': total_subjects,
            'avg_marks': round(avg_marks, 2),
            'present_today': present_today
        }
        
        return render_template('dashboard.html', stats=stats, recent_students=recent_students)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('dashboard.html', stats={'total_students': 0, 'total_subjects': 0, 'avg_marks': 0, 'present_today': 0}, recent_students=[])

@app.route('/students')
@login_required
def students():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()
    semester = request.args.get('semester', '').strip()
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE ? OR student_id LIKE ? OR email LIKE ?)"
            like_search = f'%{search}%'
            params.extend([like_search, like_search, like_search])
        
        if department:
            query += " AND department = ?"
            params.append(department)
        
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        students_list = cursor.fetchall()
        
        cursor.execute("SELECT DISTINCT department FROM students WHERE department IS NOT NULL")
        departments = cursor.fetchall()
        
        conn.close()
        
        return render_template('students.html', students=students_list, departments=departments,
                           search=search, department=department, semester=semester)
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'danger')
        return render_template('students.html', students=[], departments=[], search='', department='', semester='')

@app.route('/students/add', methods=['GET', 'POST'])
@admin_required
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        contact = request.form.get('contact', '').strip()
        
        if not student_id or not name:
            flash('Student ID and Name are required', 'danger')
            return render_template('add_student.html')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (student_id, name, email, department, semester, contact) VALUES (?, ?, ?, ?, ?, ?)",
                          (student_id, name, email, department, semester, contact))
            conn.commit()
            conn.close()
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'danger')
    
    return render_template('add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_student(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department = request.form.get('department', '').strip()
        semester = request.form.get('semester', '').strip()
        contact = request.form.get('contact', '').strip()
        
        try:
            cursor.execute("UPDATE students SET student_id = ?, name = ?, email = ?, department = ?, semester = ?, contact = ? WHERE id = ?",
                          (student_id, name, email, department, semester, contact, id))
            conn.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'danger')
    
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))
    
    return render_template('edit_student.html', student=student)

@app.route('/students/delete/<int:id>', methods=['POST'])
@admin_required
def delete_student(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'danger')
    
    return redirect(url_for('students'))

@app.route('/students/view/<int:id>')
@login_required
def view_student(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('students'))
        
        cursor.execute("SELECT g.*, s.subject_name, s.subject_code FROM grades g JOIN subjects s ON g.subject_id = s.id WHERE g.student_id = ?", (id,))
        grades = cursor.fetchall()
        
        total_marks = sum(grade['marks'] for grade in grades) if grades else 0
        avg_marks = total_marks / len(grades) if grades else 0
        
        if avg_marks >= 90:
            gpa = 4.0
        elif avg_marks >= 80:
            gpa = 3.0
        elif avg_marks >= 70:
            gpa = 2.0
        elif avg_marks >= 60:
            gpa = 1.0
        else:
            gpa = 0.0
        
        cursor.execute("SELECT COUNT(*) as total_classes, SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_count FROM attendance WHERE student_id = ?", (id,))
        attendance_stats = cursor.fetchone()
        
        attendance_percentage = 0
        if attendance_stats and attendance_stats['total_classes'] > 0:
            attendance_percentage = (attendance_stats['present_count'] / attendance_stats['total_classes']) * 100
        
        conn.close()
        
        return render_template('view_student.html', student=student, grades=grades, gpa=gpa,
                           avg_marks=avg_marks, attendance_percentage=attendance_percentage)
    except Exception as e:
        flash(f'Error loading student details: {str(e)}', 'danger')
        return redirect(url_for('students'))

@app.route('/grades')
@teacher_required
def grades():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, student_id, name FROM students ORDER BY name")
        students_list = cursor.fetchall()
        
        cursor.execute("SELECT * FROM subjects ORDER BY subject_name")
        subjects = cursor.fetchall()
        
        cursor.execute("SELECT g.*, s.name as student_name, s.student_id, sub.subject_name, sub.subject_code FROM grades g JOIN students s ON g.student_id = s.id JOIN subjects sub ON g.subject_id = sub.id ORDER BY g.created_at DESC")
        grades_list = cursor.fetchall()
        
        conn.close()
        
        return render_template('grades.html', students=students_list, subjects=subjects, grades=grades_list)
    except Exception as e:
        flash(f'Error loading grades: {str(e)}', 'danger')
        return render_template('grades.html', students=[], subjects=[], grades=[])

@app.route('/grades/add', methods=['POST'])
@teacher_required
def add_grade():
    student_id = request.form.get('student_id')
    subject_id = request.form.get('subject_id')
    marks = request.form.get('marks')
    exam_type = request.form.get('exam_type', 'Final')
    
    if not student_id or not subject_id or not marks:
        flash('All fields are required', 'danger')
        return redirect(url_for('grades'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM grades WHERE student_id = ? AND subject_id = ? AND exam_type = ?", (student_id, subject_id, exam_type))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("UPDATE grades SET marks = ? WHERE id = ?", (marks, existing['id']))
            flash('Grade updated successfully!', 'success')
        else:
            cursor.execute("INSERT INTO grades (student_id, subject_id, marks, exam_type) VALUES (?, ?, ?, ?)", (student_id, subject_id, marks, exam_type))
            flash('Grade added successfully!', 'success')
        
        conn.commit()
        conn.close()
    except Exception as e:
        flash(f'Error adding grade: {str(e)}', 'danger')
    
    return redirect(url_for('grades'))

@app.route('/grades/delete/<int:id>', methods=['POST'])
@teacher_required
def delete_grade(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grades WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash('Grade deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting grade: {str(e)}', 'danger')
    
    return redirect(url_for('grades'))

@app.route('/attendance')
@teacher_required
def attendance():
    date_str = request.args.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.date.today()
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT s.*, a.status, a.id as attendance_id FROM students s LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ? ORDER BY s.name", (selected_date.strftime('%Y-%m-%d'),))
        students_list = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present, SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent FROM attendance WHERE date = ?", (selected_date.strftime('%Y-%m-%d'),))
        stats = cursor.fetchone()
        
        conn.close()
        
        return render_template('attendance.html', students=students_list, selected_date=selected_date, stats=stats)
    except Exception as e:
        flash(f'Error loading attendance: {str(e)}', 'danger')
        return render_template('attendance.html', students=[], selected_date=selected_date, stats=None)

@app.route('/attendance/mark', methods=['POST'])
@teacher_required
def mark_attendance():
    date_str = request.form.get('date')
    student_ids = request.form.getlist('student_ids[]')
    statuses = request.form.getlist('statuses[]')
    
    if not date_str or not student_ids:
        flash('Invalid data provided', 'danger')
        return redirect(url_for('attendance'))
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'danger')
        return redirect(url_for('attendance'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        marked_by = session.get('user_id')
        
        for student_id, status in zip(student_ids, statuses):
            cursor.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?", (student_id, selected_date.strftime('%Y-%m-%d')))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("UPDATE attendance SET status = ?, marked_by = ? WHERE id = ?", (status, marked_by, existing['id']))
            else:
                cursor.execute("INSERT INTO attendance (student_id, date, status, marked_by) VALUES (?, ?, ?, ?)", (student_id, selected_date.strftime('%Y-%m-%d'), status, marked_by))
        
        conn.commit()
        conn.close()
        flash('Attendance marked successfully!', 'success')
    except Exception as e:
        flash(f'Error marking attendance: {str(e)}', 'danger')
    
    return redirect(url_for('attendance', date=date_str))

@app.route('/reports')
@login_required
def reports():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, name FROM students ORDER BY name")
        students_list = cursor.fetchall()
        conn.close()
        return render_template('reports.html', students=students_list)
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'danger')
        return render_template('reports.html', students=[])

@app.route('/reports/generate/<int:student_id>')
@login_required
def generate_report(student_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('reports'))
        
        cursor.execute("SELECT g.*, s.subject_name, s.subject_code, s.max_marks FROM grades g JOIN subjects s ON g.subject_id = s.id WHERE g.student_id = ?", (student_id,))
        grades = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total_classes, SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_count FROM attendance WHERE student_id = ?", (student_id,))
        attendance_stats = cursor.fetchone()
        
        attendance_percentage = 0
        if attendance_stats and attendance_stats['total_classes'] > 0:
            attendance_percentage = (attendance_stats['present_count'] / attendance_stats['total_classes']) * 100
        
        conn.close()
        
        total_marks = sum(grade['marks'] for grade in grades) if grades else 0
        avg_marks = total_marks / len(grades) if grades else 0
        
        if avg_marks >= 90:
            gpa = 4.0
            grade_letter = 'A'
        elif avg_marks >= 80:
            gpa = 3.0
            grade_letter = 'B'
        elif avg_marks >= 70:
            gpa = 2.0
            grade_letter = 'C'
        elif avg_marks >= 60:
            gpa = 1.0
            grade_letter = 'D'
        else:
            gpa = 0.0
            grade_letter = 'F'
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2c3e50'), spaceAfter=30, alignment=1)
        header_style = ParagraphStyle('CustomHeader', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#34495e'), spaceAfter=12)
        
        elements.append(Paragraph("STUDENT MANAGEMENT SYSTEM", title_style))
        elements.append(Paragraph("Academic Report Card", header_style))
        elements.append(Spacer(1, 20))
        
        elements.append(Paragraph("<b>STUDENT INFORMATION</b>", header_style))
        student_data = [['Student ID:', student['student_id']], ['Name:', student['name']], ['Department:', student['department'] or 'N/A'], ['Semester:', str(student['semester']) if student['semester'] else 'N/A']]
        student_table = Table(student_data, colWidths=[2*inch, 4*inch])
        student_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')), ('TEXTCOLOR', (0, 0), (-1, -1), colors.black), ('ALIGN', (0, 0), (0, -1), 'LEFT'), ('ALIGN', (1, 0), (1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 10), ('GRID', (0, 0), (-1, -1), 1, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        elements.append(student_table)
        elements.append(Spacer(1, 20))
        
        if grades:
            elements.append(Paragraph("<b>ACADEMIC PERFORMANCE</b>", header_style))
            grades_data = [['Subject Code', 'Subject Name', 'Marks', 'Max Marks', 'Percentage']]
            for grade in grades:
                percentage = (grade['marks'] / grade['max_marks']) * 100 if grade['max_marks'] else 0
                grades_data.append([grade['subject_code'], grade['subject_name'], f"{grade['marks']:.1f}", str(grade['max_marks']), f"{percentage:.1f}%"])
            
            grades_table = Table(grades_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
            grades_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, 0), 10), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')), ('GRID', (0, 0), (-1, -1), 1, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            elements.append(grades_table)
            elements.append(Spacer(1, 15))
            
            summary_data = [['Total Subjects:', str(len(grades))], ['Average Marks:', f"{avg_marks:.1f}%"], ['Grade:', grade_letter], ['GPA:', f"{gpa:.2f}"], ['Attendance:', f"{attendance_percentage:.1f}%"]]
            summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
            summary_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#27ae60')), ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke), ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#d5f4e6')), ('TEXTCOLOR', (1, 0), (1, -1), colors.black), ('ALIGN', (0, 0), (0, -1), 'LEFT'), ('ALIGN', (1, 0), (1, -1), 'LEFT'), ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 11), ('GRID', (0, 0), (-1, -1), 1, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            elements.append(summary_table)
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"<i>Report generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)))
        
        doc.build(elements)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"Report_{student['student_id']}.pdf", mimetype='application/pdf')
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.errorhandler(404)
def not_found_error(error):
    flash('Page not found', 'danger')
    return redirect(url_for('dashboard'))

@app.errorhandler(500)
def internal_error(error):
    flash('Internal server error', 'danger')
    return redirect(url_for('dashboard'))

# ==================== AI ASSISTANT ROUTES ====================

@app.route('/ai-assistant')
@login_required
def ai_assistant():
    """AI Assistant page"""
    return render_template('ai_assistant.html')

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """AI Chat API endpoint"""
    try:
        from ai_agent import get_ai_agent
        
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        agent = get_ai_agent()
        response = agent.query(question)
        
        return jsonify({
            'success': True,
            'answer': response.get('answer', 'No response'),
            'sources': response.get('sources', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/student-insights/<student_id>')
@login_required
def ai_student_insights(student_id):
    """Get AI insights for a specific student"""
    try:
        from ai_agent import get_ai_agent
        
        agent = get_ai_agent()
        insights = agent.get_student_insights(student_id)
        
        return jsonify({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/report-summary')
@login_required
def ai_report_summary():
    """Get AI-generated school report summary"""
    try:
        from ai_agent import get_ai_agent
        
        agent = get_ai_agent()
        summary = agent.generate_report_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/refresh-data', methods=['POST'])
@login_required
def ai_refresh_data():
    """Refresh AI vector store with latest data"""
    try:
        from ai_agent import get_ai_agent
        
        agent = get_ai_agent()
        agent.refresh_vector_store()
        
        return jsonify({
            'success': True,
            'message': 'AI knowledge base updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
    print("""
===============================================
  Student Management System - Enhanced AI Version
===============================================
  Server URL: http://127.0.0.1:5000
  Database: SQLite (student_management.db)
  AI Features: Enhanced LangChain + OpenAI + ChromaDB
                                              
  Login Credentials:
  • Admin: admin / admin123
  • Teacher: teacher / teacher123
                                              
  Features:
  • Student Management (CRUD)
  • Grades & GPA Calculation
  • Attendance Tracking
  • PDF Report Generation
  • Enhanced AI Assistant with:
    - Advanced RAG & Semantic Search
    - Performance Predictions
    - Multi-modal Document Processing
    - Conversation Context Management
    - Real-time Data Sync
===============================================
    """)
