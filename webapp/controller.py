from tkinter import NO
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import webapp as webapp
from webapp import mysql,csrf
import cloudinary
import cloudinary.uploader
mysql = MySQL()

controller = Blueprint('controller', __name__)
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

class Error(Exception):
    pass
class InvalidID(Error):
    pass

class IDExists(Error):
    pass

@controller.route("/")
@csrf.exempt
def base():
    return render_template('base.html')

@controller.route("/index")
@csrf.exempt
def index():
    return render_template("index.html")

@controller.route('/signup', methods=['GET', 'POST'])
@csrf.exempt
def signup():
    if request.method == 'GET':
        return render_template('signup.html') 

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
            return redirect(url_for("controller.login"))  
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.signup"))

import MySQLdb.cursors 

@controller.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        print("Fetched user:", user)

        if not user:
            flash("Invalid email or password", "danger")
            return redirect(url_for("controller.login"))

        user_id = user["id"]
        hashed_password = user["password"]

        print("Stored password hash:", hashed_password)

        if check_password_hash(hashed_password, password):  
            session["user_id"] = user_id
            flash("Login successful!", "success")
            return redirect(url_for("controller.home"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@controller.route('/logout')
@csrf.exempt
def logout():
    session.pop('user_id', None) 
    flash("You have been logged out.", "info")
    return redirect(url_for('controller.login'))



from flask import request

@controller.route('/home')
@csrf.exempt
def home():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))

 
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

       
        cur.execute("SELECT * FROM students LIMIT %s OFFSET %s", (per_page, offset))
        students = cur.fetchall()

  
        cur.execute("SELECT COUNT(*) AS total FROM students")
        total_students = cur.fetchone()['total']
        total_pages = (total_students + per_page - 1) // per_page

        cur.close()

        return render_template(
            'home.html',
            students=students,
            page=page,
            total_pages=total_pages
        )

    except Exception as e:
        flash(f"An error occurred while fetching data: {e}", "danger")
        return redirect(url_for('controller.login'))



@controller.route('/addstudent', methods=['GET', 'POST'])
@csrf.exempt
def add_student():
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
        cur.execute("SELECT coursecode FROM course")  
        courses = [row['coursecode'] for row in cur.fetchall()]
        cur.close()
    except Exception as e:
        print("Database Error:", e)
        courses = [] 

    if request.method == 'GET':
        return render_template('add_student.html', courses=courses) 

 
    stud_id = request.form.get('stud_id')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    course = request.form.get('course')
    yearlevel = request.form.get('yearlevel')
    gender = request.form.get('gender')
    profile_photo = request.files['profile_photo']
    
    upload_result = None
    if profile_photo:
        upload_result = cloudinary.uploader.upload(profile_photo)

    photo_url = upload_result['secure_url'] if upload_result else 'default_profile.png'
    photo_public_id = upload_result['public_id'] if upload_result else None

    if not stud_id or not course or not yearlevel or not gender:
        flash("Please fill in all fields", "danger")
        return redirect(url_for("controller.add_student"))

    try:
        with mysql.connection.cursor() as cur:
            cur.execute("INSERT INTO students (id_number, fname, lname, course, yearlevel, gender, profile,profile_id) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)", 
                        (stud_id, fname, lname, course, yearlevel, gender, photo_url,photo_public_id))
            mysql.connection.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for("controller.home"))
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for("controller.add_student"))


@controller.route('/editstudent/<string:student_id>', methods=['GET', 'POST'])
@csrf.exempt
def edit_student(student_id):
    with mysql.connection.cursor() as cur:
        if request.method == 'POST':
            id_number = request.form['id_number']
            fname = request.form['fname']
            lname = request.form['lname']
            course = request.form['course']
            yearlevel = request.form['yearlevel']
            gender = request.form['gender']
            
            cur.execute("""
                UPDATE students 
                SET id_number=%s, fname=%s, lname=%s, course=%s, yearlevel=%s, gender=%s 
                WHERE id_number=%s
            """, (id_number, fname, lname, course, yearlevel, gender, student_id))
            
            mysql.connection.commit()
            flash("Student updated successfully!", "success")
            return redirect(url_for("controller.home"))

        else:
            cur.execute("SELECT * FROM students WHERE id_number = %s", (student_id,))
            student = cur.fetchone()

            return render_template('edit_student.html', student=student)


@controller.route('/delete_student/<string:student_id>', methods=['POST'])
@csrf.exempt
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute("SELECT profile_id FROM students WHERE id_number = %s", (student_id,))
        student = cur.fetchone()
        profile_public_id = student.get('profile_id') if student else None

    
        cur.execute("DELETE FROM students WHERE id_number = %s", (student_id,))
        mysql.connection.commit()
        cur.close()

 
        if profile_public_id:
            cloudinary.uploader.destroy(profile_public_id)

        flash("Student deleted successfully!", "success")
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred. Please try again.", "danger")
    
    return redirect(url_for("controller.home"))

@controller.route('/collegeh')
@csrf.exempt
def collegehome():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    
    # Fetch all colleges
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT collegecode, collegename FROM college")
    colleges = cur.fetchall()

    return render_template('college.html', colleges=colleges)

