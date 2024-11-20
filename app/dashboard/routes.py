"""
Routes for managing the dashboard of the application.

This module contains various Flask routes that provide functionality for
logged-in users to manage their medications. It includes features for
viewing, adding, updating, and deleting medications, as well as searching
for medications and managing user settings.

Key Functions:
- dashboard: Renders the user's dashboard with a summary of their medications.
- search_medication: Searches for medications based on the user's query.
- add_medication: Allows users to add a new medication or edit an existing one.
- update_medication_status: Toggles the status of a medication between 'taken' 
    and 'not taken'.
- delete_medication: Deletes a specified medication for the logged-in user.
- schedule: Renders the schedule page.
- forum: Renders the forum page.
- settings: Handles user settings management, including updating profile
    information and changing passwords.
- change_password: Processes password change requests.

Each route is protected by the `login_required` decorator, ensuring that
only authenticated users can access these functionalities.

Module Dependencies:
- Flask: Web framework for building the application.
- Flask-Login: Extension for managing user sessions.
- SQLAlchemy: ORM for interacting with the database.
- datetime: Standard library for date and time manipulation.
"""

from datetime import datetime, timedelta, date
from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import (
    current_user,
    login_required,
)
from apscheduler.schedulers.background import BackgroundScheduler

from app.dashboard import dash
from app.extensions import db
from app.models.medication import Medications
from app.models.medicationData import MedicationData
from app.dashboard.forms import MedicationForm


@dash.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """
    Render the user's dashboard with a summary of their medications.

    This function retrieves all medications associated with the currently
    logged-in user, organizes them by day of the week and time of day, and
    renders the dashboard template.

    Returns:
        Rendered template for the dashboard with grouped medications and the
        current day.
    """
    # Current signed in users id
    user_id = current_user.id

    grouped_meds = get_grouped_meds(user_id=user_id)

    today = datetime.now().strftime("%A")

    current_date = datetime.now().strftime("%B %d, %Y")

    return render_template(
        "dashboard/dashboard.html",
        current_user=current_user,
        grouped_meds=grouped_meds,
        today=today,
        current_date=current_date,
    )


def reset():
    """Reset medication status to 'not taken' only for days not marked as 'taken'."""
    today = datetime.today().date()
    today_str = today.strftime("%Y-%m-%d")  # Format today's date as a string
    medications = Medications.query.all()

    for medication in medications:
        days_taken = medication.days_taken.split(",") if medication.days_taken else []

        # If today's date is not in `days_taken`, reset the status to 'not taken'
        if today_str not in days_taken:
            medication.status = "not taken"
        else:
            # If today is already marked as 'taken', keep the status as 'taken'
            medication.status = "taken"

        db.session.commit()



# Setup the scheduler to run at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(func=reset, trigger="cron", hour=0, minute=0)
scheduler.start()


def get_grouped_meds(user_id):
    """Helper function to group medications by day of the week and time of day."""
    medications = (
        db.session.query(Medications, MedicationData)
        .join(MedicationData)
        .filter(Medications.user_id == user_id)
        .all()
    )

    # Group medications by day of the week and time of day
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    grouped_meds = {
        day: {
            "Morning": [],
            "Afternoon": [],
            "Evening": [],
            "Night": [],
            "As Needed": [],
        }
        for day in days
    }

    for med, med_data in medications:
        days_of_week = med.days_of_week.split(",")
        for day in days_of_week:
            day_capitalized = day.strip().capitalize()

            if day_capitalized == "All":
                for day_key in grouped_meds.keys():
                    time_of_day_capitalized = (
                        med.time_of_day.capitalize() if med.time_of_day else "As Needed"
                    )
                    if time_of_day_capitalized not in grouped_meds[day_key]:
                        grouped_meds[day_key][time_of_day_capitalized] = []
                    grouped_meds[day_key][time_of_day_capitalized].append(
                        (med, med_data)
                    )
            else:
                time_of_day_capitalized = (
                    med.time_of_day.capitalize() if med.time_of_day else "As Needed"
                )
                if day_capitalized in grouped_meds:
                    if time_of_day_capitalized not in grouped_meds[day_capitalized]:
                        grouped_meds[day_capitalized][time_of_day_capitalized] = []
                    grouped_meds[day_capitalized][time_of_day_capitalized].append(
                        (med, med_data)
                    )

    return grouped_meds


