from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.tasks import tasks_blueprint
from routes.activity_logs import activity_logs_blueprint
from routes.auth import auth_blueprint
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SESSION_SECRET_KEY")

CORS(app)

app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")
app.register_blueprint(activity_logs_blueprint, url_prefix="/api/v1/activity-logs")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")

if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", ssl_context=ctx)
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    app.run()
    # app.run(debug=True, port=8080)
