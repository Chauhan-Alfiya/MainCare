from flask import *
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from routes.database import get_db_connection


def init_admin_routes(app):
        
        # ===========================
        # ADMIN DASHBOARD
        # ===========================

        @app.route("/admin_dashboard")
        def admin_dashboard():

            # ===========================
            # LOGIN CHECK
            # ===========================

            if "user_id" not in session:
                return redirect(url_for("login"))


            # ===========================
            # ADMIN ONLY
            # ===========================

            if session.get("role") != "ADMIN":
                return redirect(url_for("dashboard_redirect"))



            db = get_db_connection()
            cursor = db.cursor(dictionary=True)


            try:


                # ===========================
                # TOTAL STUDENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM users u

                    INNER JOIN roles r
                    ON u.role_id = r.role_id

                    WHERE r.role = 'STUDENT'

                    AND u.is_deleted = FALSE
                """)

                total_students = cursor.fetchone()["total"]



                # ===========================
                # TOTAL COUNSELLORS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM users u

                    INNER JOIN roles r
                    ON u.role_id = r.role_id

                    WHERE r.role = 'COUNSELLOR'

                    AND u.is_deleted = FALSE
                """)

                total_counsellors = cursor.fetchone()["total"]




                # ===========================
                # TOTAL ASSESSMENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM assessments
                """)

                total_assessments = cursor.fetchone()["total"]




                # ===========================
                # TOTAL APPOINTMENTS
                # ===========================

                cursor.execute("""
                    SELECT COUNT(*) AS total

                    FROM appointments
                """)

                total_appointments = cursor.fetchone()["total"]





                # ===========================
                # RECENT STUDENTS
                # ===========================

                cursor.execute("""
                    SELECT

                        u.user_id,
                        u.username,
                        u.email,
                        u.is_active,
                        u.created_at


                    FROM users u


                    INNER JOIN roles r

                    ON u.role_id = r.role_id



                    WHERE r.role = 'STUDENT'


                    AND u.is_deleted = FALSE



                    ORDER BY u.created_at DESC



                    LIMIT 5

                """)


                students = cursor.fetchall()






                # ===========================
                # RECENT COUNSELLORS
                # ===========================

                cursor.execute("""
                    SELECT

                        u.user_id,
                        u.username,
                        u.email,
                        u.is_active,
                        u.created_at


                    FROM users u


                    INNER JOIN roles r

                    ON u.role_id = r.role_id



                    WHERE r.role = 'COUNSELLOR'


                    AND u.is_deleted = FALSE



                    ORDER BY u.created_at DESC



                    LIMIT 5

                """)


                counsellors = cursor.fetchall()






                # ===========================
                # RECENT APPOINTMENTS
                # ===========================

                cursor.execute("""
                    SELECT


                        a.appointment_id,


                        s.username AS student_name,


                        c.username AS counsellor_name,


                        a.appointment_date,


                        a.appointment_time,


                        a.status



                    FROM appointments a



                    INNER JOIN users s

                    ON a.user_id = s.user_id




                    INNER JOIN users c

                    ON a.counsellor_id = c.user_id




                    ORDER BY a.created_at DESC




                    LIMIT 5

                """)


                appointments = cursor.fetchall()






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



                    INNER JOIN users u

                    ON a.user_id = u.user_id




                    ORDER BY a.created_at DESC




                    LIMIT 5

                """)



                assessments = cursor.fetchall()





            except mysql.connector.Error as err:


                print(
                    "Admin Dashboard Error:",
                    err
                )


                flash(
                    "Unable to load admin dashboard."
                )


                return redirect(
                    url_for("logout")
                )



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


                appointments=appointments,


                assessments=assessments

            )