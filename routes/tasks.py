from flask import Blueprint, request, jsonify

tasks_blueprint: Blueprint = Blueprint("tasks", __name__)

# Mock data
day_tasks = [{"id":1, "name": "Exercise", "completed": False, "createdAt": "2024-03-23"},
             {"id":2, "name": "Laundry", "completed": False, "createdAt": "2024-03-23"},
             {"id":3, "name": "Cook Lunch", "completed": False, "createdAt": "2024-03-23"}]
week_tasks = []
month_tasks = []
year_tasks = []

# @app.route("/api/tasks/day", methods=["GET"])
# def get_day_tasks():
#     response = {"data": day_tasks}
#     return jsonify(response)

# Example: /api/v1/tasks?period=week
# period could be day, week, month, year
@tasks_blueprint.route("", methods=["GET"])
def get_year_tasks():
    period = request.args.get('period')
    # Logic to fetch tasks based on the period
    if period == 'day':
        response = {"data": day_tasks}
    elif period == 'week':
        response = {"data": week_tasks}
    elif period == 'month':
        response = {"data": month_tasks}
    elif period == 'year':
        response = {"data": year_tasks}
    else:
        response = {"error": "Invalid period specified"}
        return jsonify(response), 400  # Bad Request
    return jsonify(response)