from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Mock data
day_tasks = [{"id":1, "name": "Exercise", "completed": False, "createdAt": "2024-03-23"},
             {"id":2, "name": "Laundry", "completed": False, "createdAt": "2024-03-23"},
             {"id":3, "name": "Cook Lunch", "completed": False, "createdAt": "2024-03-23"}]
week_tasks = []
month_tasks = []
year_tasks = []

@app.route("/api/tasks/day", methods=["GET"])
def get_day_tasks():
    response = {"day_tasks": day_tasks}
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=8080)