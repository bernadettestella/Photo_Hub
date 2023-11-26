#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, Response, session, send_file
from flask_mysqldb import MySQL
import io
import imghdr


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
    cursor.execute("SELECT id, image_data FROM photohub.images")
    images = cursor.fetchall()

    image_data_list = []
    content_type_list = []

    for image_id, image_data in images:
        image_type = imghdr.what(None, h=image_data)
        if image_type:
            content_type = f'image/{image_type}'
            content_type_list.append(content_type)
            image_data_list.append((image_id, content_type))
    return render_template('load_upload_images.html', images=image_data_list, content_types=content_type_list)



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
def get_images(image_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image_data FROM photohub.images WHERE id = %s", (image_id,))
    image_data = cursor.fetchone()

    if image_data:
        image_type = imghdr.what(None, h=image_data[0])
        if image_type:
            # content type based on image type
            content_type = f'image/{image_type}'
            return send_file(io.BytesIO(image_data[0]), mimetype=content_type)
        else:
            return 'Unknown image type'
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
