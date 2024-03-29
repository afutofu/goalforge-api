import boto3

from flask import current_app

dynamodb_client = boto3.resource(
    "dynamodb",
    aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
)
