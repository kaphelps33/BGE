"""All of the forms required for dashboard functionality
"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    DecimalField,
    IntegerField,
    SelectField,
    RadioField,
    SelectMultipleField,
)
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired, NumberRange


class MedicationForm(FlaskForm):
    """Form for adding medications to the users profile/dashboard."""

    # Medication dosage field
    dosage = DecimalField(
        "Dosage", validators=[DataRequired(), NumberRange(min=0, max=120)]
    )
    # Users can select different measurements of medication
    unit = SelectField(
        "Unit",
        choices=[
            ("mg", "mg"),
            ("mL", "mL"),
            ("g", "g"),
            ("L", "L"),
            ("units", "Units"),
        ],
        validators=[DataRequired()],
        default="mg",
    )
    # The time at which a user takes their medication
    time_of_day = RadioField(
        "Time of Day",
        choices=[
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
            ("night", "Night"),
            ("as_needed", "As Needed"),
        ],
        default="as_needed",
        validators=[DataRequired()],
    )
    # The days when a user takes their medications
    days_of_week = SelectMultipleField(
        "Days of the Week",
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )
    # Medication price
    price = DecimalField(
        "Price", validators=[DataRequired(), NumberRange(min=0, max=1000)]
    )
    # How long a user takes this medication
    duration = IntegerField(
        "Duration (Days)", validators=[DataRequired(), NumberRange(min=1, max=720)]
    )
    # Submit button
    submit = SubmitField("Add Medication")
