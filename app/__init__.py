"""Main application module"""

# TODO: UPDATE THIS FILE AND SPLIT INTO BLUEPRINTS
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate  # Import Migrate here
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

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
    """Load a user from the database by their user ID.

    This function is used by Flask-Login to retrieve a user object
    when a user is logged in. It queries the Users model using the
    provided user ID and returns the corresponding user instance.

    Args:
        user_id (int): The ID of the user to be loaded.

    Returns:
        Users or None: Returns the user object if found, or None if
        no user with the given ID exists.
    """
    return Users.query.get(int(user_id))


# User model
class Users(db.Model, UserMixin):
    """A class representing users in the application.

    This model is used to store user information in the database, such as
    username, name, email, account type, date of account creation, and
    password. The password is stored as a hashed value for security.

    Args:
        db (SQLAlchemy): Database instance used for defining the model.
        UserMixin (Flask-Login): Provides default implementations for user
        authentication.

    Raises:
        AttributeError: Raised when attempting to read the password attribute
        directly.

    Returns:
        Users: An instance of the Users class representing a user in the
        application.
    """

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
        """Prevents reading of the password attribute.

        Raises:
            AttributeError: Raised when trying to access the password directly.
        """
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        """Hashes and sets the password.

        Args:
            password (str): The plain-text password to be hashed and stored.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verifies the provided password against the stored hash.

        Args:
            password (str): The plain-text password to verify.

        Returns:
            bool: True if the password matches the stored hash, False
            otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Returns a string representation of the user instance.

        Returns:
            str: String representation of the user, displaying the username.
        """
        return f"<User {self.username}>"


# TODO: MIGHT NEED TO REPLACE THIS AND STORE IN A DIFFERENT WAY
# Medication model
class Medications(db.Model):
    """A class representing medications in the application.

    This model is used to store medication information in the database,
    such as the medication name, description, dosage, price, and duration.
    Medications can be added either globally or linked to a specific user.

    Args:
        db (SQLAlchemy): Database instance used for defining the model.

    Returns:
        Medications: An instance of the Medications class representing a
        medication entry.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Allow null for medications added globally
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # Add dosage
    price = db.Column(db.Float, nullable=False)  # Add price
    duration = db.Column(db.String(50))  # Example: '7 Days'
    user = db.relationship("Users", backref="medications", lazy=True)

    def __repr__(self):
        """Returns a string representation of the medication instance.

        Returns:
            str: String representation of the medication, displaying the
            medication name.
        """
        return f"<Medication {self.name}>"


@app.route("/")
def index():
    """Renders the home page of the application.

    This function handles requests to the root URL ("/") and returns
    the rendered HTML template for the index page.

    Returns:
        Response: The rendered HTML template for the index page.
    """
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration in the application.

    This function renders the registration form on a GET request and processes
    the form data on a POST request. It checks if the username or email already
    exists, and if not, creates a new user with the provided information.

    Args:
        None

    Raises:
        None

    Returns:
        Response:
            - On GET: Renders the registration form.
            - On POST: If the form is valid, either flashes an error message if
                the username or email already exists, or registers the new user
                and redirects to the login page with a success message.
    """
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
    """Handles user login in the application.

    This function renders the login form on a GET request and processes
    the form data on a POST request. It checks if the user exists and
    verifies the password. Upon successful login, the user is redirected
    to the dashboard.

    Returns:
        Response:
            - On GET: Renders the login form and displays a list of all
            registered users.
            - On POST: If the form is valid:
                - If the user exists and the password is correct, logs in the
                user and redirects to the dashboard.
                - If the password is incorrect, flashes an error message.
                - If the user does not exist, flashes an error message.
    """
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
    """Handles user logout in the application.

    This function logs out the currently authenticated user, flashes a logout
    confirmation message, and redirects the user to the login page.

    Returns:
        Response: Redirects the user to the login page after logging them out.
    """
    logout_user()
    flash("You have been logged out!", "success")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Renders the dashboard page for the logged-in user.

    This function fetches all medications associated with the currently logged-
    in user and displays them on the dashboard page. It ensures that only
    authenticated users can access the dashboard.

    Returns:
        Response: Renders the dashboard page with the current user and their
        medications.
    """
    medications = Medications.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", current_user=current_user, medications=medications
    )


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Handles user settings management.

    This function allows users to update their account settings, including
    changing their password and updating their profile information (first name,
    last name, and email). It verifies the current password before allowing
    a password change and provides feedback for successful or failed
    operations.

    Returns:
        Response:
            - On GET: Renders the settings page with the current user's
            information.
            - On POST: If the form is submitted, it checks for password
            changes or updates to profile information and redirects
            accordingly, flashing appropriate messages for success or errors.
    """
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
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.email = request.form.get("email")

        # Save changes to the database
        db.session.commit()
        flash("Account details updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("settings.html", current_user=current_user)


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    """Handles password change requests.

    This function processes a password change request by verifying the user's
    current password and ensuring that the new password and its confirmation
    match. It provides feedback through messages and renders the dashboard
    with appropriate alerts based on the outcome.

    Returns:
        Response: Renders the dashboard page with a message indicating success
        or failure of the password change operation.
    """
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")

    # Verify current password
    if not current_user.verify_password(current_password):
        password_message = "Current password was incorrect."
        return render_template(
            "dashboard.html",
            current_user=current_user,
            medications=Medications.query.filter_by(user_id=current_user.id).all(),
            password_message=password_message,
        )

    # Check if new passwords match
    if new_password != confirm_new_password:
        password_message = "New passwords do not match."
        return render_template(
            "dashboard.html",
            current_user=current_user,
            medications=Medications.query.filter_by(user_id=current_user.id).all(),
            password_message=password_message,
        )

    # Update password
    current_user.password = new_password
    db.session.commit()
    password_message = "Password successfully changed!"
    return render_template(
        "dashboard.html",
        current_user=current_user,
        medications=Medications.query.filter_by(user_id=current_user.id).all(),
        password_message=password_message,
    )


@app.route("/search_medication", methods=["GET"])
@login_required
def search_medication():
    query = request.args.get("query")
    if query:
        # Assuming Medications is your model for medications
        search_results = Medications.query.filter(
            Medications.name.ilike(f"%{query}%")
        ).all()
    else:
        search_results = []

    return render_template(
        "dashboard.html", medications=search_results, current_user=current_user
    )


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
        price=medication.price,
    )
    db.session.add(new_medication)
    db.session.commit()

    flash(f"{medication.name} has been added to your dashboard.", "success")
    return redirect(url_for("dashboard"))


class RegisterForm(FlaskForm):
    """A form for user registration.

    This form collects the user's desired username, email, and password
    (with confirmation). It includes validation to ensure the fields are
    filled out correctly, with constraints on length and password confirmation.

    Fields:
        username (StringField): The desired username (4-20 characters).
        email (StringField): The user's email address (up to 50 characters).
        password (PasswordField): The user's password, must match the
        confirmation. password_confirm (PasswordField): Field for confirming
        the password. submit (SubmitField): Button to submit the form.

    Raises:
        ValidationError: Raised if any field's validation fails (e.g.,
        username length, password mismatch).
    """

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
    """A form for user login.

    This form collects the username and password to authenticate the user.
    It includes validation to ensure the fields are filled out correctly.

    Fields:
        username (StringField): The user's username (4-20 characters).
        password (PasswordField): The user's password.
        submit (SubmitField): Button to submit the form.

    Raises:
        ValidationError: Raised if any field's validation fails (e.g., missing
        fields).
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# Running the app
if __name__ == "__main__":
    app.run(debug=True)
