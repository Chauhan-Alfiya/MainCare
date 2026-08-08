from flask import (
    render_template,
    redirect,
    request,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection

def  init_wellness_tracker_routes(app):
        
        # ===========================
        # WELLNESS TRACKER
        # ===========================

        @app.route("/wellness_tracker", methods=["GET", "POST"])
        def wellness_tracker():

            # Login Check
            if "user_id" not in session:
                return redirect(url_for("login"))

            user_id = session["user_id"]

            if request.method == "POST":

                mood = request.form["mood"]
                stress_level = request.form["stress_level"]
                sleep_hours = request.form["sleep_hours"]
                note = request.form["note"]

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO wellness_tracker
                    (user_id, mood, stress_level, sleep_hours, note)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    user_id,
                    mood,
                    stress_level,
                    sleep_hours,
                    note
                ))

                conn.commit()
                cursor.close()
                conn.close()

                flash("Wellness record saved successfully.")

                return redirect(url_for("wellness_tracker"))

            return render_template(
                "wellness_tracker.html",
                role=session.get("role")
            )
            # ===========================
        # WELLNESS HISTORY
        # ===========================

        @app.route("/wellness_history")
        def wellness_history():

            if "user_id" not in session:
                return redirect(url_for("login"))

            user_id = session["user_id"]

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM wellness_tracker
                WHERE user_id=%s
                ORDER BY created_at DESC
            """,(user_id,))

            records = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template(
                "wellness_history.html",
                records=records,
                role=session.get("role")
            )