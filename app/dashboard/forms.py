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
    """Form for adding/editing medication details."""

    dosage = StringField("Dosage", validators=[DataRequired()])
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
        default="mg",  # Set a default unit
    )
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
        option_widget=CheckboxInput(),  # This ensures checkboxes are rendered
    )
    price = DecimalField("Price", validators=[DataRequired()])
    duration = IntegerField("Duration", validators=[DataRequired()])
    submit = SubmitField("Add Medication", validators=[DataRequired()])
