#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
        LoginManager,
        UserMixin,
        login_user,
        login_required,
        logout_user,
        current_user,
        )
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os
import io
import imghdr
from datetime import datetime


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/photohub"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED_IMAGES_DEST"] = "uploads/images"
images = UploadSet("images", IMAGES)
configure_uploads(app, images)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    location = db.Column(db.String(100))
    preferred_username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    images = db.relationship("Image", backref="user", lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    images = db.relationship("Image", backref="category", lazy=True)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.LargeBinary(length=(2**32)-1))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/photographer_login", methods=["GET", "POST"])
def photographer_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(preferred_username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/photographers_signup", methods=["GET", "POST"])
def photographers_signup():
    if request.method == "POST":
        # Extract form data
        first_name = request.form["first_name"]
        surname = request.form["surname"]
        middle_name = request.form["middle_name"]
        gender = request.form["gender"]
        dob_str = request.form["dob"]
        # parsing dob
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        location = request.form["location"]
        preferred_username = request.form["preferred_username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Validate password match
        if password != confirm_password:
            return render_template(
                    "photographers_signup.html", error="Passwords do not match"
                    )
        # Validate username uniqueness
        existing_user = User.query.filter_by(
                preferred_username=preferred_username
                ).first()
        if existing_user:
            return render_template(
                    "signup.html",
                    error="Username is already taken. Please choose another one.",
                    )

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        new_user = User(
                first_name=first_name,
                surname=surname,
                middle_name=middle_name,
                gender=gender,
                dob=dob,
                location=location,
                preferred_username=preferred_username,
                password=hashed_password,
                )
        db.session.add(new_user)
        try:
            # Attempt to commit changes to the database
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("dashboard"))
        except IntegrityError:
            # Handle the case where a duplicate username was inserted
            db.session.rollback()
            return render_template(
                    "signup.html",
                    error="Username is already taken. Please choose another one.",
                    )
        db.session.commit()

        login_user(new_user)

    return render_template("signup.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_images = db.session.get(User, current_user.id).images
    categories = Category.query.all()
    category_images = {}
    for category in categories:
        category_images[category.id] = {
                "category_name": category.name,
                "images": Image.query.filter_by(category_id=category.id, user_id=current_user.id).all(),
                }

    return render_template(
            "dashboard.html",
            user_images=user_images,
            categories=categories,
            category_images=category_images,
            )


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" in request.files and "category" in request.form:
        file = request.files["file"]
        category_id = request.form["category"]

        if file.filename != "":
            file_data = file.read()

            new_image = Image(
                    image_data=file_data, user_id=current_user.id, category_id=category_id
                    )
            db.session.add(new_image)
            db.session.commit()

    return redirect(url_for("dashboard"))


@app.route("/image/<int:image_id>")
def get_image(image_id):
    image = db.session.get(Image,image_id)

    if image:
        image_type = imghdr.what(None, h=image.image_data)
        if image_type:
            content_type = f"image/{image_type}"
            return send_file(io.BytesIO(image.image_data), mimetype=content_type)
        else:
            return "Unknown image type"
    else:
        return "Image not found"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
