from flask import Blueprint, request, jsonify

tasks_blueprint: Blueprint = Blueprint("tasks", __name__)


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
def get_tasks():
    period = int(request.args.get("period"))
    # Logic to fetch tasks based on the period
    tasks = mockGetTask(period)

    if tasks is None:
        response = {"error": "Invalid period specified"}
        return jsonify(response), 400  # Bad Request

    return jsonify(tasks)


# Add tasks to the database
# Example: POST /api/v1/tasks
@tasks_blueprint.route("", methods=["POST"])
def add_task():
    task = request.json
    if "name" not in task:
        response = {"error": "Task name is required"}
        return jsonify(response), 400

    # Test fail rollback
    # return jsonify({"error": "Test fail rollback"}), 500

    # Insert new task to the end of the database
    tasks.append(task)

    return jsonify(task), 201


# Delete tasks from the database
# Example: DELETE /api/v1/tasks/task_id
@tasks_blueprint.route("/<string:task_id>", methods=["DELETE"])
def delete_task(task_id):
    print("TASK ID:", task_id)

    found_task = None

    for task in tasks:
        print("CURRENT TASK ID:", task["id"])
        if task["id"] == task_id:
            found_task = task
            break

    if not found_task:
        return jsonify({"error": "Task not found"}), 404

    # Test fail
    # return jsonify({"error": "Test fail rollback"}), 500

    tasks.remove(found_task)

    return jsonify({"message": "Task deleted successfully"}), 200
