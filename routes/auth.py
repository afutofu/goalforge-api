from flask import Blueprint, jsonify, redirect, url_for
from flask.globals import session, request
from flask.wrappers import Response
from datetime import datetime, timezone, timedelta
import jwt
import requests
from database import dynamodb
from dotenv import load_dotenv
import os, pathlib
import json
import google

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

CLIENT_SECRETS_FILE = os.path.join(
    pathlib.Path(__file__).parent.parent, "client-secret.json"
)
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

auth_blueprint: Blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/google")
def login_google():

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
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
        # access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        # include_granted_scopes="true",
    )

    # Store the state so the callback can verify the auth server response.
    session["state"] = state

    resp = Response(
        response=json.dumps({"auth_url": authorization_url}),
        status=200,
        # mimetype="application/json",
    )
    return resp


@auth_blueprint.route("/callback/google")
def oauth_google_callback():

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
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

    # Check if user exists in the databse
    email = id_info["email"]
    name = id_info["name"]
    picture = id_info["picture"]

    user = users_table.get_item(Key={"UserID": email})

    # If user does not exist, register the user in the database
    if not "Item" in user or not user["Item"]:
        users_table.put_item(
            Item={
                "UserID": email,
                "Name": name,
                "Picture": picture,
                "SignInType": "google",
                "CreatedAt": str(datetime.now(tz=timezone.utc)),
            }
        )

    jwt_token = generate_user_info_jwt(email, name, picture)

    return redirect(f"{FRONTEND_URL}?jwt={jwt_token}")


@auth_blueprint.route("/oauth-signin", methods=["POST"])
def oauth_signin():
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


# Generate a JWT
def generate_user_info_jwt(user_id, name, picture):
    encoded_jwt = jwt.encode(
        {
            "userID": user_id,
            "name": name,
            "picture": picture,
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(hours=24),  # 24-hour expiration
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256",
    )

    return encoded_jwt


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
