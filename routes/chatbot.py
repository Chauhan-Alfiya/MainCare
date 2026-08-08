from flask import render_template

def init_chatbot_routes(app):
    @app.route("/chatbot")
    def chatbot():

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "STUDENT":
            return redirect(url_for("login"))

        return render_template("chatbot.html")