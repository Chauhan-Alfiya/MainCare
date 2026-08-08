from flask import Flask

from routes.home import init_home_routes
from routes.auth import init_auth_routes
from routes.student import init_student_routes
from routes.counsellors import init_counsellors_routes
from routes.counsellors import init_counsellors_routes
from routes.admin import init_admin_routes
from routes.appointment import init_appointment_routes
from routes.my_appointment import init_my_appointment_routes
from routes.wellness_tracker import init_wellness_tracker_routes
from routes.assessment import init_assessment_routes
from routes.resources import init_resources_routes
from routes.chatbot import init_chatbot_routes


app = Flask(__name__)

app.secret_key = "mindcare123"

app.config["UPLOAD_FOLDER"] = "static/resources"


# ===========================
# REGISTER ALL ROUTES
# ===========================

init_home_routes(app)
init_auth_routes(app)
init_student_routes(app)
init_counsellors_routes(app)
init_counsellor_routes(app)
init_admin_routes(app)
init_appointment_routes(app)
init_my_appointment_routes(app)
init_wellness_tracker_routes(app)
init_assessment_routes(app)
init_resources_routes(app)
init_chatbot_routes(app)


# ===========================
# RUN APPLICATION
# ===========================

if __name__ == "__main__":
    app.run(debug=True)