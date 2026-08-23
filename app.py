from database import create_tables
from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_tables
from flask import Flask, render_template, request, flash, redirect, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = "your_secret_key"


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()

        result = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = result.fetchone()

        connection.close()

        if user is None:
            return "User does not exist"

        stored_password = user["password"]

        if check_password_hash(stored_password, password):

            session["username"] = username
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/dashboard")

        else:
            return "Wrong password"

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("username", None)
    session.pop("role", None)

    return redirect("/login")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)


        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users
                (username, password, role)
                VALUES (?, ?, ?)
                """,
                (username, hashed_password, "student")
            )

            connection.commit()

            flash("Registration successful!")

            connection.close()

            return redirect("/login")

        except:

            connection.close()

            flash("Username already exists!")

    return render_template("register.html")


# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") == "admin":
        return redirect("/admin")

    username = session["username"]

    connection = get_db_connection()

    result = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = result.fetchone()

    user_id = user["id"]

    student = connection.execute(
    """
    SELECT
        students.*,
        classes.class_name
    FROM students
    LEFT JOIN classes
    ON students.class_id = classes.id
    WHERE students.user_id = ?
    """,
    (user_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        username=username,
        student=student
    )


# =========================
# CREATE STUDENT PROFILE
# =========================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        department = request.form["department"]
        semester = request.form["semester"]

        username = session["username"]

        connection = get_db_connection()

        result = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )

        user = result.fetchone()

        user_id = user["id"]

        existing_student = connection.execute(
            "SELECT * FROM students WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if existing_student:

            connection.close()

            flash("Profile already exists!")

            return redirect("/dashboard")

        connection.execute(
            """
            INSERT INTO students
            (user_id, name, age, department, semester)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                age,
                department,
                semester
            )
        )

        connection.commit()
        connection.close()

        flash("Profile created successfully!")

        return redirect("/dashboard")

    return render_template("student_profile.html")


# =========================
# EDIT PROFILE
# =========================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = get_db_connection()

    result = connection.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    )

    user = result.fetchone()

    user_id = user["id"]

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        department = request.form["department"]
        semester = request.form["semester"]

        connection.execute(
            """
            UPDATE students
            SET name = ?,
                age = ?,
                department = ?,
                semester = ?
            WHERE user_id = ?
            """,
            (
                name,
                age,
                department,
                semester,
                user_id
            )
        )

        connection.commit()
        connection.close()

        flash("Profile updated successfully!")

        return redirect("/dashboard")

    student = connection.execute(
        "SELECT * FROM students WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "edit_profile.html",
        student=student
    )


# ============================================================
# ADMIN
# ============================================================

@app.route("/admin")
def admin():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    total_students = connection.execute(
        "SELECT COUNT(*) AS count FROM students"
    ).fetchone()["count"]

    total_classes = connection.execute(
        "SELECT COUNT(*) AS count FROM classes"
    ).fetchone()["count"]

    total_subjects = connection.execute(
        "SELECT COUNT(*) AS count FROM subjects"
    ).fetchone()["count"]

    total_marks = connection.execute(
        "SELECT COUNT(*) AS count FROM marks"
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_classes=total_classes,
        total_subjects=total_subjects,
        total_marks=total_marks
    )

# =========================
# ADMIN - CLASSES
# =========================

@app.route("/admin/classes", methods=["GET", "POST"])
def admin_classes():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        class_name = request.form["class_name"]

        connection.execute(
            """
            INSERT INTO classes (class_name)
            VALUES (?)
            """,
            (class_name,)
        )

        connection.commit()

        flash("Class added successfully!")

    classes = connection.execute(
        "SELECT * FROM classes"
    ).fetchall()

    connection.close()

    return render_template(
        "admin_classes.html",
        classes=classes
    )


# =========================
# ADMIN - SUBJECTS
# =========================

