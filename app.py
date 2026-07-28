from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mindcare123"

# ===========================
# DATABASE CONNECTION
# ===========================

def get_db_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mindcare"
    )


# ===========================
# HOME PAGE
# ===========================

@app.route("/")
def home():
    return render_template("home.html")


# ===========================
# ABOUT PAGE
# ===========================

@app.route("/about")
def about():
    return render_template("about.html")


# ===========================
# ASSESSMENT PAGE
# ===========================

@app.route("/assessment")
def assessment():
    return render_template("assessment.html")


# ===========================
# AI CHAT PAGE
# ===========================

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


# ===========================
# RESOURCES PAGE
# ===========================

@app.route("/resources")
def resources():
    return render_template("resources.html")


# ===========================
# APPOINTMENT PAGE
# ===========================

@app.route("/appointment")
def appointment():
    return render_template("appointment.html")


# ===========================
# REGISTER
# ===========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        student_class = request.form["class"]
        stream = request.form["stream"]

        password = generate_password_hash(
            request.form["password"]
        )

        db = get_db_connection()
        cursor = db.cursor()

        # Check Email

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        if user:

            flash("Email already exists.")
            cursor.close()
            db.close()

            return redirect(url_for("register"))

        # Insert User

        cursor.execute("""

        INSERT INTO users
        (
            username,
            email,
            password,
            role_id
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )

        """,

        (
            username,
            email,
            password,
            2
        ))

        db.commit()

        user_id = cursor.lastrowid

        # Student Details

        cursor.execute("""

        INSERT INTO student_details
        (
            user_id,
            class,
            stream
        )

        VALUES
        (
            %s,
            %s,
            %s
        )

        """,

        (
            user_id,
            student_class,
            stream
        ))

        db.commit()

        cursor.close()
        db.close()

        flash("Registration Successful.")

        return redirect(url_for("login"))

    return render_template("register.html")

    # ===========================
# LOGIN
# ===========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""

        SELECT
            users.*,
            roles.role

        FROM users

        JOIN roles
        ON users.role_id = roles.role_id

        WHERE username=%s

        """, (username,))

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:

            if check_password_hash(user["password"], password):

                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["role"] = user["role"]

                if user["role"] == "ADMIN":
                    return redirect(url_for("admin_dashboard"))

                elif user["role"] == "COUNSELLOR":
                    return redirect(url_for("counsellor_dashboard"))

                else:
                    return redirect(url_for("student_dashboard"))

        flash("Invalid Username or Password")

    return render_template("login.html")


# ===========================
# STUDENT DASHBOARD
# ===========================

@app.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "STUDENT":
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""

    SELECT
        users.username,
        users.email,
        student_details.class,
        student_details.stream

    FROM users

    JOIN student_details
    ON users.user_id = student_details.user_id

    WHERE users.user_id=%s

    """, (session["user_id"],))

    student = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "student_dashboard.html",
        student=student
    )


# ===========================
# ADMIN DASHBOARD
# ===========================

@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "ADMIN":
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Dashboard Counts

    cursor.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role_id=2"
    )
    total_students = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role_id=3"
    )
    total_counsellors = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM assessments"
    )
    total_assessments = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM appointments"
    )
    total_appointments = cursor.fetchone()["total"]

    # Recent Students

    cursor.execute("""

    SELECT
        user_id,
        username,
        email,
        created_at,
        is_active

    FROM users

    WHERE role_id=2

    ORDER BY user_id DESC

    LIMIT 5

    """)

    students = cursor.fetchall()

    # ===========================
    # RECENT COUNSELLORS
    # ===========================

    cursor.execute("""

    SELECT
        user_id,
        username,
        email,
        created_at,
        is_active

    FROM users

    WHERE role_id=3

    ORDER BY user_id DESC

    LIMIT 5

    """)

    counsellors = cursor.fetchall()

    # ===========================
    # RECENT ASSESSMENTS
    # ===========================

    cursor.execute("""

    SELECT

        a.assessment_id,
        u.username,
        a.assessment_type,
        a.score,
        a.risk_level,
        a.created_at

    FROM assessments a

    JOIN users u
    ON a.student_id=u.user_id

    ORDER BY a.assessment_id DESC

    LIMIT 5

    """)

    assessments = cursor.fetchall()

    # ===========================
    # RECENT APPOINTMENTS
    # ===========================

    cursor.execute("""

    SELECT

        ap.appointment_id,

        s.username AS student_name,

        c.username AS counsellor_name,

        ap.appointment_date,

        ap.appointment_time,

        ap.status

    FROM appointments ap

    JOIN users s
    ON ap.student_id=s.user_id

    JOIN users c
    ON ap.counsellor_id=c.user_id

    ORDER BY ap.appointment_id DESC

    LIMIT 5

    """)

    appointments = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(

        "admin_dashboard.html",

        total_students=total_students,

        total_counsellors=total_counsellors,

        total_assessments=total_assessments,

        total_appointments=total_appointments,

        students=students,

        counsellors=counsellors,

        assessments=assessments,

        appointments=appointments

    )


# ===========================
# COUNSELLOR DASHBOARD
# ===========================

@app.route("/counsellor_dashboard")
def counsellor_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "COUNSELLOR":
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""

    SELECT
        username,
        email,
        created_at

    FROM users

    WHERE user_id=%s

    """, (session["user_id"],))

    counsellor = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "counsellor_dashboard.html",
        counsellor=counsellor
    )


# ===========================
# LOGOUT
# ===========================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect(url_for("home"))


# ===========================
# RUN APPLICATION
# ===========================

if __name__ == "__main__":
    app.run(debug=True)