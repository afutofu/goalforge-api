from flask import Blueprint, current_app, request, jsonify
from datetime import datetime
import jwt

auth_blueprint: Blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/api/generate-jwt", methods=["POST"])
def generate_jwt():
    # Assuming you are sending JSON data
    user_data = request.json
    email = user_data.get("email")
    name = user_data.get("name")

    # Generate a JWT
    encoded_jwt = jwt.encode(
        {
            "email": email,
            "name": name,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(hours=24),  # 24-hour expiration
        },
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify(token=encoded_jwt)
