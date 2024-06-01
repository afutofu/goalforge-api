from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.tasks import tasks_blueprint
from routes.activity_logs import activity_logs_blueprint
from routes.auth import auth_blueprint
import os
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL
from datetime import datetime

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SESSION_SECRET_KEY")

CORS(app)

app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")
app.register_blueprint(activity_logs_blueprint, url_prefix="/api/v1/activity-logs")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")


# postgres_connection_url = f"postgresql://{os.getenv('DB_USER')}:password@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
postgres_connection_url = URL.create(
    "postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),  # plain (unescaped) text
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
)

app.config["SQLALCHEMY_DATABASE_URI"] = postgres_connection_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=True)
    signup_method = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


# def __repr__(self):
#     return "<User %r>" % self.email


if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", ssl_context=ctx)
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    with app.app_context():
        # Create tables
        db.create_all()
        print(db)
        app.run()
        # app.run(debug=True)
        print("Running server.py")
