"""Routes for authentication
"""

from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from app.extensions import db
from app.auth import auth
from app.models.user import Users
from app.auth.forms import RegisterForm, LoginForm


@auth.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("dash.dashboard"))
            # If the password is wrong
            else:
                flash("Wrong password! Try again!", "danger")
        # If the user does not exist
        else:
            flash("That user does not exist!", "danger")
    return render_template("auth/login.html", form=form, users=users)


@auth.route("/logout")
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
    return redirect(url_for("auth.login"))
