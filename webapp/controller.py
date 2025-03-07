from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import webapp as webapp
from webapp import mysql

# Initialize MySQL (Make sure it's properly configured in your app)
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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password correctly
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # ✅ Save user to database (assuming you have a users table)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Sign Up Successful!', 'success')
        return redirect(url_for('controller.login'))  # Redirect to login after sign-up
    
    return render_template('signup.html')

@controller.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]  # ✅ Store user ID in session
            flash("Login successful!", "success")
            return redirect(url_for("controller.home"))  # Redirect to home page
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
    cur.execute("SELECT id, id_number, course, year_level, college, gender FROM students")
    students = cur.fetchall()
    cur.close()

    return render_template('home.html', students=students)
