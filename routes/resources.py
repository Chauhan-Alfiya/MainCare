from flask import (
    render_template,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from routes.database import get_db_connection


def init_resources_routes(app):
        
        ## ===========================
        # WELLNESS RESOURCES
        # ===========================

        @app.route("/resources", methods=["GET", "POST"])
        def resources():

            if "user_id" not in session:
                return redirect(url_for("login"))

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            # ADD RESOURCE
            if request.method == "POST" and session.get("role") == "ADMIN":
                print(request.form)
                print(request.form)   # Testing

                title = request.form["title"]
                category = request.form["category"]
                description = request.form["description"]
                language = request.form["language"]
                pdf = request.files["pdf"]  
                filename = secure_filename(pdf.filename)
                pdf.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        filename
                    )
                )

                file_path = "resources/" + filename

                cursor.execute("""
                    INSERT INTO wellness_resources
                    (title, category, description, language, file_path)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (
                    title,
                    category,
                    description,
                    language,
                    file_path
                ))
                cursor.execute("""
                    INSERT INTO wellness_resources
                    (title, category, description, language, file_path)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    title,
                    category,
                    description,
                    language,
                    file_path
                ))

                db.commit()
                flash("Resource Added Successfully!")
                return redirect(url_for("resources"))

            # SHOW RESOURCES
            cursor.execute("""
                SELECT *
                FROM wellness_resources
                ORDER BY resource_id DESC
            """)

            resources = cursor.fetchall()

            cursor.close()
            db.close()

            return render_template(
                "resources.html",
                resources=resources
            )
            # ===========================
        # EDIT RESOURCE
        # ===========================

        @app.route("/edit_resource/<int:resource_id>", methods=["GET", "POST"])
        def edit_resource(resource_id):

            if "user_id" not in session:
                return redirect(url_for("login"))

            if session.get("role") != "ADMIN":
                return redirect(url_for("dashboard_redirect"))

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            if request.method == "POST":

                title = request.form["title"]
                category = request.form["category"]
                description = request.form["description"]
                language = request.form["language"]
                file_path = request.form["file_path"]

                cursor.execute("""

                    UPDATE wellness_resources

                    SET

                        title=%s,
                        category=%s,
                        description=%s,
                        language=%s,
                        file_path=%s

                    WHERE resource_id=%s

                """,(

                    title,
                    category,
                    description,
                    language,
                    file_path,
                    resource_id

                ))

                db.commit()

                flash("Resource Updated Successfully!")

                cursor.close()
                db.close()

                return redirect(url_for("resources"))

            cursor.execute("""

                SELECT *

                FROM wellness_resources

                WHERE resource_id=%s

            """,(resource_id,))

            resource = cursor.fetchone()

            cursor.close()
            db.close()

            return render_template(

                "edit_resource.html",

                resource=resource

            )
            # ===========================
        # DELETE RESOURCE
        # ===========================

        @app.route("/delete_resource/<int:resource_id>")
        def delete_resource(resource_id):

            print("Deleting:", resource_id)

            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM wellness_resources WHERE resource_id=%s",
                (resource_id,)
            )

            print(cursor.rowcount)

            db.commit()

            cursor.close()
            db.close()

            flash("Deleted")

            return redirect(url_for("resources"))