"""For working with errors that might be thrown by the app"""

from flask import render_template
from app.main import main


@main.app_errorhandler(404)
def page_not_found(e):
    """Used for redirecting to a 404 error page"""
    return render_template("errors/404.html"), 404
