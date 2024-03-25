from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.tasks import tasks_blueprint

app = Flask(__name__)
CORS(app)

app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")

if __name__ == "__main__":
    app.run(debug=True, port=8080)
