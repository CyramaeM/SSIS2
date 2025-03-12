from flask import Flask
from flask_mysqldb import MySQL
#from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY
from flask_wtf.csrf import CSRFProtect
import cloudinary
import cloudinary.uploader
import cloudinary.api



mysql = MySQL()

def create_app():
    app = Flask(__name__, template_folder="templates", instance_relative_config=True)
    
    # MySQL Configurations
    app.config["SECRET_KEY"] = "blue"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = "root"
    app.config["MYSQL_DB"] = "app"
    app.config["MYSQL_HOST"] = "127.0.0.1"
    app.config["MYSQL_PORT"] = 3306
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"

    cloudinary.config(
        cloud_name = 'dbth29nsw',
        api_key = '875432953529479',
        api_secret = 'Pd9SnwsUh40BXu67DaOh6LcxI4s'
        )
    mysql.init_app(app)

    with app.app_context():
        try:
            conn = mysql.connection
            if conn:
                print("✅ MySQL Connection Successful")
                cur = conn.cursor()
                cur.execute("SELECT DATABASE();")
                print("Connected to Database:", cur.fetchone())
            else:
                print("❌ MySQL Connection Failed!")
        except Exception as e:
            print("❌ MySQL Connection Error:", e)

    CSRFProtect(app)

    from webapp.controller import controller
    app.register_blueprint(controller)

    return app
