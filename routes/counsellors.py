from flask import (
    render_template,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection

def init_counsellors_routes(app):    

    # ===========================
    # ALL COUNSELLORS PAGE
    # ===========================

    @app.route("/counsellors")
    def counsellors():

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "STUDENT":
            return redirect(url_for("dashboard_redirect"))


        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        try:

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

                LEFT JOIN counsellor_details c
                ON u.user_id = c.user_id


                WHERE r.role = 'COUNSELLOR'

                ORDER BY u.username ASC

            """)


            counsellors = cursor.fetchall()


            #print("COUNSELLORS DATA:", counsellors)



        except mysql.connector.Error as err:

            print(
                "Counsellor Page Error:",
                err
            )

            flash(
                "Unable to load counsellors."
            )

            counsellors = []



        finally:

            cursor.close()
            db.close()



        return render_template(
            "counsellors.html",
            counsellors=counsellors
        )