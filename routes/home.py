from flask import render_template

def init_home_routes(app):

    @app.route("/")
    def home():
        return render_template("home.html")


    @app.route("/about")
    def about():
        return render_template("about.html")


    @app.route("/assessment")
    def assessment():
        return render_template("assessment.html")