@controller.route('/addcollege', methods=['GET', 'POST'])
@csrf.exempt
def add_college():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))

    if request.method == 'POST':
        collegecode = request.form['collegecode']
        collegename = request.form['collegename']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO college (collegecode, collegename) VALUES (%s, %s)", (collegecode, collegename))
        mysql.connection.commit()
        flash("College added successfully!", "success")
        return redirect(url_for('controller.collegehome'))
    
    return render_template('add_college.html')



@controller.route('/editcollege/<string:collegecode>', methods=['GET', 'POST'])
@csrf.exempt
def edit_college(collegecode):
    with mysql.connection.cursor() as cur:
        if request.method == 'POST':
            # Get form data for college
            college_code = request.form.get('college_code')
            college_name = request.form.get('college_name')

    
            cur.execute("""
                UPDATE college
                SET collegecode = %s, collegename = %s
                WHERE collegecode = %s
            """, (college_code, college_name, collegecode))

            mysql.connection.commit()
            flash("College updated successfully!", "success")
            return redirect(url_for('controller.collegehome'))
        
        else:

            cur.execute("SELECT * FROM college WHERE collegecode = %s", (collegecode,))
            college = cur.fetchone()

            if not college:
                flash("College not found!", "danger")
                return redirect(url_for('controller.collegehome')) 

            return render_template('edit_college.html', college=college) 



@controller.route('/deletecollege/<string:college_id>', methods=['POST'])
@csrf.exempt
def delete_college(college_id):
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM college WHERE collegecode = %s", (college_id,))
    mysql.connection.commit()
    flash("College deleted successfully!", "success")
    return redirect(url_for('controller.collegehome'))

@controller.route('/coursehome')
@csrf.exempt
def coursehome():
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    
    # Fetch all courses and colleges
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT 
            course.coursecode, 
            course.coursename, 
            course.collegebelong, 
            college.collegecode, 
            college.collegename 
        FROM 
            course 
        JOIN 
            college 
        ON 
            course.collegebelong = college.collegecode
    """)
    courses = cur.fetchall()
    
    return render_template('course.html', courses=courses)


@controller.route('/addcourse', methods=['GET', 'POST'])
@csrf.exempt
def add_course():
    with mysql.connection.cursor() as cur:
        if request.method == 'POST':
            course_code = request.form['coursecode']
            course_name = request.form['coursename']
            college_belong = request.form['college']
            
          
            cur.execute("""
                INSERT INTO course (coursecode, coursename, collegebelong)
                VALUES (%s, %s, %s)
            """, (course_code, course_name, college_belong))
            mysql.connection.commit()
            flash("Course added successfully!", "success")
            return redirect(url_for('controller.coursehome'))

        else:
        
            cur.execute("SELECT collegecode, collegename FROM college")
            colleges = cur.fetchall()  
            return render_template('add_course.html', colleges=colleges)



@controller.route('/editcourse/<string:coursecode>', methods=['GET', 'POST'])
@csrf.exempt
def edit_course(coursecode):
    with mysql.connection.cursor() as cur:
        if request.method == 'POST':
            course_code = request.form.get('course_code')
            course_name = request.form.get('course_name')

            cur.execute("""
                UPDATE course
                SET coursecode = %s, coursename = %s
                WHERE coursecode = %s
            """, (course_code, course_name, coursecode)) 

            mysql.connection.commit()
            flash("Course updated successfully!", "success")
            return redirect(url_for('controller.coursehome'))
        
        else:
            cur.execute("SELECT * FROM course WHERE coursecode = %s", (coursecode,))
            course = cur.fetchone() 

            if not course:
                flash("Course not found!", "danger")
                return redirect(url_for('controller.coursehome'))

            return render_template('edit_course.html', course=course)  

    
@controller.route('/deletecourse/<string:coursecode>', methods=['POST'])
@csrf.exempt
def delete_course(coursecode):
    if 'user_id' not in session:
        flash("You must log in first!", "danger")
        return redirect(url_for('controller.login'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM course WHERE coursecode = %s", (coursecode,))
    mysql.connection.commit()
    flash("Course deleted successfully!", "success")
    return redirect(url_for('controller.coursehome'))

@controller.route('/search', methods=['GET'])
@csrf.exempt
def search():
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int) 
    per_page = 10 
    offset = (page - 1) * per_page  

    results = []
    total_results = 0

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


        cur.execute("""
            SELECT COUNT(*) AS total FROM students
            WHERE id_number = %s
            OR fname LIKE %s
            OR lname LIKE %s
            OR course LIKE %s
            OR gender = %s
            OR yearlevel = %s
        """, (query, f"%{query}%", f"%{query}%", f"%{query}%", query, query))
        
        total_results = cur.fetchone()["total"]
        cur.execute("""
            SELECT id_number, fname, lname, course, yearlevel, gender, profile
            FROM students
            WHERE id_number = %s
            OR fname LIKE %s
            OR lname LIKE %s
            OR course LIKE %s
            OR gender = %s
            OR yearlevel = %s
            LIMIT %s OFFSET %s
        """, (query, f"%{query}%", f"%{query}%", f"%{query}%", query, query, per_page, offset))

        results = cur.fetchall()
        cur.close()
    except Exception as e:
        print("Database Error:", e)
        flash("An error occurred while searching. Please try again.", "danger")

    total_pages = (total_results + per_page - 1) // per_page 

    return render_template('search.html', results=results, query=query, page=page, total_pages=total_pages)
