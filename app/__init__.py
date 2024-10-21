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


# User model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)  # Add a default date
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # Fix the attribute name

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


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
        # Create a new user
        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,  # This will call the setter method to hash the password
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(
            url_for("login")
        )  # Redirect to login after successful registration
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    users = Users.query.all()  # Query all users from the database
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


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Running the app
if __name__ == "__main__":
    app.run(debug=True)
