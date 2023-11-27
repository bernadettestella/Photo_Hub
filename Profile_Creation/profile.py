#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MYSQL

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Raelynn@2017'
app.config['MYSQL_DATABASE_DB'] = 'photo_hub'

mysql = MYSQL(app)

@app.route('/')
def index():
    return render_template('index.html', profiles=profiles)

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']

        # Create a new profile dictionary
        new_profile = {
            'name': name,
            'age': age,
            'email': email
        }

        # Add the new profile to the list
        profiles.append(new_profile)

        return redirect(url_for('index'))

    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)

