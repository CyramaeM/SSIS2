from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import webapp as webapp
from webapp import mysql
mysql = MySQL()

controller = Blueprint('controller', __name__)

@controller.route("/")
def base():
    return render_template('base.html')

@controller.route("/index")
def index():
    return render_template("index.html")

@controller.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')  # Ensures form loads correctly

    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash("Please fill in all fields", "danger")
        return redirect(url_for("controller.signup"))

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            mysql.connection.commit()
            flash("Sign Up Successful!", "success")
            return redirect(url_for("controller.login"))  # Redirect after success
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.signup"))

import MySQLdb.cursors  # Make sure this is imported

@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # ✅ Use DictCursor to get dictionary results
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Debugging logs
        print("Fetched user:", user)

        if not user:
            flash("Invalid email or password", "danger")
            return redirect(url_for("controller.login"))

        user_id = user["id"]
        hashed_password = user["password"]

        print("Stored password hash:", hashed_password)  # Debugging output

        if check_password_hash(hashed_password, password):  
            session["user_id"] = user_id
            flash("Login successful!", "success")
            return redirect(url_for("controller.home"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")




@controller.route('/home')
def home():
    # ✅ Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))  # Redirect to login page

    # ✅ Fetch students' data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT  id_number,fname, lname, course, yearlevel, course, gender FROM students")
    students = cur.fetchall()
    cur.close()

    return render_template('home.html', students=students)
