from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

activity_logs_blueprint: Blueprint = Blueprint("activity_logs", __name__)


# Mock database
now = datetime.now()
logs = [
    {
        "id": 1,
        "text": "Work",
        "createdAt": (now + timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 2,
        "text": "Eat Lunch",
        "createdAt": (now + timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 3,
        "text": "Finish workout",
        "createdAt": (now + timedelta(hours=-2)).strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 4,
        "text": "Workout",
        "createdAt": (now + timedelta(hours=-3)).strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 5,
        "text": "Prepare to workout",
        "createdAt": (now + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 6,
        "text": "Eat Breakfast",
        "createdAt": (now + timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S"),
    },
]


# Get tasks from the database
# Example: GET /api/v1/tasks?period=2
# period could be 0, 1, 2, 3, 4
# 0 - all, 1 - day, 2 - week, 3 - month, 4 - year
@activity_logs_blueprint.route("", methods=["GET"])
def get_tasks():
    # If date is not provided, use the current date
    date = request.args.get("date")
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    print("DATE:", date)
    date_format = "%Y-%m-%d"
    date_obj = datetime.strptime(date, date_format)

    print(logs)

    return jsonify(logs)

    if logs is None:
        response = {"error": "Invalid period specified"}
        return jsonify(response), 400  # Bad Request
