from flask import (
    render_template,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection

def init_appointment_routes(app):
    # ===========================
    # APPOINTMENT
    # ===========================

    @app.route("/appointment", methods=["GET", "POST"])
    def appointment():

        # ===========================
        # LOGIN CHECK
        # ===========================

        if "user_id" not in session:
            return redirect(url_for("login"))

        # ===========================
        # STUDENT ONLY
        # ===========================

        if session.get("role") != "STUDENT":
            return redirect(url_for("login"))

        student_id = session["user_id"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        try:

            # =================================================
            # POST - BOOK APPOINTMENT
            # =================================================

            if request.method == "POST":

                counsellor_id = request.form.get(
                    "counsellor_id",
                    ""
                ).strip()

                appointment_date = request.form.get(
                    "appointment_date",
                    ""
                ).strip()

                appointment_time = request.form.get(
                    "appointment_time",
                    ""
                ).strip()

                reason = request.form.get(
                    "reason",
                    ""
                ).strip()

                # ===========================
                # REQUIRED FIELDS
                # ===========================

                if (
                    not counsellor_id
                    or not appointment_date
                    or not appointment_time
                ):

                    flash(
                        "Please select counsellor, date and time."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                # ===========================
                # CHECK COUNSELLOR
                # ===========================

                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.username

                    FROM users u

                    INNER JOIN roles r
                        ON u.role_id = r.role_id

                    INNER JOIN counsellor_details c
                        ON u.user_id = c.user_id

                    WHERE u.user_id = %s

                    AND r.role = 'COUNSELLOR'

                    AND u.is_active = TRUE

                    AND u.is_deleted = FALSE
                """, (counsellor_id,))

                counsellor = cursor.fetchone()

                if not counsellor:

                    flash(
                        "Selected counsellor is not available."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                # ===========================
                # CHECK DATE
                # ===========================

                cursor.execute("""
                    SELECT CURDATE() AS today
                """)

                today = cursor.fetchone()["today"]

                from datetime import datetime

                try:

                    selected_date = datetime.strptime(
                        appointment_date,
                        "%Y-%m-%d"
                    ).date()

                except ValueError:

                    flash(
                        "Invalid appointment date."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                if selected_date < today:

                    flash(
                        "Please select today or a future date."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                # ===========================
                # CHECK COUNSELLOR SLOT
                # ===========================

                cursor.execute("""
                    SELECT appointment_id

                    FROM appointments

                    WHERE counsellor_id = %s

                    AND appointment_date = %s

                    AND appointment_time = %s

                    AND status IN (
                        'Pending',
                        'Approved'
                    )
                """, (
                    counsellor_id,
                    appointment_date,
                    appointment_time
                ))

                existing_slot = cursor.fetchone()

                if existing_slot:

                    flash(
                        "This time slot is already booked. Please select another time."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                # ===========================
                # CHECK STUDENT SLOT
                # ===========================

                cursor.execute("""
                    SELECT appointment_id

                    FROM appointments

                    WHERE user_id = %s

                    AND appointment_date = %s

                    AND appointment_time = %s

                    AND status IN (
                        'Pending',
                        'Approved'
                    )
                """, (
                    student_id,
                    appointment_date,
                    appointment_time
                ))

                student_existing = cursor.fetchone()

                if student_existing:

                    flash(
                        "You already have an appointment at this date and time."
                    )

                    return redirect(
                        url_for("appointment")
                    )

                # ===========================
                # INSERT APPOINTMENT
                # ===========================

                cursor.execute("""
                    INSERT INTO appointments
                    (
                        user_id,
                        counsellor_id,
                        appointment_date,
                        appointment_time,
                        reason,
                        status
                    )

                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        'Pending'
                    )
                """, (
                    student_id,
                    counsellor_id,
                    appointment_date,
                    appointment_time,
                    reason if reason else None
                ))

                db.commit()

                flash(
                    "Counselling appointment request submitted successfully."
                )

                return redirect(
                    url_for("student_dashboard")
                )

            # =================================================
            # GET - LOAD COUNSELLORS
            # =================================================

            cursor.execute("""
                SELECT

                    u.user_id,
                    u.username,
                    u.email,

                    c.qualification,
                    c.specialization,
                    c.experience

                FROM users u

                INNER JOIN roles r
                    ON u.role_id = r.role_id

                INNER JOIN counsellor_details c
                    ON u.user_id = c.user_id

                WHERE r.role = 'COUNSELLOR'

                AND u.is_active = TRUE

                AND u.is_deleted = FALSE

                ORDER BY u.username ASC
            """)

            counsellors = cursor.fetchall()

            # ===========================
            # TODAY'S DATE
            # ===========================

            cursor.execute("""
                SELECT CURDATE() AS today
            """)

            today_value = cursor.fetchone()["today"]

            today = today_value.strftime("%Y-%m-%d")

        except mysql.connector.Error as err:

            db.rollback()

            print(
                "Appointment Database Error:",
                err
            )

            flash(
                "Unable to process appointment. Please try again."
            )

            return redirect(
                url_for("student_dashboard")
            )

        finally:

            cursor.close()
            db.close()

        # ===========================
        # RENDER PAGE
        # ===========================

        return render_template(
            "appointment.html",
            counsellors=counsellors,
            today=today
        )