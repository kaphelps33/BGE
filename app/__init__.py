from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# User model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Medication model
class Medications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(50))  # Example: '7 Days'
    user = db.relationship('Users', backref='medications', lazy=True)

    def __repr__(self):
        return f"<Medication {self.name}>"

# Create the database tables
with app.app_context():

    db.create_all()  # This will create the database tables

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    Users.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = Users.query.filter(
            (Users.username == form.username.data) | (Users.email == form.email.data)
        ).first()

        if existing_user:
            flash("Username or email already exists.", "danger")
        else:
            # Create a new user
            new_user = Users(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,  # Password will be hashed
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    users = Users.query.all()  # Display all registered users on the login page
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash(f"Logged in as {form.username.data}!", "success")
                # Direct user to dashboard
                return redirect(url_for("dashboard"))
            # If the password is wrong
            else:
                flash("Wrong password! Try again!")
        # If the user does not exist
        else:
            flash("That user does not exist!")
    return render_template("login.html", form=form, users=users)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Length(max=50)])
    password = PasswordField(
        "Password", validators=[DataRequired(), EqualTo("password_confirm")]
    )
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# Sample form for logging in
class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Running the app
if __name__ == "__main__":
    app.run(debug=True)
