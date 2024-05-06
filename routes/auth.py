from flask import Blueprint, request, jsonify, redirect, session, url_for
from datetime import datetime, timezone, timedelta
import jwt
from database import dynamodb
from dotenv import load_dotenv
import os

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

CLIENT_SECRETS_FILE = "../client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

auth_blueprint: Blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/google")
def login_google():

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for("oauth_google_callback", _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    # Store the state so the callback can verify the auth server response.
    session["state"] = state

    return redirect(authorization_url)


@auth_blueprint.route("/callback/google")
def oauth_google_callback():
    # Specify the state when creating the flow in the callback so that it can be
    # verified in the authorization server response.
    state = session["state"]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = url_for("oauth_google_callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)

    return redirect(f"{FRONTEND_URL}?jwt={"jwt_token"}")
    """ return Response(
        response=json.dumps({'JWT':jwt_token}),
        status=200,
        mimetype='application/json'
    ) """


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


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
