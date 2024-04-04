from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.tasks import tasks_blueprint
from routes.activity_logs import activity_logs_blueprint
from routes.auth import auth_blueprint
import ssl


app = Flask(__name__)

CORS(app)

app.register_blueprint(tasks_blueprint, url_prefix="/api/v1/tasks")
app.register_blueprint(activity_logs_blueprint, url_prefix="/api/v1/activity-logs")
app.register_blueprint(auth_blueprint, url_prefix="/api/v1/auth")

ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ctx.load_cert_chain("certificate.pem", "privateKey.pem")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", ssl_context=ctx)
    # app.run()
    # app.run(debug=True, port=8080)
