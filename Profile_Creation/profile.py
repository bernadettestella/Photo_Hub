#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'photohub'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Execute the MySQL query to fetch all profiles
    cur.execute("SELECT * FROM photohub.photographers_profiles")

    # Fetch all profiles
    profiles = cur.fetchall()

    # Close the cursor
    cur.close()

    return render_template('index.html', profiles=profiles)


@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        phone_number = str(request.form['phone_number'])
        location = request.form['location']

        # Validate input
        if not first_name or not last_name or not username or not email or not phone_number or not location:
            return "All fields must be filled out."

        # Execute the MySQL query to insert the new profile
        cur.execute("INSERT INTO photohub.photographers_profiles (first_name, last_name, user_name, email, phone_number, location) VALUES (%s, %s, %s, %s, %s, %s)", (first_name, last_name, username, email, phone_number, location))

        # Commit changes to the database
        mysql.connection.commit()

        # Close the cursor
        cur.close()

        return redirect(url_for('index'))

    return render_template('profile.html')



if __name__ == '__main__':
    app.run(debug=True)
