#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
        LoginManager,
        UserMixin,
        login_user,
        login_required,
        logout_user,
        current_user,
        )
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
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
    preferred_username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
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


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route("/photographer_login", methods=["GET", "POST"])
def photographer_login():
    if current_user.is_authenticated:
        # Redirect the user to the dashboard if they are already authenticated
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(preferred_username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for("dashboard"))
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template("login.html", form=form)


class SignupForm(FlaskForm):
    preferred_username = StringField('Preferred Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


@app.route("/photographers_signup", methods=["GET", "POST"])
def photographers_signup():
    form = SignupForm()

    if form.validate_on_submit():
        preferred_username = form.preferred_username.data
        email = form.email.data
        password = form.password.data

        # Validate username uniqueness
        existing_user = User.query.filter_by(preferred_username=preferred_username).first()
        if existing_user:
            flash("Username is already taken. Please choose another one.", "error")
            return redirect(url_for("photographers_signup"))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        new_user = User(preferred_username=preferred_username, email=email, password=hashed_password)
        db.session.add(new_user)

        try:
            # Attempt to commit changes to the database
            db.session.commit()
            login_user(new_user)
            flash("Your account has been created!", "success")
            return redirect(url_for("dashboard"))
        except IntegrityError as e:
            # Handle the case where a duplicate username or email was inserted
            db.session.rollback()
            if 'unique constraint' in str(e).lower():
                flash("Username or email is already taken. Please choose another one.", "error")
            else:
                flash("An unexpected error occurred. Please try again.", "error")

    return render_template("signup.html", form=form)


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


@app.route("/client_welcome")
def client_welcome():
    return render_template("client_welcome.html")


@app.route("/photographer_signup_login")
def photographer_signup_login():
    return render_template("photographer_signup_login.html")


@app.route("/choose_category")
def choose_category():
    # Fetch categories
    categories = Category.query.all()

    return render_template("choose_category.html", categories=categories)


@app.route("/browse_category_images/<int:category>")
def browse_category_images(category):
    photographers = User.query.filter(User.images.any(category_id=category)).all()
    for photographer in photographers:
        photographer.category_images = {}
        for image_data in photographer.images:
            if image_data.category_id == category:
                if category not in photographer.category_images:
                    photographer.category_images[category] = []
                photographer.category_images[category].append(image_data)

    return render_template("browse_category_images.html", category=category, photographers=photographers)


@app.route("/photographer_profile/<int:photographer_id>")
def photographer_profile(photographer_id):
    photographer = User.query.get(photographer_id)
    category_images = {}

    # Fetch images for each category
    categories = Category.query.all()
    for category in categories:
        category_images[category.id] = {
                "category_name": category.name,
                "images": Image.query.filter_by(user_id=photographer.id, category_id=category.id).all(),
                }

    return render_template("photographer_profile.html", photographer=photographer, category_images=category_images)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
