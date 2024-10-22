"""Routes for dashboard
"""

from flask import flash, redirect, render_template, request, url_for, jsonify
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
    """Renders the dashboard page for the logged-in user.

    This function fetches all medications associated with the currently logged-
    in user and displays them on the dashboard page. It ensures that only
    authenticated users can access the dashboard.

    Returns:
        Response: Renders the dashboard page with the current user and their
        medications.
    """

    medications = Medications.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard.html", current_user=current_user, medications=medications
    )


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
                return redirect(url_for("dashboard"))

            # Check if new passwords match
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("dashboard"))

            # Update password
            current_user.password = new_password
            db.session.commit()
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for("dashboard"))

        # Otherwise, handle profile information update
        current_user.first_name = request.form.get("first_name")
        current_user.last_name = request.form.get("last_name")
        current_user.email = request.form.get("email")

        # Save changes to the database
        db.session.commit()
        flash("Account details updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("settings.html", current_user=current_user)


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


@dash.route("/search_medication", methods=["GET"])
@login_required
def search_medication():
    query = request.args.get("query")
    if query:
        search_results = MedicationData.query.filter(
            MedicationData.drug_name.ilike(f"%{query}%")
        ).all()
    else:
        search_results = []

    # Render a partial template to return only the search results
    return render_template("search_results.html", medications=search_results)


@dash.route("/add_medication", methods=["GET", "POST"])
@dash.route("/add_medication/<int:id>", methods=["GET", "POST"])
@login_required
def add_medication(id):
    form = MedicationForm()
    if form.validate_on_submit():
        dosage = form.dosage.data
        unit = form.unit.data
        price = form.price.data
        duration = form.duration.data

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
                    medication_data=medication.id,
                )

                db.session.add(new_medication)
                db.session.commit()

                print(f"Medication added: {new_medication}")
                return redirect(url_for("dash.dashboard"))
            else:
                print("No medication found with the given ID.")

    return render_template("add_medications.html", form=form)


@dash.route("/delete_medication/<int:id>", methods=["POST"])
def delete_medication(id):
    medication = Medications.query.get_or_404(id)

    # Ensure that the medication belongs to the current user
    if medication.user_id != current_user.id:
        return redirect(url_for("dash.dashboard"))

    db.session.delete(medication)
    db.session.commit()

    return redirect(url_for("dash.dashboard"))
