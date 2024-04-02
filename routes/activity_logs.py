from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from dateutil import tz
from middleware.token_required import token_required
from database import dynamodb
from boto3.dynamodb.conditions import Key, Attr

activity_logs_blueprint: Blueprint = Blueprint("activity_logs", __name__)

activity_logs_table = dynamodb.Table("GoalForge-ActivityLogs")

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
@token_required
def get_activity_logs(current_user):
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

    # for log in logs:
    #     log_date = datetime.strptime(log["createdAt"], date_format)
    #     log_date = log_date.replace(tzinfo=from_zone)
    #     log_date = log_date.astimezone(to_zone)

    #     if (
    #         log_date.year == local.year
    #         and log_date.month == local.month
    #         and log_date.day == local.day
    #     ):
    #         logs_today.append(log)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    response = activity_logs_table.query(
        KeyConditionExpression=Key("UserID").eq(current_user["UserID"]),
        FilterExpression=Attr("CreatedAt").begins_with(today),
    )

    logs_today = response["Items"]

    return jsonify(logs_today)


# Add activity log to the database
# Example: POST /api/v1/activity-logs
@activity_logs_blueprint.route("", methods=["POST"])
@token_required
def add_activity_log(current_user):

    activity_log = request.json

    print("ACTIVITY LOG:", activity_log)

    new_activity_log = {
        "UserID": current_user["UserID"],
        "ActivityLogID": activity_log["ActivityLogID"],
        "Text": activity_log["Text"],
        "CreatedAt": activity_log["CreatedAt"],
    }

    activity_logs_table.put_item(Item=new_activity_log)

    return jsonify(activity_log), 201


# Update activity log in the database
# Example: PUT /api/v1/activity_logs/activity_log_id
@activity_logs_blueprint.route("/<string:activity_log_id>", methods=["PUT"])
@token_required
def update_task(current_user, activity_log_id):
    print("TASK ID:", activity_log_id)

    edited_activity_log = request.json

    found_activity_log = activity_logs_table.get_item(
        Key={"UserID": current_user["UserID"], "ActivityLogID": activity_log_id}
    )["Item"]

    if not found_activity_log:
        return jsonify({"error": "Activity log not found"}), 404

    activity_logs_table.update_item(
        Key={
            "UserID": current_user["UserID"],
            "ActivityLogID": activity_log_id,
        },
        UpdateExpression="SET #text = :val1",
        ExpressionAttributeNames={
            "#text": "Text",
        },
        ExpressionAttributeValues={
            ":val1": edited_activity_log["Text"],
        },
    )

    return jsonify(edited_activity_log), 200

    # Test fail
    # return jsonify({"error": "Test fail rollback"}), 500


# Delete activity log in the database
# Example: DELETE /api/v1/activity-logs/activity_log_id
@activity_logs_blueprint.route("/<string:activity_log_id>", methods=["DELETE"])
@token_required
def delete_activity_log(current_user, activity_log_id):
    found_activity_log = None

    found_activity_log = activity_logs_table.get_item(
        Key={"UserID": current_user["UserID"], "ActivityLogID": activity_log_id}
    )["Item"]

    if not found_activity_log:
        return jsonify({"error": "Activity log not found"}), 404

    # Test fail
    # return jsonify({"error": "Test fail rollback"}), 500

    activity_logs_table.delete_item(
        Key={"UserID": current_user["UserID"], "ActivityLogID": activity_log_id}
    )

    return jsonify({"message": "Activity log deleted successfully"}), 200
