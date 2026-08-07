from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection    
   
   
    def init_appointment_routes(app):
        # ===========================
        # MY APPOINTMENTS
        # STUDENT + COUNSELLOR
        # ===========================

        @app.route("/my_appointments")
        def my_appointments():

            # ===========================
            # LOGIN CHECK
            # ===========================

            if "user_id" not in session:
                return redirect(url_for("login"))

            user_id = session["user_id"]
            role = session.get("role")

            # ===========================
            # ROLE CHECK
            # ===========================

            if role not in ["STUDENT", "COUNSELLOR"]:
                return redirect(url_for("login"))

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            try:

                # =================================================
                # STUDENT
                # =================================================

                if role == "STUDENT":

                    cursor.execute("""
                        SELECT

                            a.appointment_id,
                            a.appointment_date,
                            a.appointment_time,
                            a.reason,
                            a.status,

                            cuser.username AS counsellor_name,

                            cd.qualification,
                            cd.specialization

                        FROM appointments a

                        INNER JOIN users cuser
                            ON a.counsellor_id = cuser.user_id

                        LEFT JOIN counsellor_details cd
                            ON a.counsellor_id = cd.user_id

                        WHERE a.user_id = %s

                        ORDER BY
                            a.appointment_date DESC,
                            a.appointment_time DESC,
                            a.appointment_id DESC

                    """, (user_id,))

                    appointments = cursor.fetchall()


                # =================================================
                # COUNSELLOR
                # =================================================

                else:

                    cursor.execute("""
                        SELECT

                            a.appointment_id,
                            a.appointment_date,
                            a.appointment_time,
                            a.reason,
                            a.status,

                            suser.username AS student_name,
                            suser.email AS student_email,

                            sd.class AS student_class,
                            sd.stream AS student_stream

                        FROM appointments a

                        INNER JOIN users suser
                            ON a.user_id = suser.user_id

                        LEFT JOIN student_details sd
                            ON a.user_id = sd.user_id

                        WHERE a.counsellor_id = %s

                        ORDER BY
                            a.appointment_date DESC,
                            a.appointment_time DESC,
                            a.appointment_id DESC

                    """, (user_id,))

                    appointments = cursor.fetchall()


            except mysql.connector.Error as err:

                print(
                    "My Appointments Database Error:",
                    err
                )

                flash(
                    "Unable to load appointments."
                )

                if role == "STUDENT":

                    return redirect(
                        url_for("student_dashboard")
                    )

                return redirect(
                    url_for("counsellor_dashboard")
                )

            finally:

                cursor.close()
                db.close()


            # =================================================
            # SAME PAGE
            # =================================================

            return render_template(
                "my_appointments.html",
                appointments=appointments,
                role=role
            )# ===========================
        # APPOINTMENT DETAIL
        # STUDENT + COUNSELLOR
        # ===========================

        @app.route("/appointment_detail/<int:id>", methods=["GET", "POST"])
        def appointment_detail(id):

            # ===========================
            # LOGIN CHECK
            # ===========================

            if "user_id" not in session:
                return redirect(url_for("login"))


            user_id = session["user_id"]
            role = session.get("role")


            # ===========================
            # ROLE CHECK
            # ===========================

            if role not in ["STUDENT", "COUNSELLOR"]:
                return redirect(url_for("login"))


            db = get_db_connection()
            cursor = db.cursor(dictionary=True)


            try:


                # =========================================
                # COUNSELLOR ACTION
                # APPROVE / CANCEL + MESSAGE
                # =========================================

                if request.method == "POST" and role == "COUNSELLOR":


                    action = request.form.get("action")

                    message = request.form.get(
                        "counsellor_message"
                    )


                    if action == "approve":


                        cursor.execute("""
                            UPDATE appointments

                            SET status = 'Approved',
                                counsellor_message = %s

                            WHERE appointment_id = %s
                            AND counsellor_id = %s

                        """,
                        (
                            message,
                            id,
                            user_id
                        ))


                        flash(
                            "Appointment Approved Successfully."
                        )


                    elif action == "cancel":


                        cursor.execute("""
                            UPDATE appointments

                            SET status = 'Cancelled',
                                counsellor_message = %s

                            WHERE appointment_id = %s
                            AND counsellor_id = %s

                        """,
                        (
                            message,
                            id,
                            user_id
                        ))


                        flash(
                            "Appointment Cancelled."
                        )


                    db.commit()



                # =================================================
                # STUDENT VIEW
                # =================================================

                if role == "STUDENT":


                    cursor.execute("""
                        SELECT

                            a.appointment_id,
                            a.appointment_date,
                            a.appointment_time,
                            a.reason,
                            a.status,
                            a.counsellor_message,
                            a.created_at,


                            cuser.user_id AS counsellor_id,
                            cuser.username AS counsellor_name,
                            cuser.email AS counsellor_email,


                            cd.qualification,
                            cd.specialization,
                            cd.experience


                        FROM appointments a


                        INNER JOIN users cuser

                        ON a.counsellor_id = cuser.user_id



                        LEFT JOIN counsellor_details cd

                        ON a.counsellor_id = cd.user_id



                        WHERE a.appointment_id = %s

                        AND a.user_id = %s


                        LIMIT 1

                    """,
                    (
                        id,
                        user_id
                    ))



                    appointment = cursor.fetchone()



                # =================================================
                # COUNSELLOR VIEW
                # =================================================

                else:



                    cursor.execute("""
                        SELECT


                            a.appointment_id,
                            a.appointment_date,
                            a.appointment_time,
                            a.reason,
                            a.status,
                            a.counsellor_message,
                            a.created_at,


                            suser.user_id AS student_id,
                            suser.username AS student_name,
                            suser.email AS student_email,


                            sd.class AS student_class,
                            sd.stream AS student_stream


                        FROM appointments a



                        INNER JOIN users suser

                        ON a.user_id = suser.user_id



                        LEFT JOIN student_details sd

                        ON a.user_id = sd.user_id



                        WHERE a.appointment_id = %s

                        AND a.counsellor_id = %s


                        LIMIT 1


                    """,
                    (
                        id,
                        user_id
                    ))



                    appointment = cursor.fetchone()



            except mysql.connector.Error as err:


                print(
                    "Appointment Detail Error:",
                    err
                )


                flash(
                    "Unable to update appointment."
                )


                return redirect(
                    url_for("my_appointments")
                )



            finally:


                cursor.close()
                db.close()



            # ===========================
            # NOT FOUND
            # ===========================


            if not appointment:


                flash(
                    "Appointment not found."
                )


                return redirect(
                    url_for("my_appointments")
                )



            # ===========================
            # SAME PAGE RENDER
            # ===========================


            return render_template(

                "appointment_detail.html",

                appointment=appointment,

                role=role

            )