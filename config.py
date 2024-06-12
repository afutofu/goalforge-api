# file path: config.py

import os
import base64
import hmac
from hashlib import sha256
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()

# Retrieve the encryption key from environment variables
encryption_key = os.getenv("ENCRYPTION_KEY")
if encryption_key is None:
    raise ValueError("No encryption key found in environment variables.")
cipher_suite = Fernet(encryption_key.encode())

# Retrieve the HMAC key from environment variables
hmac_key = os.getenv("HMAC_KEY")
if hmac_key is None:
    raise ValueError("No HMAC key found in environment variables.")
hmac_key = base64.urlsafe_b64decode(hmac_key.encode())


def hash_value(value):
    return hmac.new(hmac_key, value.encode(), sha256).hexdigest()


# Password hashing and checking functions
def hash_password(password):
    return generate_password_hash(password)


def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)