@app.route("/admin/subjects", methods=["GET", "POST"])
def admin_subjects():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        subject_name = request.form["subject_name"]
        class_id = request.form["class_id"]

        connection.execute(
            """
            INSERT INTO subjects
            (subject_name, class_id)
            VALUES (?, ?)
            """,
            (
                subject_name,
                class_id
            )
        )

        connection.commit()

        flash("Subject added successfully!")

    classes = connection.execute(
        "SELECT * FROM classes"
    ).fetchall()

    subjects = connection.execute(
        """
        SELECT
            subjects.id,
            subjects.subject_name,
            classes.class_name
        FROM subjects
        JOIN classes
        ON subjects.class_id = classes.id
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_subjects.html",
        classes=classes,
        subjects=subjects
    )


# =========================
# ADMIN - STUDENTS
# =========================

@app.route("/admin/students", methods=["GET", "POST"])
def admin_students():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        student_id = request.form["student_id"]
        class_id = request.form["class_id"]

        connection.execute(
            """
            UPDATE students
            SET class_id = ?
            WHERE id = ?
            """,
            (class_id, student_id)
        )

        connection.commit()
        connection.close()

        flash("Student assigned to class successfully!")

        return redirect("/admin/students")

    students = connection.execute(
        """
        SELECT
            students.id,
            students.name,
            students.class_id,
            classes.class_name
        FROM students
        LEFT JOIN classes
        ON students.class_id = classes.id
        """
    ).fetchall()

    available_students = connection.execute(
        """
        SELECT id, name
        FROM students
        WHERE class_id IS NULL
        """
    ).fetchall()

    classes = connection.execute(
        "SELECT * FROM classes"
    ).fetchall()

    connection.close()

    return render_template(
        "admin_students.html",
        students=students,
        available_students=available_students,
        classes=classes
    )

@app.route("/admin/students/delete/<int:student_id>")
def delete_student(student_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    flash("Student deleted successfully!")

    return redirect("/admin/students")

@app.route("/admin/students/delete/<int:student_id>")
def delete_student(student_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    flash("Student deleted successfully!")

    return redirect("/admin/students")


# =========================
# ADMIN - ADD MARKS
# =========================

@app.route("/admin/marks", methods=["GET", "POST"])
def admin_marks():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        marks = float(request.form["marks"])

        # Check marks range
        if marks < 0 or marks > 100:

            connection.close()

            flash("Marks must be between 0 and 100!")

            return redirect("/admin/marks")

        # Check student
        student = connection.execute(
            """
            SELECT class_id
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        ).fetchone()

        if student is None:

            connection.close()

            flash("Student not found!")

            return redirect("/admin/marks")

        # Check subject belongs to student's class
        subject = connection.execute(
            """
            SELECT class_id
            FROM subjects
            WHERE id = ?
            """,
            (subject_id,)
        ).fetchone()

        if subject is None:

            connection.close()

            flash("Subject not found!")

            return redirect("/admin/marks")

        if student["class_id"] != subject["class_id"]:

            connection.close()

            flash("This subject does not belong to the student's class!")

            return redirect("/admin/marks")

        # Check duplicate marks
        existing = connection.execute(
            """
            SELECT id
            FROM marks
            WHERE student_id = ?
            AND subject_id = ?
            """,
            (
                student_id,
                subject_id
            )
        ).fetchone()

        if existing:

            connection.close()

            flash(
                "Marks already exist for this student and subject!"
            )

            return redirect("/admin/marks")

        # Insert marks
        connection.execute(
            """
            INSERT INTO marks
            (student_id, subject_id, marks)
            VALUES (?, ?, ?)
            """,
            (
                student_id,
                subject_id,
                marks
            )
        )

        connection.commit()

        flash("Marks added successfully!")

    students = connection.execute(
        """
        SELECT *
        FROM students
        """
    ).fetchall()

    subjects = connection.execute(
        """
        SELECT
            subjects.id,
            subjects.subject_name,
            subjects.class_id,
            classes.class_name
        FROM subjects
        JOIN classes
        ON subjects.class_id = classes.id
        """
    ).fetchall()

    marks = connection.execute(
    """
    SELECT
        marks.id,
        marks.marks,
        students.name,
        subjects.subject_name
    FROM marks
    JOIN students
        ON marks.student_id = students.id
    JOIN subjects
        ON marks.subject_id = subjects.id
    """
).fetchall()
    
    connection.close()

    return render_template(
        "admin_marks.html",
        students=students,
        subjects=subjects,
        marks=marks
    )


# =========================
# STUDENT SUBJECTS
# =========================

