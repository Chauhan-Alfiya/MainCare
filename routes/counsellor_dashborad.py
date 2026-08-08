from flask import (
    render_template,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection


def init_counsellor_dashboard_routes(app):
        
        
        # ===========================
        # COUNSELLOR DASHBOARD
        # ===========================

        @app.route("/counsellor_dashboard")
        def counsellor_dashboard():

            # ===========================
            # LOGIN CHECK
            # ===========================

            if "user_id" not in session:
                return redirect(url_for("login"))

            # ===========================
            # ROLE CHECK
            # ===========================

            if session.get("role") != "COUNSELLOR":
                return redirect(url_for("login"))

            counsellor_id = session["user_id"]

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            try:

                # ===========================
                # COUNSELLOR PROFILE
                # ===========================

                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.username,
                        u.email,
                        u.created_at,

                        c.qualification,
                        c.specialization,
                        c.experience

                    FROM users u

                    LEFT JOIN counsellor_details c
                        ON u.user_id = c.user_id

                    WHERE u.user_id = %s
                """, (counsellor_id,))

                counsellor = cursor.fetchone()

                # ===========================
                # PENDING APPOINTMENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM appointments

                    WHERE counsellor_id = %s
                    AND status = 'Pending'
                """, (counsellor_id,))

                pending = cursor.fetchone()["total"]

                # ===========================
                # TODAY'S SESSIONS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM appointments

                    WHERE counsellor_id = %s
                    AND appointment_date = CURDATE()
                    AND status != 'Cancelled'
                """, (counsellor_id,))

                today_sessions = cursor.fetchone()["total"]

                # ===========================
                # COMPLETED SESSIONS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM appointments

                    WHERE counsellor_id = %s
                    AND status = 'Completed'
                """, (counsellor_id,))

                completed = cursor.fetchone()["total"]

                # ===========================
                # STUDENTS UNDER MONITORING
                # ===========================

                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) AS total

                    FROM appointments

                    WHERE counsellor_id = %s
                """, (counsellor_id,))

                students = cursor.fetchone()["total"]

                # ===========================
                # COUNSELLOR STATS
                # ===========================

                stats = {
                    "pending": pending,
                    "today_sessions": today_sessions,
                    "completed": completed,
                    "students": students
                }

                # ===========================
                # COUNSELLING SCHEDULE
                # ===========================

                cursor.execute("""
                    SELECT

                        a.appointment_id,
                        a.appointment_date,
                        a.appointment_time,
                        a.reason,
                        a.status,

                        u.username,
                        u.email,

                        s.class,
                        s.stream

                    FROM appointments a

                    INNER JOIN users u
                        ON a.user_id = u.user_id

                    INNER JOIN student_details s
                        ON u.user_id = s.user_id

                    WHERE a.counsellor_id = %s

                    ORDER BY
                        a.appointment_date ASC,
                        a.appointment_time ASC
                """, (counsellor_id,))

                appointments = cursor.fetchall()

            except mysql.connector.Error as err:

                print(
                    "Counsellor Dashboard Database Error:",
                    err
                )

                flash(
                    "Unable to load counsellor dashboard."
                )

                return redirect(
                    url_for("logout")
                )

            finally:

                cursor.close()
                db.close()

            # ===========================
            # COUNSELLOR PROFILE CHECK
            # ===========================

            if not counsellor:

                flash(
                    "Counsellor profile not found."
                )

                return redirect(
                    url_for("logout")
                )

            # ===========================
            # RENDER DASHBOARD
            # ===========================

            return render_template(
                "counsellor_dashboard.html",

                counsellor=counsellor,

                stats=stats,

                appointments=appointments
            )