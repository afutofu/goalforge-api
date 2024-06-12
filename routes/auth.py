from flask import Blueprint, jsonify, redirect, url_for
from flask.globals import session, request
from flask.wrappers import Response
from datetime import datetime, timezone, timedelta
import jwt
import requests
from database import dynamodb, db
from models import User
from dotenv import load_dotenv
import os, pathlib
import json
import google

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from middleware.token_required import token_required
from config import hash_value, cipher_suite


SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRETS_FILE_PATH = os.getenv("GOOGLE_CLIENT_SECRET_PATH") or os.path.join(
    pathlib.Path(__file__).parent.parent, "client-secret.json"
)

auth_blueprint: Blueprint = Blueprint("auth", __name__)


# Login with Google OAuth
# Example: GET /api/v1/auth/google
@auth_blueprint.route("/google")
def login_google():

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE_PATH,
        scopes=SCOPES,
    )

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for("auth.oauth_google_callback", _external=True)
    # flow.redirect_uri = BACKEND_URL + "api/v1/auth/callback/google"

    print(flow.redirect_uri)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    # Store the state so the callback can verify the auth server response.
    session["state"] = state

    resp = Response(
        response=json.dumps({"auth_url": authorization_url}),
        status=200,
        # mimetype="application/json",
    )
    return resp


# Google OAuth callback route
@auth_blueprint.route("/callback/google")
def oauth_google_callback():

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE_PATH, scopes=SCOPES)
    flow.redirect_uri = url_for("auth.oauth_google_callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")

    # removing the specific audience, as it is throwing error
    del id_info["aud"]

    email = id_info["email"]
    name = id_info["name"]
    image = id_info["picture"]

    # Check if user exists in the databse
    # found_user = User.query.filter_by(email=email).first()
    hashed_email = hash_value(email)
    print("hashed email", hashed_email)

    found_user = User.query.filter_by(hashed_email=hashed_email).first()

    # If user does not exist, register the user in the database
    if not found_user:
        new_user = User(
            email=email,
            name=name,
            signup_method="google",
        )
        db.session.add(new_user)
        db.session.commit()

        found_user = User.query.filter_by(hashed_email=hashed_email).first()

    decrypted_email = cipher_suite.decrypt(found_user.encrypted_email.encode()).decode()
    decrypted_name = cipher_suite.decrypt(found_user.encrypted_name.encode()).decode()

    # If user either signs in or registers successfully, generate a JWT for the user containing the unique user ID
    jwt_token = generate_user_info_jwt(
        found_user.id, decrypted_email, decrypted_name, image
    )

    # print(jwt_token)

    return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")


# Fetch user info
# Example: GET /api/v1/auth/fetch-user
@auth_blueprint.route("/fetch-user")
@token_required
def fetch_user(current_user):
    return Response(
        response=json.dumps(
            {
                "id": current_user["userID"],
                "name": current_user["name"],
                "email": current_user["email"],
                "image": current_user["image"],
            }
        ),
        status=200,
        mimetype="application/json",
    )


# Logout
# Example: POST /api/v1/auth/logout
@auth_blueprint.route("/logout", methods=["POST"])
@token_required
def logout(current_user):
    # clear session backend
    session.clear()
    return Response(
        response=json.dumps({"message": "Logged out"}),
        status=200,
        mimetype="application/json",
    )


# Generate a JWT
def generate_user_info_jwt(user_id, email, name, image):
    encoded_jwt = jwt.encode(
        {
            "userID": user_id,
            "email": email,
            "name": name,
            "image": image,
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(hours=24),  # 24-hour expiration
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    return encoded_jwt


# DEPRECATED
# Google OAuth callback route
@auth_blueprint.route("/callback/google")
def oauth_google_callback_DEPRECATED():

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE_PATH, scopes=SCOPES)
    flow.redirect_uri = url_for("auth.oauth_google_callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    request_session = requests.session()
    token_request = google.auth.transport.requests.Request(session=request_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )
    session["google_id"] = id_info.get("sub")

    # removing the specific audience, as it is throwing error
    del id_info["aud"]

    try:
        users_table = dynamodb.Table("GoalForge-Users")
    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": "Internal server error when accessing DB"}), 500

    email = id_info["email"]
    name = id_info["name"]
    image = id_info["picture"]

    # Check if user exists in the databse
    user = users_table.get_item(Key={"UserID": email})

    # If user does not exist, register the user in the database
    if not "Item" in user or not user["Item"]:
        users_table.put_item(
            Item={
                "UserID": email,
                "Name": name,
                "Picture": image,
                "SignInType": "google",
                "CreatedAt": str(datetime.now(tz=timezone.utc)),
            }
        )

    jwt_token = generate_user_info_jwt(email, name, image)

    return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")


# DEPRECATED
@auth_blueprint.route("/oauth-signin", methods=["POST"])
def oauth_signin_DEPRECATED():
    # Assuming you are sending JSON data
    sign_in_data = request.json
    sign_in_type = sign_in_data.get("sign_in_type")
    email = sign_in_data.get("email")
    name = sign_in_data.get("name")

    try:
        users_table = dynamodb.Table("GoalForge-Users")
    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": "Internal server error"}), 500

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

    # If user either signs in or registers successfully, generate a JWT for the user containing the unique user ID

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
