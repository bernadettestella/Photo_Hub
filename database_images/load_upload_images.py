#!/usr/bin/python3
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response,
    session,
    send_file,
)
from flask_mysqldb import MySQL
import io
import imghdr


app = Flask(__name__)

app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "photohub"

mysql = MySQL(app)


@app.route("/")
def idx():
    cursor = mysql.connection.cursor()
    cursor.execute("USE photohub")
    # left join returns all the rows in the images table that match the condition
    cursor.execute(
        "SELECT c.category_id, c.category_name,i.id, i.image_data from categories c LEFT JOIN images i ON c.category_id = i.category_id"
    )
    data = cursor.fetchall()

    category_images = {}
    for category_id, category_name, image_id, image_data in data:
        if category_id not in category_images:
            # appends all the images in a specific category to a list whose key name is the category name
            category_images[category_id] = {
                "category_name": category_name,
                "images": [],
            }
        if image_id:
            image_type = imghdr.what(None, h=image_data)
            if image_type:
                content_type = f"image/{image_type}"
                category_images[category_id]["images"].append((image_id, content_type))
    return render_template("load_upload_images.html", category_images=category_images)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" in request.files and "category" in request.form:
        file = request.files["file"]
        category_id = request.form["category"]
        if file.filename != "":
            file_data = file.read()

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO photohub.images (image_data, category_id) VALUES (%s, %s)",
                (file_data, category_id),
            )
            mysql.connection.commit()

        return redirect(url_for("idx"))


@app.route("/image/<int:image_id>")
def get_images(image_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT image_data FROM photohub.images WHERE id = %s", (image_id,))
    image_data = cursor.fetchone()

    if image_data:
        image_type = imghdr.what(None, h=image_data[0])
        if image_type:
            # content type based on image type
            content_type = f"image/{image_type}"
            return send_file(io.BytesIO(image_data[0]), mimetype=content_type)
        else:
            return "Unknown image type"
    else:
        return "Image not found"


@app.route("/logout")
def logout():
    # Clear session data, but I havent yet added the flask secret key
    session.clear()
    # Redirect to the index page
    return redirect(url_for("idx"))


if __name__ == "__main__":
    app.run(debug=True)
