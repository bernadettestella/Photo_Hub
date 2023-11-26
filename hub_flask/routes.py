#!/usr/bin/python3
"""
starts a Flask web application
"""

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://your_username:your_password@your_host/your_database_name'
db = SQLAlchemy(app)

# Define a Photographer class to represent the photographers table
class Photographer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date())
    location = db.Column(db.String(100))
    preferred_username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    

"""defining routes to various pages of the hub website"""
# Route to handle landing page
@app.route('/', strict_slashes=False)
def landing_page():
    return render_template('landing.html')

# Route to handle client welcome message
@app.route('/client', strict_slashes=False)
def client_login():
    return render_template('client-welcome.html')

# Route to browse through photographs uploaded 
@app.route('/browse_photographers', strict_slashes=False)
def photographs_posts():
    return render_template('the page jude is using')

# Route to handle a new photographer sign up
@app.route('/photographers_signin', strict_slashes=False)
def photographer_signup():
    return render_template('sign_in.html')

# Route to handle successful sign up and render login page
@app.route('/signup_login', strict_slashes=False)
def new_login():
	return render_template('login.hmtl')

# Route to handle existing photographer login
@app.route('/photographer_login', strict_slashes=False)
def photographer_login():
    return render_template('login.html')
