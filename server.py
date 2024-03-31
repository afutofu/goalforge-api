from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.tasks import tasks_blueprint
from routes.activity_logs import activity_logs_blueprint
from routes.auth import auth_blueprint

app = Flask(__name__)

CORS(app)

app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")
app.register_blueprint(activity_logs_blueprint, url_prefix="/api/v1/activity-logs")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
