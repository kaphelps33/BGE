from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired


class MedicationForm(FlaskForm):
    """Form for adding/editing medication details."""

    name = StringField(
        "Medication Name", validators=[DataRequired()], render_kw={"readonly": True}
    )
    description = StringField(
        "Description", validators=[DataRequired()], render_kw={"readonly": True}
    )
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
    price = DecimalField("Price", validators=[DataRequired()])
    duration = IntegerField("Duration", validators=[DataRequired()])
    submit = SubmitField("Add Medication", validators=[DataRequired()])
