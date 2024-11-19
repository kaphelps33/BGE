from datetime import timedelta
from flask import render_template
from app.main import main


def get_next_day_of_week(created_at, target_days):
    """Calculate the nearest future date for one of the target days of the week.

    Args:
        created_at (date): The date the medication entry was created.
        target_days (list of str): Days of the week the medication is taken.

    Returns:
        date: The next date that matches one of the target days.
    """
    # Map day names to weekday numbers (0 = Monday, 6 = Sunday)
    day_name_to_index = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    # Convert target day names to a list of weekday indexes
    target_day_indexes = [day_name_to_index[day] for day in target_days]

    # Start from the created_at date and find the closest target day
    for i in range(7):
        next_date = created_at + timedelta(days=i)
        if next_date.weekday() in target_day_indexes:
            return next_date
    return created_at  # Default to created_at if no match is found


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
