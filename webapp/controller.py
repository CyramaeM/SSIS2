from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import webapp as webapp
from webapp import mysql
import cloudinary
import cloudinary.uploader
mysql = MySQL()

controller = Blueprint('controller', __name__)
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

# Class error:
class Error(Exception):
    # Base class for other EXCEPTIONS
    pass
class InvalidID(Error):
    # Raise when an ID is invalid
    pass

class IDExists(Error):
    # Raise when an ID already exists
    pass

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

@controller.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user session
    flash("You have been logged out.", "info")
    return redirect(url_for('controller.login'))



@controller.route('/home')
def home():
    # ✅ Ensure the user is logged in
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))  # Redirect to login page

    # ✅ Fetch students' data from the database as dictionaries
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # ✅ Use DictCursor
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    
    cur.close()
    return render_template('home.html', students=students)

@controller.route('/addstudent', methods=['GET', 'POST'])
def add_student():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
        cur.execute("SELECT coursecode FROM course")  
        courses = [row['coursecode'] for row in cur.fetchall()]  # Fetch course codes correctly
        cur.close()
    except Exception as e:
        print("Database Error:", e)
        courses = []  # Ensure courses is at least an empty list to avoid NameError

    if request.method == 'GET':
        return render_template('add_student.html', courses=courses)  # Ensure courses is passed

    # Handle POST request (form submission)
    id_number = request.form.get('id_number')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    course = request.form.get('course')
    year_level = request.form.get('year_level')
    college = request.form.get('college')
    gender = request.form.get('gender')

    # Handle file upload
    profile_photo = request.files['profile_photo']
    upload_result = None
    if profile_photo:
        upload_result = cloudinary.uploader.upload(profile_photo)

    # Get the secure URL of the uploaded photo
    photo_url = upload_result['secure_url'] if upload_result else 'default_profile.png'

    if not id_number or not course or not year_level or not college or not gender:
        flash("Please fill in all fields", "danger")
        return redirect(url_for("controller.add_student"))

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("INSERT INTO students (id_number, fname, lname, course, year_level, college, gender, profile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (id_number, fname, lname, course, year_level, college, gender, photo_url))
            mysql.connection.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for("controller.home"))
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.add_student"))


@controller.route('/editstudent/<string:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
        cur.execute("SELECT coursecode FROM course")  
        courses = [row['coursecode'] for row in cur.fetchall()]  # Fetch course codes correctly
        cur.close()
    except Exception as e:
        print("Database Error:", e)
        courses = []  # Ensure courses is at least an empty list to avoid NameError

    if request.method == 'GET':
        return render_template('add_student.html', courses=courses)  # Ensure courses is passed
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id_number, fname, lname, course, yearlevel, course, gender FROM students WHERE id_number = %s", (student_id,))
            student = cur.fetchone()

        if not student:
            flash("Student not found.", "danger")
            return redirect(url_for("controller.home"))

        if request.method == 'POST':
            id_number = request.form.get('id_number')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            course = request.form.get('course')
            yearlevel = request.form.get('yearlevel')
            course = request.form.get('course')
            gender = request.form.get('gender')

            if not id_number or not fname or not lname or not course or not yearlevel or not course or not gender:
                flash("Please fill in all fields", "danger")
                return redirect(url_for("controller.edit_student", student_id=student_id))

            with mysql.connection.cursor() as cur:
                cur.execute("""
                    UPDATE students 
                    SET id_number=%s, fname=%s, lname=%s, course=%s, yearlevel=%s, course=%s, gender=%s 
                    WHERE id_number=%s
                """, (id_number, fname, lname, course, yearlevel, course, gender, student_id))
                mysql.connection.commit()
                flash("Student updated successfully!", "success")
                return redirect(url_for("controller.home"))

        return render_template('edit_student.html', student=student)
    
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.home"))


    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.home"))

    return render_template('edit_student.html', student=student)

@controller.route('/delete_student/<string:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM students WHERE id_number = %s", (student_id,))
        mysql.connection.commit()
        cur.close()
        flash("Student deleted successfully!", "success")
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
    
    return redirect(url_for("controller.home"))