@dash.route("/search_medication", methods=["GET"])
@login_required
def search_medication():
    """
    Search for medications based on the user's query.

    Function retrieves medication data that matches the user's search query
    and returns the results as a rendered partial template. If no query is
    provided, an empty result set is returned.

    Returns:
        Rendered template for the search results containing matching
        medications.
    """
    query = request.args.get("query")
    if query:
        search_results = MedicationData.query.filter(
            MedicationData.drug_name.ilike(f"%{query}%")
        ).all()
    else:
        search_results = []

    # Render a partial template to return only the search results
    return render_template("dashboard/search_results.html", medications=search_results)


def get_next_day_of_week(created_at, target_days):
    """Calculate the nearest future date for one of the target days of the week."""
    day_name_to_index = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    target_day_indexes = [day_name_to_index[day] for day in target_days]

    for i in range(7):
        next_date = created_at + timedelta(days=i)
        if next_date.weekday() in target_day_indexes:
            return next_date
    return created_at  # Default to created_at if no match is found


@dash.route("/add_medication", methods=["GET", "POST"])
@dash.route("/add_medication/<int:id>", methods=["GET", "POST"])
@login_required
def add_medication(id=None):
    """
    Add a new medication for the logged-in user.

    This function handles the addition of a medication either through a POST
    request with a submitted form or by pre-filling the form with existing
    medication data if an ID is provided in the URL. The medication is
    associated with the currently logged-in user.

    If the form is submitted and valid, the medication details are extracted,
    and the medication is added to the database. The function then redirects
    the user to the dashboard. If no medication is found with the provided
    ID, an error message is printed to the console.

    Parameters:
        id (int): The ID of the medication to edit (optional). If not provided,
        a new medication will be added.

    Returns:
        Rendered template for the add medication form or redirects to the
        dashboard after successful submission.
    """
    form = MedicationForm()
    if form.validate_on_submit():
        dosage = form.dosage.data
        unit = form.unit.data
        price = form.price.data
        duration = form.duration.data
        time_of_day = form.time_of_day.data
        days_of_week = form.days_of_week.data

        if len(days_of_week) == 7:
            days_of_week_str = "all"
        else:
            days_of_week_str = ", ".join(days_of_week) if days_of_week else "all"

        created_at = date.today()  # Use today's date as the creation date

        # Calculate the start date based on the selected days
        if days_of_week_str != "all":
            # Split and calculate the closest start date based on created_at and selected days
            target_days = [day.strip().capitalize() for day in days_of_week]
            start_listing_date = get_next_day_of_week(created_at, target_days)
        else:
            # If "all" days are selected, start from created_at
            start_listing_date = created_at

        if id is not None:
            medication = (
                db.session.query(MedicationData).filter(MedicationData.id == id).first()
            )
            if medication:
                new_medication = Medications(
                    user_id=current_user.id,
                    name=medication.drug_name,
                    description=medication.medical_condition_description,
                    dosage=f"{dosage} {unit}".strip(),
                    price=price,
                    duration=duration,
                    medication_data=id,
                    time_of_day=time_of_day,
                    days_of_week=days_of_week_str,
                    created_at=created_at,  # Record the creation date
                )

                db.session.add(new_medication)
                db.session.commit()

                print(f"Medication added: {new_medication}")
                return redirect(url_for("dash.dashboard"))
            else:
                print("No medication found with the given ID.")

    return render_template("dashboard/add_medications.html", form=form)


@dash.route("/medication/update_status/<int:med_id>", methods=["POST"])
@login_required
def update_medication_status(med_id):
    """
    Update the status of a medication for the logged-in user.

    This function toggles the status of a specified medication between 'taken'
    and 'not taken'. It retrieves the medication based on the provided
    medication ID and updates its status accordingly. The function commits the
    change to the database and redirects the user back to the dashboard.

    If the medication is marked as taken, the current date is appended to the
    days_taken list.
    """
    medication = Medications.query.get(med_id)

    if medication:
        current_date = (
            datetime.now().date().strftime("%m-%d-%Y")
        )  # Format the date as MM-DD-YYYY
        print(f"Before: {medication.days_taken}")  # Debugging output

        # If the status is 'taken', add the current date to days_taken
        if medication.status == "taken":
            medication.status = "not taken"
            # Remove the current date from days_taken if the status is being toggled off
            if current_date in medication.days_taken:
                # Remove the date from the comma-separated list
                medication.days_taken = ",".join(
                    [
                        date
                        for date in medication.days_taken.split(",")
                        if date != current_date
                    ]
                )
        else:
            medication.status = "taken"
            # Append the current date to days_taken if not already added
            if current_date not in medication.days_taken:
                if medication.days_taken:
                    # Append new date
                    # TODO: THIS MUST BE TESTED TOMORROW NOVEMBER 20!!!!
                    medication.days_taken += "," + current_date
                else:
                    # initialize first date
                    medication.days_taken = current_date

        # Commit the changes to the database
        db.session.commit()

        print(f"After: {medication.days_taken}")  # Debugging output
    else:
        print(f"Medication with id {med_id} not found!")

    return redirect(url_for("dash.dashboard"))


