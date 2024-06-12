from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from flask_migrate import Migrate
from routes.tasks import tasks_blueprint
from routes.activity_logs import activity_logs_blueprint
from routes.auth import auth_blueprint
import os
from dotenv import load_dotenv

from database import db, db_url

app = Flask(__name__)

load_dotenv()

# Set the secret key to sign the session cookie
app.secret_key = os.getenv("SESSION_SECRET_KEY")

# Enable CORS
CORS(app)

# Register the route blueprints
app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")
app.register_blueprint(activity_logs_blueprint, url_prefix="/api/v1/activity-logs")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")

# Set up the database
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Import models to create tables
from models import Task, User, ActivityLog

# Create the database tables
migrate = Migrate(app, db)

if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", ssl_context=ctx)
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("\n\n----------- Database connection successful !")
            print(db)

            # Create tables if they do not exist
            # db.create_all()

        except Exception as e:
            print("\n\n----------- Connection failed ! ERROR : ", e)

        # app.run()
        app.run(debug=True)
        print("Running server.py")
