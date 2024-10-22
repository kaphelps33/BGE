from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


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
