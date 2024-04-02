from flask import Blueprint, request, jsonify
from middleware.token_required import token_required
from database import dynamodb
from boto3.dynamodb.conditions import Key

tasks_blueprint: Blueprint = Blueprint("tasks", __name__)

tasks_table = dynamodb.Table("GoalForge-Tasks")

# Mock database
tasks = [
    {
        "id": 1,
        "name": "Exercise",
        "completed": False,
        "period": 1,
        "createdAt": "2024-03-23",
    },
    {
        "id": 2,
        "name": "Laundry",
        "completed": False,
        "period": 1,
        "createdAt": "2024-03-23",
    },
    {
        "id": 3,
        "name": "Cook Dinner",
        "completed": False,
        "period": 1,
        "createdAt": "2024-03-23",
    },
    {
        "id": 4,
        "name": "Buy Groceries",
        "completed": False,
        "period": 2,
        "createdAt": "2024-03-23",
    },
    {
        "id": 5,
        "name": "Dentist Appointment",
        "completed": False,
        "period": 3,
        "createdAt": "2024-03-23",
    },
    {
        "id": 6,
        "name": "Get a new job",
        "completed": False,
        "period": 4,
        "createdAt": "2024-03-23",
    },
]


def mockGetTask(period=0):
    if period == 0:
        return tasks
    elif period == 1:
        return list(filter(lambda x: x["period"] == 1, tasks))
    elif period == 2:
        return list(filter(lambda x: x["period"] == 2, tasks))
    elif period == 3:
        return list(filter(lambda x: x["period"] == 3, tasks))
    elif period == 4:
        return list(filter(lambda x: x["period"] == 4, tasks))
    else:
        return None


# Get tasks from the database
# Example: GET /api/v1/tasks?period=2
# period could be 0, 1, 2, 3, 4
# 0 - all, 1 - day, 2 - week, 3 - month, 4 - year
@tasks_blueprint.route("", methods=["GET"])
@token_required
def get_tasks(current_user):
    period = int(request.args.get("period"))
    # Logic to fetch tasks based on the period
    # tasks = mockGetTask(period)
    tasks = []
    if period == 0:
        tasks_query = tasks_table.query(
            KeyConditionExpression=Key("UserID").eq(current_user["UserID"])
        )

        tasks = tasks_query["Items"]

    if tasks is None:
        response = {"error": "Invalid period specified"}
        return jsonify(response), 400  # Bad Request

    return jsonify(tasks), 200


# Add tasks to the database
# Example: POST /api/v1/tasks
@tasks_blueprint.route("", methods=["POST"])
@token_required
def add_task(current_user):
    task = request.json
    if "Name" not in task:
        response = {"error": "Task name is required"}
        return jsonify(response), 400

    # Test fail rollback
    # return jsonify({"error": "Test fail rollback"}), 500

    # Insert new task to the end of the database
    # tasks.append(task)

    new_task = {
        "UserID": current_user["UserID"],
        "TaskID": task["TaskID"],
        "Name": task["Name"],
        "Completed": task["Completed"],
        "Period": task["Period"],
        "CreatedAt": task["CreatedAt"],
    }

    tasks_table.put_item(Item=new_task)

    return jsonify(new_task), 201


# Update tasks from the database
# Example: PUT /api/v1/tasks/task_id
@tasks_blueprint.route("/<string:task_id>", methods=["PUT"])
@token_required
def update_task(current_user, task_id):
    print("TASK ID:", task_id)

    new_task = request.json

    # for idx, task in enumerate(tasks):
    #     if task["id"] == task_id:
    #         tasks[idx] = new_task

    #         return jsonify(new_task), 200

    found_task = tasks_table.get_item(
        Key={"UserID": current_user["UserID"], "TaskID": task_id}
    )["Item"]

    if not found_task:
        return jsonify({"error": "Task not found"}), 404

    tasks_table.update_item(
        Key={
            "UserID": current_user["UserID"],
            "TaskID": task_id,
        },
        UpdateExpression="SET #name = :val1, #completed = :val2",
        ExpressionAttributeNames={
            "#name": "Name",
            "#completed": "Completed",
        },
        ExpressionAttributeValues={
            ":val1": new_task["Name"],
            ":val2": new_task["Completed"],
        },
        ReturnValues="UPDATED_NEW",
    )

    return jsonify(new_task), 200

    # return jsonify({"error": "Task not found"}), 404

    # Test fail
    # return jsonify({"error": "Test fail rollback"}), 500


# Delete tasks from the database
# Example: DELETE /api/v1/tasks/task_id
@tasks_blueprint.route("/<string:task_id>", methods=["DELETE"])
@token_required
def delete_task(current_user, task_id):
    found_task = None

    # for task in tasks:
    #     if task["id"] == task_id:
    #         found_task = task
    #         break

    found_task = tasks_table.get_item(
        Key={"UserID": current_user["UserID"], "TaskID": task_id}
    )["Item"]

    if not found_task:
        return jsonify({"error": "Task not found"}), 404

    tasks_table.delete_item(Key={"UserID": current_user["UserID"], "TaskID": task_id})

    # Test fail
    # return jsonify({"error": "Test fail rollback"}), 500

    return jsonify({"message": "Task deleted successfully"}), 200
