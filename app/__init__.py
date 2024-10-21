from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate here
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

# Set up Flask-Migrate
migrate = Migrate(app, db)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# User model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50), nullable=False, unique=True)
    account_type = db.Column(db.String(20), default="Patient")
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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Allow null for medications added globally
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # Add dosage
    price = db.Column(db.Float, nullable=False)  # Add price
    duration = db.Column(db.String(50))  # Example: '7 Days'
    user = db.relationship("Users", backref="medications", lazy=True)

    def __repr__(self):
        return f"<Medication {self.name}>"




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
                flash("Wrong password! Try again!", "danger")
        # If the user does not exist
        else:
            flash("That user does not exist!", "danger")
    return render_template("login.html", form=form, users=users)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    medications = Medications.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", current_user=current_user, medications=medications)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        # If current_password is provided, handle password change
        if "current_password" in request.form:
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_new_password = request.form.get("confirm_new_password")

            # Verify current password
            if not current_user.verify_password(current_password):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("dashboard"))

            # Check if new passwords match
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("dashboard"))

            # Update password
            current_user.password = new_password
            db.session.commit()
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for("dashboard"))

        # Otherwise, handle profile information update
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')

        # Save changes to the database
        db.session.commit()
        flash("Account details updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("settings.html", current_user=current_user)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")

    # Verify current password
    if not current_user.verify_password(current_password):
        password_message = "Current password was incorrect."
        return render_template("dashboard.html",
                               current_user=current_user,
                               medications=Medications.query.filter_by(user_id=current_user.id).all(),
                               password_message=password_message)

    # Check if new passwords match
    if new_password != confirm_new_password:
        password_message = "New passwords do not match."
        return render_template("dashboard.html",
                               current_user=current_user,
                               medications=Medications.query.filter_by(user_id=current_user.id).all(),
                               password_message=password_message)

    # Update password
    current_user.password = new_password
    db.session.commit()
    password_message = "Password successfully changed!"
    return render_template("dashboard.html",
                           current_user=current_user,
                           medications=Medications.query.filter_by(user_id=current_user.id).all(),
                           password_message=password_message)


@app.route('/search_medication', methods=['GET'])
@login_required
def search_medication():
    query = request.args.get('query')
    if query:
        # Assuming Medications is your model for medications
        search_results = Medications.query.filter(Medications.name.ilike(f'%{query}%')).all()
    else:
        search_results = []

    return render_template('dashboard.html', medications=search_results, current_user=current_user)


@app.route("/add_medication/<int:medication_id>", methods=["POST"])
@login_required
def add_medication(medication_id):
    # Find the medication in the database
    medication = Medications.query.get(medication_id)
    if not medication:
        flash("Medication not found.", "danger")
        return redirect(url_for("dashboard"))

    # Create a new entry in the Medications model linked to the user
    new_medication = Medications(
        user_id=current_user.id,
        name=medication.name,
        description=medication.description,
        dosage=medication.dosage,
        price=medication.price
    )
    db.session.add(new_medication)
    db.session.commit()

    flash(f"{medication.name} has been added to your dashboard.", "success")
    return redirect(url_for("dashboard"))



# Register form
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


# Login form
class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Running the app
if __name__ == "__main__":
    app.run(debug=True)