@app.route("/subjects")
def subjects():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") == "admin":
        return redirect("/admin")

    username = session["username"]

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    if user is None:

        connection.close()

        return redirect("/logout")

    user_id = user["id"]

    student = connection.execute(
        """
        SELECT id, class_id
        FROM students
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if student is None:

        connection.close()

        flash("Create your profile first!")

        return redirect("/dashboard")

    student_id = student["id"]

    subjects = connection.execute(
        """
        SELECT subjects.*
        FROM subjects
        JOIN students
        ON subjects.class_id = students.class_id
        WHERE students.id = ?
        """,
        (student_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


# =========================
# STUDENT RESULTS
# =========================

@app.route("/results")
def results():

    if "username" not in session:
        return redirect("/login")

    if session.get("role") == "admin":
        return redirect("/admin")

    username = session["username"]

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    if user is None:

        connection.close()

        return redirect("/logout")

    user_id = user["id"]

    student = connection.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    if student is None:

        connection.close()

        flash("Create your profile first!")

        return redirect("/dashboard")

    student_id = student["id"]

    results = connection.execute(
        """
        SELECT
            subjects.subject_name,
            marks.marks
        FROM marks
        JOIN subjects
        ON marks.subject_id = subjects.id
        WHERE marks.student_id = ?
        """,
        (student_id,)
    ).fetchall()

    connection.close()

    total_marks = 0

    for result in results:
        total_marks += float(result["marks"])

    number_of_subjects = len(results)

    if number_of_subjects > 0:

        maximum_marks = number_of_subjects * 100

        percentage = (
            total_marks / maximum_marks
        ) * 100

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"

    else:

        percentage = 0
        grade = "N/A"

    return render_template(
        "results.html",
        results=results,
        total_marks=total_marks,
        percentage=percentage,
        grade=grade
    )

@app.route("/admin/marks/edit/<int:mark_id>", methods=["GET", "POST"])
def edit_marks(mark_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        marks = float(request.form["marks"])

        if marks < 0 or marks > 100:
            connection.close()
            flash("Marks must be between 0 and 100!")
            return redirect("/admin/marks")

        connection.execute(
            """
            UPDATE marks
            SET marks = ?
            WHERE id = ?
            """,
            (marks, mark_id)
        )

        connection.commit()
        connection.close()

        flash("Marks updated successfully!")

        return redirect("/admin/marks")

    mark = connection.execute(
        """
        SELECT
            marks.id,
            marks.marks,
            students.name,
            subjects.subject_name
        FROM marks
        JOIN students
            ON marks.student_id = students.id
        JOIN subjects
            ON marks.subject_id = subjects.id
        WHERE marks.id = ?
        """,
        (mark_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "edit_marks.html",
        mark=mark
    )

@app.route("/admin/marks/delete/<int:mark_id>")
def delete_marks(mark_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM marks WHERE id = ?",
        (mark_id,)
    )

    connection.commit()
    connection.close()

    flash("Marks deleted successfully!")

    return redirect("/admin/marks")


@app.route("/admin/subjects/edit/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        subject_name = request.form["subject_name"]

        connection.execute(
            """
            UPDATE subjects
            SET subject_name = ?
            WHERE id = ?
            """,
            (subject_name, subject_id)
        )

        connection.commit()
        connection.close()

        flash("Subject updated successfully!")

        return redirect("/admin/subjects")

    subject = connection.execute(
        "SELECT * FROM subjects WHERE id = ?",
        (subject_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "edit_subject.html",
        subject=subject
    )

@app.route("/admin/subjects/delete/<int:subject_id>")
def delete_subject(subject_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    # Delete marks belonging to this subject first
    connection.execute(
        "DELETE FROM marks WHERE subject_id = ?",
        (subject_id,)
    )

    connection.execute(
        "DELETE FROM subjects WHERE id = ?",
        (subject_id,)
    )

    connection.commit()
    connection.close()

    flash("Subject deleted successfully!")

    return redirect("/admin/subjects")

@app.route("/admin/classes/edit/<int:class_id>", methods=["GET", "POST"])
def edit_class(class_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    if request.method == "POST":

        class_name = request.form["class_name"]

        connection.execute(
            """
            UPDATE classes
            SET class_name = ?
            WHERE id = ?
            """,
            (class_name, class_id)
        )

        connection.commit()
        connection.close()

        flash("Class updated successfully!")

        return redirect("/admin/classes")

    class_data = connection.execute(
        "SELECT * FROM classes WHERE id = ?",
        (class_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "edit_class.html",
        class_data=class_data
    )

@app.route("/admin/classes/delete/<int:class_id>")
def delete_class(class_id):

    if "username" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    connection = get_db_connection()

    # Remove class assignment from students
    connection.execute(
        """
        UPDATE students
        SET class_id = NULL
        WHERE class_id = ?
        """,
        (class_id,)
    )

    # Remove subjects belonging to class
    connection.execute(
        """
        DELETE FROM subjects
        WHERE class_id = ?
        """,
        (class_id,)
    )

    # Delete class
    connection.execute(
        """
        DELETE FROM classes
        WHERE id = ?
        """,
        (class_id,)
    )

    connection.commit()
    connection.close()

    flash("Class deleted successfully!")

    return redirect("/admin/classes")
# =========================
# RUN APPLICATION
# =========================

create_tables()

app.run(debug=True)