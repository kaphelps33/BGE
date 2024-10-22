"""Authentication related forms. Includes the form for registration and 
logging in.
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


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
