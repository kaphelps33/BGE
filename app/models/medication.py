from datetime import date

from app.extensions import db


class Medications(db.Model):
    """A class representing medications in the application.

    This model is used to store medication information in the database,
    such as the medication name, description, dosage, price, and duration.
    Medications can be added either globally or linked to a specific user.

    Args:
        db (SQLAlchemy): Database instance used for defining the model.

    Returns:
        Medications: An instance of the Medications class representing a
        medication entry.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Foreign key to link user to a medication
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=True
    )  # Allow null for medications added globally
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # Add dosage
    price = db.Column(db.Float, nullable=False)  # Add price
    duration = db.Column(db.String(50))  # Example: '7 Days'
    # medication can have one data piece
    medication_data = db.Column(
        db.Integer, db.ForeignKey("medicationData.id"), nullable=True
    )
    time_of_day = db.Column(
        db.String(50), nullable=False, default="as needed"
    )  # e.g., 'Morning', 'Evening', 'Night', 'As Needed'
    days_of_week = db.Column(
        db.String(50), nullable=False, default="all"
    )  # e.g., 'Monday, Wednesday, Friday'
    medication_info = db.relationship(
        "MedicationData", backref="medications", lazy=True
    )
    status = db.Column(db.String, nullable=False, default="pending")
    created_at = db.Column(db.Date, default=date.today, nullable=False)

    days_taken = db.Column(db.String, default="")

    def __repr__(self):
        """Returns a string representation of the medication instance.

        Returns:
            str: String representation of the medication, displaying the
            medication name.
        """
        return f"<Medication {self.name}>"
