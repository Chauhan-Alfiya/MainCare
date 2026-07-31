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

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))

    return render_template("assessment.html")


# ===========================
# AI CHAT PAGE
# ===========================

@app.route("/chatbot")
def chatbot():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))

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

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "STUDENT":
        return redirect(url_for("login"))

    return render_template("appointment.html")
    # ===========================
# REGISTER
# ===========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # ===========================
        # FORM DATA
        # ===========================

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        selected_role = request.form.get("role", "").strip()

        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # ===========================
        # REQUIRED FIELDS
        # ===========================

        if not username or not email or not selected_role:

            flash("Please fill all required fields.")

            return redirect(
                url_for("register")
            )


        # ===========================
        # PASSWORD MATCH
        # ===========================

        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect(
                url_for("register")
            )


        # ===========================
        # VALID ROLE
        # ===========================

        if selected_role not in [
            "STUDENT",
            "COUNSELLOR"
        ]:

            flash("Please select a valid role.")

            return redirect(
                url_for("register")
            )


        db = get_db_connection()
        cursor = db.cursor()


        try:

            # ===========================
            # CHECK EMAIL
            # ===========================

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            if cursor.fetchone():

                flash("Email already exists.")

                return redirect(
                    url_for("register")
                )


            # ===========================
            # CHECK USERNAME
            # ===========================

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            if cursor.fetchone():

                flash("Username already exists.")

                return redirect(
                    url_for("register")
                )


            # ===========================
            # GET ROLE ID
            # ===========================

            cursor.execute(
                """
                SELECT role_id
                FROM roles
                WHERE role = %s
                """,
                (selected_role,)
            )

            role_data = cursor.fetchone()


            if not role_data:

                flash(
                    "Selected role does not exist."
                )

                return redirect(
                    url_for("register")
                )


            role_id = role_data[0]


            # ===========================
            # HASH PASSWORD
            # ===========================

            password_hash = generate_password_hash(
                password
            )


            # ===========================
            # INSERT INTO USERS
            # ===========================

            cursor.execute(
                """
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
                    password_hash,
                    role_id
                )
            )

            user_id = cursor.lastrowid


            # ===========================
            # STUDENT DETAILS
            # ===========================

            if selected_role == "STUDENT":

                student_class = request.form.get(
                    "class",
                    ""
                ).strip()

                stream = request.form.get(
                    "stream",
                    ""
                ).strip()


                if not student_class or not stream:

                    db.rollback()

                    flash(
                        "Please select class and stream."
                    )

                    return redirect(
                        url_for("register")
                    )


                cursor.execute(
                    """
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
                    )
                )


            # ===========================
            # COUNSELLOR DETAILS
            # ===========================

            elif selected_role == "COUNSELLOR":

                qualification = request.form.get(
                    "qualification",
                    ""
                ).strip()

                specialization = request.form.get(
                    "specialization",
                    ""
                ).strip()

                experience = request.form.get(
                    "experience",
                    "0"
                ).strip()


                if not qualification or not specialization:

                    db.rollback()

                    flash(
                        "Please enter qualification and specialization."
                    )

                    return redirect(
                        url_for("register")
                    )


                if not experience:
                    experience = 0


                cursor.execute(
                    """
                    INSERT INTO counsellor_details
                    (
                        user_id,
                        qualification,
                        specialization,
                        experience
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
                        user_id,
                        qualification,
                        specialization,
                        experience
                    )
                )


            # ===========================
            # SAVE
            # ===========================

            db.commit()

            flash(
                "Registration Successful."
            )

            return redirect(
                url_for("login")
            )


        except mysql.connector.Error as err:

            db.rollback()

            print(
                "Registration Error:",
                err
            )

            flash(
                "Registration failed."
            )

            return redirect(
                url_for("register")
            )


        finally:

            cursor.close()
            db.close()


    return render_template(
        "register.html"
    )
    # ===========================
# LOGIN
# ===========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        try:

            # ===========================
            # GET USER + ROLE
            # ===========================

            cursor.execute(
                """
                SELECT

                    users.user_id,
                    users.username,
                    users.email,
                    users.password,
                    users.role_id,
                    users.is_active,
                    users.is_deleted,

                    roles.role

                FROM users

                INNER JOIN roles
                    ON users.role_id =
                       roles.role_id

                WHERE users.username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()


        except mysql.connector.Error as err:

            print(
                "Login Database Error:",
                err
            )

            flash(
                "Login failed. Please try again."
            )

            cursor.close()
            db.close()

            return render_template(
                "login.html"
            )


        finally:

            try:
                cursor.close()
                db.close()
            except:
                pass


        # ===========================
        # USER NOT FOUND
        # ===========================

        if not user:

            flash(
                "Invalid Username or Password."
            )

            return render_template(
                "login.html"
            )


        # ===========================
        # ACCOUNT STATUS
        # ===========================

        if not user["is_active"]:

            flash(
                "Your account is inactive."
            )

            return render_template(
                "login.html"
            )


        if user["is_deleted"]:

            flash(
                "Your account has been deleted."
            )

            return render_template(
                "login.html"
            )


        # ===========================
        # PASSWORD CHECK
        # ===========================

        try:

            password_valid = check_password_hash(
                user["password"],
                password
            )

        except (ValueError, TypeError):

            password_valid = False


        if not password_valid:

            flash(
                "Invalid Username or Password."
            )

            return render_template(
                "login.html"
            )


        # ===========================
        # SESSION
        # ===========================

        session.clear()

        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["email"] = user["email"]
        session["role"] = user["role"]


        # ===========================
        # ROLE REDIRECTION
        # ===========================

        if user["role"] == "ADMIN":

            return redirect(
                url_for("admin_dashboard")
            )


        elif user["role"] == "COUNSELLOR":

            return redirect(
                url_for("counsellor_dashboard")
            )


        elif user["role"] == "STUDENT":

            return redirect(
                url_for("student_dashboard")
            )


        else:

            session.clear()

            flash(
                "Invalid user role."
            )

            return redirect(
                url_for("login")
            )


    return render_template(
        "login.html"
    )
    # ===========================
# STUDENT DASHBOARD
# ===========================

@app.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if session.get("role") != "STUDENT":

        return redirect(
            url_for("login")
        )


    db = get_db_connection()
    cursor = db.cursor(dictionary=True)


    try:

        cursor.execute(
            """
            SELECT

                users.username,
                users.email,

                student_details.class,
                student_details.stream

            FROM users

            INNER JOIN student_details

                ON users.user_id =
                   student_details.user_id

            WHERE users.user_id = %s
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()


    finally:

        cursor.close()
        db.close()


    if not student:

        flash(
            "Student profile not found."
        )

        return redirect(
            url_for("logout")
        )


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

        return redirect(
            url_for("login")
        )


    if session.get("role") != "ADMIN":

        return redirect(
            url_for("login")
        )


    db = get_db_connection()
    cursor = db.cursor(dictionary=True)


    try:

        # ===========================
        # TOTAL STUDENTS
        # ===========================

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM users u

            INNER JOIN roles r
                ON u.role_id = r.role_id

            WHERE r.role = 'STUDENT'

              AND u.is_deleted = FALSE
            """
        )

        total_students = cursor.fetchone()["total"]


        # ===========================
        # TOTAL COUNSELLORS
        # ===========================

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM users u

            INNER JOIN roles r
                ON u.role_id = r.role_id

            WHERE r.role = 'COUNSELLOR'

              AND u.is_deleted = FALSE
            """
        )

        total_counsellors = cursor.fetchone()["total"]


        # ===========================
        # TOTAL ASSESSMENTS
        # ===========================

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM assessments
            """
        )

        total_assessments = cursor.fetchone()["total"]


        # ===========================
        # TOTAL APPOINTMENTS
        # ===========================

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM appointments
            """
        )

        total_appointments = cursor.fetchone()["total"]


        # ===========================
        # RECENT STUDENTS
        # ===========================

        cursor.execute(
            """
            SELECT

                u.user_id,
                u.username,
                u.email,
                u.created_at,
                u.is_active

            FROM users u

            INNER JOIN roles r
                ON u.role_id = r.role_id

            WHERE r.role = 'STUDENT'

              AND u.is_deleted = FALSE

            ORDER BY u.user_id DESC

            LIMIT 5
            """
        )

        students = cursor.fetchall()


        # ===========================
        # RECENT COUNSELLORS
        # ===========================

        cursor.execute(
            """
            SELECT

                u.user_id,
                u.username,
                u.email,
                u.created_at,
                u.is_active

            FROM users u

            INNER JOIN roles r
                ON u.role_id = r.role_id

            WHERE r.role = 'COUNSELLOR'

              AND u.is_deleted = FALSE

            ORDER BY u.user_id DESC

            LIMIT 5
            """
        )

        counsellors = cursor.fetchall()


        # ===========================
        # RECENT ASSESSMENTS
        # ===========================

        cursor.execute(
            """
            SELECT

                a.assessment_id,
                u.username,
                a.assessment_type,
                a.score,
                a.risk_level,
                a.created_at

            FROM assessments a

            INNER JOIN users u

                ON a.user_id =
                   u.user_id

            ORDER BY
                a.assessment_id DESC

            LIMIT 5
            """
        )

        assessments = cursor.fetchall()


        # ===========================
        # RECENT APPOINTMENTS
        # ===========================

        cursor.execute(
            """
            SELECT

                ap.appointment_id,

                s.username
                    AS student_name,

                c.username
                    AS counsellor_name,

                ap.appointment_date,

                ap.appointment_time,

                ap.status

            FROM appointments ap

            INNER JOIN users s

                ON ap.user_id =
                   s.user_id

            INNER JOIN users c

                ON ap.counsellor_id =
                   c.user_id

            ORDER BY
                ap.appointment_id DESC

            LIMIT 5
            """
        )

        appointments = cursor.fetchall()


    finally:

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

        return redirect(
            url_for("login")
        )


    if session.get("role") != "COUNSELLOR":

        return redirect(
            url_for("login")
        )


    db = get_db_connection()
    cursor = db.cursor(dictionary=True)


    try:

        cursor.execute(
            """
            SELECT

                users.username,
                users.email,
                users.created_at,

                counsellor_details.qualification,
                counsellor_details.specialization,
                counsellor_details.experience

            FROM users

            LEFT JOIN counsellor_details

                ON users.user_id =
                   counsellor_details.user_id

            WHERE users.user_id = %s
            """,
            (session["user_id"],)
        )

        counsellor = cursor.fetchone()


    finally:

        cursor.close()
        db.close()


    if not counsellor:

        flash(
            "Counsellor profile not found."
        )

        return redirect(
            url_for("logout")
        )


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

    flash(
        "Logged out successfully."
    )

    return redirect(
        url_for("home")
    )


# ===========================
# RUN APPLICATION
# ===========================

if __name__ == "__main__":

    app.run(
        debug=True
    )