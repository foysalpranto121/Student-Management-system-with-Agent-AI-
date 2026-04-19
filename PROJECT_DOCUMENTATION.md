# Student Management System - Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [Project Structure](#project-structure)
6. [Database Schema](#database-schema)
7. [Authentication & Roles](#authentication--roles)
8. [Application Routes](#application-routes)
9. [AI Assistant Features](#ai-assistant-features)
10. [Usage Guide](#usage-guide)

---

## Project Overview

The **Student Management System** is a comprehensive web-based academic record management application built with Flask. It provides teachers and administrators with tools to manage student records, track grades, monitor attendance, and generate reports. The system also includes an AI-powered assistant for intelligent insights and analysis.

---

## Features

### Core Features
- **User Authentication** - Secure login system with role-based access control
- **Student Management** - Add, edit, view, and delete student records
- **Grade Management** - Record and manage student grades by subject
- **Attendance Tracking** - Daily attendance marking with statistics
- **PDF Report Generation** - Export student reports and transcripts
- **Dashboard Analytics** - Visual overview of system statistics

### AI-Powered Features
- **Intelligent Insights** - AI analysis of student performance
- **Grade Analysis** - Automated grade trend analysis
- **Attendance Analytics** - Smart attendance pattern detection
- **Document Processing** - Multi-modal document analysis (PDF, images, DOCX)
- **RAG-based Q&A** - Retrieval-Augmented Generation for student queries

---

## Technology Stack

### Backend
| Component | Technology |
|-----------|------------|
| Framework | Flask 3.0.0 |
| Database | SQLite3 |
| Authentication | Werkzeug (PBKDF2 hashing) |
| PDF Generation | ReportLab 4.0.7 |

### AI/ML Stack
| Component | Technology |
|-----------|------------|
| LLM Framework | LangChain 0.2.0 |
| AI Models | OpenAI GPT |
| Embeddings | OpenAI Embeddings / Sentence Transformers |
| Vector Store | ChromaDB |
| Document Processing | PyMuPDF, Pillow, pytesseract, python-docx |

### Frontend
| Component | Technology |
|-----------|------------|
| Templates | Jinja2 (HTML) |
| Styling | Custom CSS |
| Icons | Font Awesome |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone/Navigate to Project
```bash
cd "Student Managemnet System"
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 6: Run the Application
```bash
python app.py
```

The application will start at: `http://127.0.0.1:5000`

### Default Login Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |

---

## Project Structure

```
Student Managemnet System/
│
├── app.py                 # Main Flask application
├── ai_agent.py           # AI assistant module (LangChain + RAG)
├── database.sql          # Database schema backup
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .env.example          # Environment template
│
├── static/               # Static assets (CSS, JS, images)
│
├── templates/            # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── add_student.html
│   ├── edit_student.html
│   ├── view_student.html
│   ├── grades.html
│   ├── attendance.html
│   ├── reports.html
│   └── ai_assistant.html
│
└── student_management.db # SQLite database (auto-created)
```

---

## Database Schema

### Tables

#### 1. Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| username | TEXT UNIQUE | Login username |
| password | TEXT | Hashed password (PBKDF2) |
| role | TEXT | 'admin' or 'teacher' |
| created_at | TIMESTAMP | Account creation time |

#### 2. Students Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| student_id | TEXT UNIQUE | Student roll number |
| name | TEXT | Full name |
| email | TEXT | Email address |
| department | TEXT | Department/major |
| semester | INTEGER | Current semester |
| contact | TEXT | Contact number |
| created_at | TIMESTAMP | Record creation time |

#### 3. Subjects Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| subject_name | TEXT | Subject name |
| subject_code | TEXT UNIQUE | Subject code |
| max_marks | INTEGER | Maximum marks (default 100) |

#### 4. Grades Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| student_id | INTEGER FK | Reference to students.id |
| subject_id | INTEGER FK | Reference to subjects.id |
| marks | REAL | Score obtained |
| exam_type | TEXT | Type of exam |
| created_at | TIMESTAMP | Record creation time |

#### 5. Attendance Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| student_id | INTEGER FK | Reference to students.id |
| date | DATE | Attendance date |
| status | TEXT | 'Present' or 'Absent' |
| marked_by | INTEGER FK | Reference to users.id |
| created_at | TIMESTAMP | Record creation time |

---

## Authentication & Roles

### Role-Based Access Control

| Feature | Admin | Teacher |
|---------|-------|---------|
| View Dashboard | ✓ | ✓ |
| View Students | ✓ | ✓ |
| Add Student | ✓ | ✓ |
| Edit Student | ✓ | ✓ |
| Delete Student | ✓ | ✗ |
| Manage Grades | ✓ | ✓ |
| Mark Attendance | ✓ | ✓ |
| Generate Reports | ✓ | ✓ |
| Use AI Assistant | ✓ | ✓ |
| User Management | ✓ | ✗ |

### Decorators Used
- `@login_required` - Requires authentication
- `@admin_required` - Requires admin role
- `@teacher_required` - Requires teacher or admin role

---

## Application Routes

### Authentication Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Redirect to login or dashboard |
| `/login` | GET/POST | User login page |
| `/logout` | GET | User logout |

### Main Application Routes
| Route | Method | Access | Description |
|-------|--------|--------|-------------|
| `/dashboard` | GET | Any user | Main dashboard with statistics |
| `/students` | GET | Any user | List all students |
| `/students/add` | GET/POST | Teacher+ | Add new student |
| `/students/edit/<id>` | GET/POST | Teacher+ | Edit student record |
| `/students/view/<id>` | GET | Any user | View student details |
| `/students/delete/<id>` | POST | Admin only | Delete student |
| `/grades` | GET/POST | Teacher+ | Manage grades |
| `/attendance` | GET/POST | Teacher+ | Mark/view attendance |
| `/reports` | GET | Any user | Generate reports |
| `/reports/pdf/<id>` | GET | Any user | Download student PDF report |

### AI Assistant Routes
| Route | Method | Access | Description |
|-------|--------|--------|-------------|
| `/ai-assistant` | GET | Any user | AI assistant interface |
| `/ai-assistant/chat` | POST | Any user | Send message to AI |
| `/ai-assistant/upload` | POST | Any user | Upload documents for analysis |
| `/ai-assistant/student/<id>` | GET | Any user | Get AI insights for student |

---

## AI Assistant Features

### Capabilities
1. **Student Performance Analysis**
   - Grade trends and patterns
   - Performance predictions
   - Improvement recommendations

2. **Document Processing**
   - PDF text extraction
   - Image OCR (text recognition)
   - Word document analysis

3. **Intelligent Q&A**
   - RAG-based retrieval from student records
   - Natural language queries about students
   - Context-aware responses

4. **Attendance Insights**
   - Pattern detection
   - Risk identification
   - Intervention recommendations

### AI Architecture
```
User Query → Document Loaders → Text Splitter → Embeddings → ChromaDB
                                                      ↓
                                               Retriever
                                                      ↓
User ← Response ← LLM (GPT) ← Conversational Chain ← Query
```

---

## Usage Guide

### Getting Started

1. **Login** with default credentials
2. **Dashboard** shows system overview:
   - Total students
   - Total subjects
   - Average marks
   - Today's attendance

### Managing Students
1. Navigate to **Students** page
2. Click **Add Student** to create new records
3. Use **View** to see detailed information
4. Use **Edit** to modify records
5. Use **Delete** (admin only) to remove records

### Managing Grades
1. Go to **Grades** page
2. Select student and subject
3. Enter marks and exam type
4. Save to record grades
5. View grade history per student

### Marking Attendance
1. Navigate to **Attendance** page
2. Select date
3. Mark each student as Present/Absent
4. View attendance statistics and history

### Using AI Assistant
1. Go to **AI Assistant** page
2. Type natural language queries like:
   - "Show me students with low attendance"
   - "Analyze Alice Johnson's performance"
   - "Which students need intervention?"
3. Upload documents for analysis
4. Get AI-generated insights and recommendations

### Generating Reports
1. Go to **Reports** page
2. Select a student
3. Click **Download PDF** for printable transcript

---

## Default Data

The system initializes with sample data:

### Default Subjects
- Mathematics (MATH101)
- Physics (PHY101)
- Chemistry (CHEM101)
- English (ENG101)
- Computer Science (CS101)
- Biology (BIO101)

### Sample Students
| ID | Name | Department | Semester |
|----|------|------------|----------|
| STD001 | Alice Johnson | Computer Science | 3 |
| STD002 | Bob Smith | Computer Science | 3 |
| STD003 | Charlie Brown | Physics | 2 |
| STD004 | Diana Prince | Chemistry | 4 |
| STD005 | Eve Wilson | Mathematics | 2 |

---

## Security Notes

1. **Change default passwords** immediately after first login
2. **Keep `.env` file secure** - never commit it to version control
3. **Use strong passwords** for production deployment
4. **Enable HTTPS** for production deployments

---

## Support & Troubleshooting

### Common Issues

**Database errors on startup:**
- Check write permissions in project directory
- Delete `student_management.db` to reset (will lose data)

**AI features not working:**
- Verify `OPENAI_API_KEY` in `.env` file
- Check API key validity and quotas

**PDF generation fails:**
- Ensure `reportlab` is installed: `pip install reportlab`

---

*Documentation generated for Student Management System v1.0*
