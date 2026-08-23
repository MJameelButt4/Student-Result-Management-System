# 🎓 Student Result Management System

A web-based **Student Result Management System** built with **Python, Flask, SQLite, HTML, CSS, JavaScript, and Bootstrap**.

The system provides separate functionality for **Administrators** and **Students**. Administrators can manage classes, subjects, students, and marks, while students can view their profile, subjects, and academic results.

---

## 🚀 Features

### 👨‍💼 Admin

- Admin login
- Admin dashboard
- View system statistics
- Create and manage classes
- Edit classes
- Delete classes
- Create and manage subjects
- Edit subjects
- Delete subjects
- View students
- Assign students to classes
- Delete students
- Add student marks
- Edit marks
- Delete marks

### 👨‍🎓 Student

- Student registration
- Student login
- Student dashboard
- Create student profile
- Edit student profile
- View assigned subjects
- View academic results
- View marks

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Web page structure |
| CSS3 | Styling |
| JavaScript | Client-side functionality |
| Bootstrap | Responsive UI |
| Font Awesome | Icons |
| Jinja2 | HTML templating |

---

## 📁 Project Structure

```text
Student Result System/
│
├── app.py
├── database.py
├── students.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── student_profile.html
│   ├── edit_profile.html
│   ├── subjects.html
│   ├── results.html
│   │
│   └── admin/
│       ├── dashboard.html
│       ├── classes.html
│       ├── edit_class.html
│       ├── subjects.html
│       ├── edit_subject.html
│       ├── students.html
│       ├── marks.html
│       └── edit_marks.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
