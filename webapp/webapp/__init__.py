from flask import Flask
from flask_mysql_connector import MySQL
import mysql.connector
import pandas as pd


def create_app():
    app = Flask(__name__,template_folder=="templates",instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = SECRET_KEY,
        MYSQL_USER = DB_USERNAME,
        MYSQL_PASSWORD = DB_PASSWORD,
        MYSQL_DATABASE = DB_NAME,
        MYSQL_HOST = DB_HOST
    )

def Query(query,params={},mode="SELECT"):
    final=None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123",
            database="safe_and_sure"
        )

        with conn.cursor() as cursor:
            if mode=="PANDAS":
                final=pd.read_sql(query,conn,params=params)
            else:
                cursor.execute(query,params)
                if mode=="SELECT":
                    final=cursor.fetchall()
                else:
                    conn.commit()
    finally:
        conn.close()
    return final