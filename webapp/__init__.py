from flask import Flask
from flask_mysqldb import MySQL
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY
from flask_wtf.csrf import CSRFProtect

mysql = MySQL()

def create_app():
    app = Flask(__name__, template_folder="templates", instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DB=DB_NAME,  # Use MYSQL_DB instead of MYSQL_DATABASE
        MYSQL_HOST=DB_HOST
    )

    mysql.init_app(app)
    CSRFProtect(app)  # Correct CSRF setup

    from.controller import controller
    app.register_blueprint(controller)

    return app  # Ensure you return the app instance
