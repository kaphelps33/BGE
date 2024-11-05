"""All of the forms required for dashboard functionality
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    DecimalField,
    IntegerField,
    SelectField,
    RadioField,
    SelectMultipleField,
)
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired


class MedicationForm(FlaskForm):
    """Form for adding medications to the users profile/dashboard."""

    # Medication dosage field
    dosage = StringField("Dosage", validators=[DataRequired()])
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
    # TODO: MAKE THIS REQUIRED WITH VALIDATORS
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
    price = DecimalField("Price", validators=[DataRequired()])
    # How long a user takes this medications
    # TODO: MAKE IT SO THIS MUST BE ABOVE 0 DAYS AND CAN'T BE SOME CRAZY VALUE
    # LIKE 1,000,000 DAYS
    duration = IntegerField("Duration", validators=[DataRequired()])
    # Submit button
    submit = SubmitField("Add Medication", validators=[DataRequired()])