@dash.route("/delete_medication/<int:med_id>", methods=["POST"])
@login_required
def delete_medication(med_id):
    """
    Delete a specified medication for the logged-in user.

    This function retrieves a medication based on the provided medication ID
    and deletes it from the database. If the medication is found and deleted
    successfully, a success message is flashed. If no medication is found
    with the given ID, an error message is flashed instead. The user is then
    redirected back to the dashboard.

    Parameters:
        med_id (int): The ID of the medication to be deleted.

    Returns:
        Redirects the user to the dashboard after attempting to delete the
        medication.
    """

    medication = Medications.query.get(med_id)

    if medication:
        db.session.delete(medication)
        db.session.commit()
        flash("Medication deleted successfully!", "success")
    else:
        flash("Medication not found!", "error")

    return redirect(url_for("dash.dashboard"))


@dash.route("/schedule")
@login_required
def schedule():
    """Route to render the schedule page"""
    return render_template("dashboard/schedule.html")


@dash.route("/get_medications", methods=["GET"])
@login_required
def get_medications():
    user_id = current_user.id
    medications = Medications.query.filter_by(user_id=user_id).all()

    meds_data = []
    day_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    for med in medications:
        start_date = med.created_at
        duration = int(med.duration)

        # Parse days_of_week into numeric values
        if med.days_of_week != "all":
            target_days = [day_map[day.strip().lower()] for day in med.days_of_week.split(",")]
        else:
            target_days = list(range(7))  # All days of the week

        # Calculate the actual number of weeks needed to fit the duration
        days_per_week = len(target_days)
        if days_per_week == 0:
            days_per_week = 1  # Avoid division by zero if no days are set
        weeks_needed = (duration + days_per_week - 1) // days_per_week
        end_date = start_date + timedelta(weeks=weeks_needed)

        # Convert days_taken into ISO 8601 format
        days_taken = [
            datetime.strptime(day.strip(), "%m-%d-%Y").strftime("%Y-%m-%d")
            for day in med.days_taken.split(",") if day
        ]

        meds_data.append({
            "id": med.id,
            "name": med.name,
            "dosage": med.dosage,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "days": target_days,
            "duration": duration,
            "days_taken": days_taken,
        })

    return jsonify(meds_data)





@dash.route("/settings", methods=["GET", "POST"])
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
                return redirect(url_for("dash.dashboard"))

            # Check if new passwords match
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("dash.dashboard"))

            # Update password
            current_user.password = new_password
            db.session.commit()
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for("dash.dashboard"))

        # Otherwise, handle profile information update
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.email = request.form.get("email")

        # Save changes to the database
        db.session.commit()
        flash("Account details updated successfully.", "success")
        return redirect(url_for("dash.dashboard"))

    return render_template("dashboard/settings.html", current_user=current_user)


@dash.route("/change_password", methods=["POST"])
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

    grouped_meds = get_grouped_meds(current_user.id)

    # Verify current password
    if not current_user.verify_password(current_password):
        password_message = "Current password was incorrect."
        return render_template(
            "dashboard/dashboard.html",
            current_user=current_user,
            grouped_meds=grouped_meds,
            today=datetime.now().strftime("%A"),
            password_message=password_message,
        )

    # Check if new passwords match
    if new_password != confirm_new_password:
        password_message = "New passwords do not match."
        return render_template(
            "dashboard/dashboard.html",
            current_user=current_user,
            grouped_meds=grouped_meds,
            today=datetime.now().strftime("%A"),
            password_message=password_message,
        )

    # Update password
    current_user.password = new_password
    db.session.commit()
    password_message = "Password successfully changed!"
    return render_template(
        "dashboard/dashboard.html",
        current_user=current_user,
        grouped_meds=grouped_meds,
        today=datetime.now().strftime("%A"),
        password_message=password_message,
    )
