from flask import request, jsonify
from functools import wraps
import jwt
from database import dynamodb
from dotenv import load_dotenv
import os

load_dotenv()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, os.getenv["JWT_SECRET_KEY"])
            user_table = dynamodb.Table("GoalForge-Users")
            current_user = user_table.get_item(Key={"UserID": data["userID"]})

            if not "Item" in current_user or not current_user["Item"]:
                return jsonify({"error": "Invalid token"}), 401
        except:
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
