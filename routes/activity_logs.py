from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from dateutil import tz

activity_logs_blueprint: Blueprint = Blueprint("activity_logs", __name__)


# Mock database
utcNow = datetime.now(timezone.utc)
logs = [
    {
        "id": 10,
        "text": "Work",
        "createdAt": (utcNow + timedelta(days=-1, hours=-1))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 11,
        "text": "Work",
        "createdAt": (utcNow + timedelta(days=-1, hours=-1))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 1,
        "text": "Work",
        "createdAt": (utcNow + timedelta(hours=-1))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 2,
        "text": "Eat Lunch",
        "createdAt": (utcNow + timedelta(hours=-2))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 3,
        "text": "Finish workout",
        "createdAt": (utcNow + timedelta(hours=-2))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 4,
        "text": "Workout",
        "createdAt": (utcNow + timedelta(hours=-3))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 5,
        "text": "Prepare to workout",
        "createdAt": (utcNow + timedelta(hours=-4))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
    {
        "id": 6,
        "text": "Eat Breakfast",
        "createdAt": (utcNow + timedelta(hours=-4))
        .isoformat(timespec="seconds")
        .replace("+00:00", "")
        + "Z",
    },
]


# Get tasks from the database
# Example: GET /api/v1/activity-logs?date=2024-03-27T01:53:36Z
# "date" query parameter is in UTC
@activity_logs_blueprint.route("", methods=["GET"])
def get_tasks():
    # If date is not provided, use the current date
    date = request.args.get("date").replace(" ", " ")
    if date is None:
        response = {"error": "Invalid date specified"}
        return jsonify(response), 400  # Bad Request

    print("DATE UTC:", date)
    date_format = "%Y-%m-%dT%H:%M:%SZ"

    # Parse the string into a datetime object
    dt_naive = datetime.strptime(date, date_format)

    from_zone = tz.gettz("UTC")
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    dt_aware = dt_naive.replace(tzinfo=from_zone)

    # Convert the datetime object to the local time zone
    local = dt_aware.astimezone(to_zone)

    print("DATE DT_AWARE:", dt_aware)
    print("DATE LOCAL:", local)

    logs_today = []

    for log in logs:
        log_date = datetime.strptime(log["createdAt"], date_format)
        log_date = log_date.replace(tzinfo=from_zone)
        log_date = log_date.astimezone(to_zone)

        if (
            log_date.year == local.year
            and log_date.month == local.month
            and log_date.day == local.day
        ):
            logs_today.append(log)

    return jsonify(logs_today)


# Get tasks from the database
# Example: POST /api/v1/activity-logs
@activity_logs_blueprint.route("", methods=["POST"])
def add_activity_log():

    acitivity_log = request.json

    print("ACTIVITY LOG:", acitivity_log)

    #  insert activity log into the first position of the database (as it represents the latest item in logs list)
    logs.insert(0, acitivity_log)

    return jsonify(acitivity_log), 201
