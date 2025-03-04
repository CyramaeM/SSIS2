from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import webapp as webapp


app = Flask(__name__)
app.config['DEBUG'] =True

@app.route("/")
def home():
    return render_template('base.html')

@app.route("/index")
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password (for demonstration purposes; you should store it securely in a database)
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Add your code to store the email and hashed_password in the database here
        
        flash('Sign Up Successful!', 'success')
        return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)