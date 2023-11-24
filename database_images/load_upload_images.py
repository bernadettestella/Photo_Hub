#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'photohub'

mysql = MySQL(app)

@app.route('/')
def idx():
    cursor = mysql.connection.cursor()
    cursor.execute("USE photohub")
    cursor.execute("SELECT id FROM photohub.images")
    imageid = [row[0] for row in cursor.fetchall()]
    return render_template('load_upload_images.html', imageid=imageid)



@app.route('/upload', methods=['POST'])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            file_data = file.read()

            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO photohub.images (image_data) VALUES (%s)", (file_data,))
            mysql.connection.commit()

        return redirect(url_for('idx'))



@app.route('/image/<int:image_id>')
def get_images(imageid):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image_data FROM photohub.images WHERE id = %s", (image_id,))
    image_data = cursor.fetchone()

    if image_data:
        return base64.b64encode(image_data[0]).decode('utf-8')
    else:
        return 'Image not found'


@app.route('/logout')
def logout():
    # Clear session data, but I havent yet added the flask secret key
    session.clear()
    # Redirect to the index page
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
