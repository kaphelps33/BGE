"""All routes dealing with the main page of the app, specifically just the
index"""

from flask import render_template
from app.main import main


@main.route("/")
def index():
    """Renders the home page of the application.

    This function handles requests to the root URL ("/") and returns
    the rendered HTML template for the index page.

    Returns:
        Response: The rendered HTML template for the index page.
    """
    return render_template("index.html")


@main.route("/about")
def about():
    """Renders the about page of the application

    Returns:
        Response: The rendered HTML template for the about page
    """
    return render_template("about.html")
