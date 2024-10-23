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
- settings: Handles user settings management, including updating profile information and changing passwords.
- change_password: Processes password change requests.

Each route is protected by the `login_required` decorator, ensuring that
only authenticated users can access these functionalities.

Module Dependencies:
- Flask: Web framework for building the application.
- Flask-Login: Extension for managing user sessions.
- SQLAlchemy: ORM for interacting with the database.
- datetime: Standard library for date and time manipulation.
"""

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
)

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

    # Query all medications that exist with the current users id
    medications = (
        db.session.query(Medications, MedicationData)
        .join(MedicationData)
        .filter(Medications.user_id == user_id)
        .all()
    )

    # Group medications by day of the week and time of day
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Initialize a dictionary to group medications by day and time of day
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

    # Iterate through each medication and its associated data
    for med, med_data in medications:  # Unpack the tuple
        # Split the days of the week for each medication
        days_of_week = med.days_of_week.split(",")

        # Loop through each day in days_of_week
        for day in days_of_week:
            day_capitalized = day.strip().capitalize()

            # Handle "All" days by assigning to all specific days
            if day_capitalized == "All":
                for day_key in grouped_meds.keys():  # Loop through all days
                    # Ensure the time of day exists in the dictionary
                    time_of_day_capitalized = (
                        med.time_of_day.replace("_", " ").capitalize()
                        if med.time_of_day
                        else "As Needed"
                    )
                    if time_of_day_capitalized not in grouped_meds[day_key]:
                        grouped_meds[day_key][time_of_day_capitalized] = []
                    grouped_meds[day_key][time_of_day_capitalized].append(
                        (med, med_data)
                    )
            else:
                # If it's a specific day, handle it normally
                time_of_day_capitalized = (
                    med.time_of_day.capitalize() if med.time_of_day else "As Needed"
                )
                if day_capitalized in grouped_meds:
                    if time_of_day_capitalized not in grouped_meds[day_capitalized]:
                        grouped_meds[day_capitalized][time_of_day_capitalized] = []
                    grouped_meds[day_capitalized][time_of_day_capitalized].append(
                        (med, med_data)
                    )

    today = datetime.now().strftime("%A")

    return render_template(
        "dashboard/dashboard.html",
        current_user=current_user,
        grouped_meds=grouped_meds,
        today=today,
    )


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


@dash.route("/add_medication", methods=["GET", "POST"])
@dash.route("/add_medication/<int:id>", methods=["GET", "POST"])
@login_required
def add_medication(id):
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

    Parameters:
        med_id (int): The ID of the medication whose status is to be updated.

    Returns:
        Redirects the user to the dashboard after updating the medication
        status.
    """
    medication = Medications.query.get(med_id)

    if medication:
        # Toggle status
        medication.status = "not taken" if medication.status == "taken" else "taken"
        db.session.commit()

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
    return render_template("dashboard/schedule.html")


@dash.route("/forum")
@login_required
def forum():
    return render_template("dashboard/forum.html")


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
