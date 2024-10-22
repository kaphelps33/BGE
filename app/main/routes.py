from app.main import main

from flask import render_template


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
