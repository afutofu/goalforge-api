from flask import Blueprint, request, jsonify

tasks_blueprint: Blueprint = Blueprint("tasks", __name__)



# Mock data

tasks = [{"id":1, "name": "Exercise", "completed": False, "period":1, "createdAt": "2024-03-23"},
             {"id":2, "name": "Laundry", "completed": False, "period":1, "createdAt": "2024-03-23"},
             {"id":3, "name": "Cook Dinner", "completed": False, "period":1, "createdAt": "2024-03-23"}]


def mockGetTask(period=1):
    if period == 1:
        return list(filter(lambda x: x['period'] == 1, tasks))
    elif period == 2:
        return list(filter(lambda x: x['period'] == 2, tasks))
    elif period == 3:
        return list(filter(lambda x: x['period'] == 3, tasks))
    elif period == 4:
        return list(filter(lambda x: x['period'] == 4, tasks))
    else:
        return None

# Example: /api/v1/tasks?period=week
# period could be 1, 2, 3, 4
# 1 - day, 2 - week, 3 - month, 4 - year
@tasks_blueprint.route("", methods=["GET"])
def get_year_tasks():
    period =  int(request.args.get('period'))
    # Logic to fetch tasks based on the period
    tasks = mockGetTask(period)

    if tasks is None:
        response = {"error": "Invalid period specified"}
        return jsonify(response), 400  # Bad Request

    return jsonify(tasks)