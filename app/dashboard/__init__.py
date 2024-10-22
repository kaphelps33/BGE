"""Blueprint for dashboard
"""

from flask import Blueprint

dash = Blueprint("dash", __name__)

from app.dashboard import routes
