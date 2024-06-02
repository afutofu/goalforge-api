from datetime import datetime
import boto3
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL
from flask import current_app as app

load_dotenv()

# DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

# PostgreSQL connection URL
db_url = URL.create(
    drivername="postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),  # plain (unescaped) text
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
)

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=True)
    signup_method = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<User %r>" % self.email
