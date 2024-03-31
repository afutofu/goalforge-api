from flask import Blueprint, current_app, request, jsonify
from datetime import datetime, timezone, timedelta
import jwt
from database import dynamodb_client
from dotenv import load_dotenv
import os

load_dotenv()

auth_blueprint: Blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/oauth-signin", methods=["POST"])
def oauth_signin():
    # Assuming you are sending JSON data
    sign_in_data = request.json
    sign_in_type = sign_in_data.get("sign_in_type")
    email = sign_in_data.get("email")
    name = sign_in_data.get("name")

    try:
        users_table = dynamodb_client.Table("GoalForge-Users")
    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": "Internal server error"}), 500

    print("test generate_jwt")

    # Check if data is valid
    if not sign_in_type or not email or not name:
        response = {"error": "Invalid data"}
        return jsonify(response), 400

    # Check if user exists in the databse
    user = None
    if sign_in_type == "google":
        user = users_table.get_item(Key={"UserID": email})

    # If user does not exist, register the user in the database
    if not "Item" in user or not user["Item"]:
        users_table.put_item(
            Item={
                "UserID": email,
                "Name": name,
                "SignInType": sign_in_type,
                "CreatedAt": str(datetime.now(tz=timezone.utc)),
            }
        )

    # In either case, generate a JWT for the user containing the unique user ID

    # Generate a JWT
    encoded_jwt = jwt.encode(
        {
            "userID": email,
            "name": name,
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(hours=24),  # 24-hour expiration
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    return jsonify(token=encoded_jwt)
