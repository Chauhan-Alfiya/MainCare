from flask import (
    render_template,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection

def init_student_routes(app):
        
        
        # ===========================
        # STUDENT DASHBOARD
        # ===========================

        @app.route("/student_dashboard")
        def student_dashboard():

            # ===========================
            # LOGIN CHECK
            # ===========================

            if "user_id" not in session:
                return redirect(url_for("login"))

            # ===========================
            # ROLE CHECK
            # ===========================

            if session.get("role") != "STUDENT":
                return redirect(url_for("login"))

            user_id = session["user_id"]

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            try:

                # ===========================
                # STUDENT PROFILE
                # ===========================

                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.username,
                        u.email,
                        s.class,
                        s.stream
                    FROM users u
                    INNER JOIN student_details s
                        ON u.user_id = s.user_id
                    WHERE u.user_id = %s
                """, (user_id,))

                student = cursor.fetchone()

                # ===========================
                # TOTAL ASSESSMENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM assessments
                    WHERE user_id = %s
                """, (user_id,))

                total_assessments = cursor.fetchone()["total"]

                # ===========================
                # PENDING APPOINTMENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM appointments
                    WHERE user_id = %s
                    AND status = 'Pending'
                """, (user_id,))

                pending_appointments = cursor.fetchone()["total"]

                # ===========================
                # WELLNESS CHECK-INS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM wellness_tracker
                    WHERE user_id = %s
                """, (user_id,))

                wellness_checkins = cursor.fetchone()["total"]

            except mysql.connector.Error as err:

                print("Student Dashboard Database Error:", err)

                flash("Unable to load student dashboard.")

                return redirect(url_for("logout"))

            finally:

                cursor.close()
                db.close()

            # ===========================
            # STUDENT PROFILE NOT FOUND
            # ===========================

            if not student:

                flash("Student profile not found.")

                return redirect(url_for("logout"))

            # ===========================
            # RENDER DASHBOARD
            # ===========================

            return render_template(
                "student_dashboard.html",

                student=student,

                total_assessments=total_assessments,

                pending_appointments=pending_appointments,

                wellness_checkins=wellness_checkins
            )