-- Student Management System Database Schema
-- MySQL Database

-- Create database
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- Users table (for authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher') DEFAULT 'teacher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50),
    semester INT,
    contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) UNIQUE,
    max_marks INT DEFAULT 100
);

-- Grades table
CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    marks DECIMAL(5,2) NOT NULL,
    exam_type VARCHAR(50) DEFAULT 'Final',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_grade (student_id, subject_id, exam_type)
);

-- Attendance table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    marked_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id),
    UNIQUE KEY unique_attendance (student_id, date)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, role) VALUES 
('admin', 'pbkdf2:sha256:600000$jC5OXv8L$b8d8ed7682d7e5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5', 'admin');

-- Insert default teacher user (password: teacher123)
INSERT INTO users (username, password, role) VALUES 
('teacher', 'pbkdf2:sha256:600000$jC5OXv8L$b8d8ed7682d7e5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5', 'teacher');

-- Insert sample subjects
INSERT INTO subjects (subject_name, subject_code, max_marks) VALUES
('Mathematics', 'MATH101', 100),
('Physics', 'PHY101', 100),
('Chemistry', 'CHEM101', 100),
('English', 'ENG101', 100),
('Computer Science', 'CS101', 100),
('Biology', 'BIO101', 100);

-- Insert sample students
INSERT INTO students (student_id, name, email, department, semester, contact) VALUES
('STD001', 'Alice Johnson', 'alice@student.edu', 'Computer Science', 3, '1234567890'),
('STD002', 'Bob Smith', 'bob@student.edu', 'Computer Science', 3, '1234567891'),
('STD003', 'Charlie Brown', 'charlie@student.edu', 'Physics', 2, '1234567892'),
('STD004', 'Diana Prince', 'diana@student.edu', 'Chemistry', 4, '1234567893'),
('STD005', 'Eve Wilson', 'eve@student.edu', 'Mathematics', 2, '1234567894');

-- Insert sample grades
INSERT INTO grades (student_id, subject_id, marks, exam_type) VALUES
(1, 1, 85.50, 'Final'),
(1, 4, 78.00, 'Final'),
(1, 5, 92.00, 'Final'),
(2, 1, 76.50, 'Final'),
(2, 4, 88.00, 'Final'),
(3, 2, 82.00, 'Final'),
(3, 3, 79.50, 'Final'),
(4, 3, 91.00, 'Final'),
(4, 4, 85.00, 'Final'),
(5, 1, 74.00, 'Final');

-- Insert sample attendance
INSERT INTO attendance (student_id, date, status, marked_by) VALUES
(1, CURDATE(), 'Present', 1),
(2, CURDATE(), 'Present', 1),
(3, CURDATE(), 'Absent', 1),
(4, CURDATE(), 'Present', 1),
(5, CURDATE(), 'Present', 1);

-- Create indexes for better performance
CREATE INDEX idx_student_name ON students(name);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_grades_student ON grades(student_id);
