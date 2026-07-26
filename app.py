from flask import Flask, render_template

app = Flask(__name__)

# ===========================
# Home Page
# ===========================

@app.route("/")
def home():
    return render_template("home.html")


# ===========================
# About Page
# ===========================

@app.route("/about")
def about():
    return render_template("about.html")


# ===========================
# Assessment Page
# ===========================

@app.route("/assessment")
def assessment():
    return "<h2>Mental Health Assessment Coming Soon...</h2>"


# ===========================
# AI Chat Page
# ===========================

@app.route("/chatbot")
def chatbot():
    return "<h2>AI Chat Support Coming Soon...</h2>"


# ===========================
# Resources Page
# ===========================

@app.route("/resources")
def resources():
    return "<h2>Wellness Resources Coming Soon...</h2>"


# ===========================
# Appointment Page
# ===========================

@app.route("/appointment")
def appointment():
    return "<h2>Counselling Appointment Coming Soon...</h2>"


# ===========================
# Login Page
# ===========================

@app.route("/login")
def login():
    return render_template("login.html")


# ===========================
# Register Page
# ===========================

@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True) 