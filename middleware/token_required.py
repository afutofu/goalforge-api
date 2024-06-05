from flask import request, jsonify
from functools import wraps
import jwt
from dotenv import load_dotenv
import os

load_dotenv()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if request.headers.get("x-auth-token") != None:
            token = request.headers["x-auth-token"]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            print("About to decode token: ", token)
            data = jwt.decode(
                jwt=token,
                key=os.getenv("JWT_SECRET_KEY"),
                algorithms="HS256",
            )
            current_user = data

        except Exception as e:
            print("Error: ", e)
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
