# file path: config.py

import os
import base64
import hmac
from hashlib import sha256
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

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


def initialize_user_data(user_id):
    from models import Task
    from models import Category
    from models import ActivityLog

    # Create a few tasks for the user
    # Day tasks
    task1 = Task(text="Buy groceries", completed=False, period=1, user_id=user_id)
    task2 = Task(text="Walk the dog", completed=False, period=1, user_id=user_id)
    task3 = Task(text="Meeting at 1", completed=False, period=1, user_id=user_id)
    task4 = Task(text="Do laundry", completed=False, period=1, user_id=user_id)
    task5 = Task(text="Exercise", completed=False, period=1, user_id=user_id)

    # Week tasks
    task6 = Task(text="Clean the house", completed=False, period=2, user_id=user_id)
    task7 = Task(text="Work on project", completed=False, period=2, user_id=user_id)

    # Month tasks
    task8 = Task(text="Pay bills", completed=False, period=3, user_id=user_id)
    task9 = Task(text="Plan vacation", completed=False, period=3, user_id=user_id)

    # Year tasks
    task10 = Task(text="Set goals", completed=False, period=4, user_id=user_id)
    task11 = Task(text="Review progress", completed=False, period=4, user_id=user_id)

    # Add tasks to the database
    db.session.add(task1)
    db.session.add(task2)
    db.session.add(task3)
    db.session.add(task4)
    db.session.add(task5)
    db.session.add(task6)
    db.session.add(task7)
    db.session.add(task8)
    db.session.add(task9)
    db.session.add(task10)
    db.session.add(task11)
    db.session.commit()

    # Create a few categories for the user
    category1 = Category(name="No Category", color="#ffffff", user_id=user_id)
    category2 = Category(name="Personal", color="#00ff00", user_id=user_id)
    category3 = Category(name="Work", color="#0000ff", user_id=user_id)
    category4 = Category(name="Health", color="#ff0000", user_id=user_id)

    # Add categories to the database
    db.session.add(category1)
    db.session.add(category2)
    db.session.add(category3)
    db.session.add(category4)
    db.session.commit()

    # Create an activity log for the user
    activity_log = ActivityLog(text="Registered to GoalForge", user_id=user_id)

    # Add activity log to the database
    db.session.add(activity_log)
    db.session.commit()

    # Add tasks to categories
    # Personal category
    category2.tasks.append(task1)
    category2.tasks.append(task2)
    category2.tasks.append(task4)
    category2.tasks.append(task6)
    category2.tasks.append(task8)
    category2.tasks.append(task9)
    category2.tasks.append(task10)

    # Work category
    category3.tasks.append(task3)
    category3.tasks.append(task7)
    category3.tasks.append(task11)

    # Health category
    category4.tasks.append(task5)

    db.session.commit()
