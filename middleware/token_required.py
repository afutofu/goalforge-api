from flask import current_app, request, jsonify
from functools import wraps
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"])
        except:
            return jsonify({"error": "Token is invalid"}), 401
