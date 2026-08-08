from flask import render_template

def init_assessment_routes(app):

    @app.route("/assessment")
    def assessment():
        return render_template("assessment.html")