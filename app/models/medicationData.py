from app.extensions import db


class MedicationData(db.Model):
    __tablename__ = "medicationData"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_name = db.Column(db.String(100), nullable=False)
    medical_condition = db.Column(db.String(100), nullable=False)
    medical_condition_description = db.Column(db.Text)
    activity = db.Column(db.String(100))
    rx_otc = db.Column(db.String(50))
    pregnancy_category = db.Column(db.String(50))
    csa = db.Column(db.String(50))
    alcohol = db.Column(db.String(50))
    rating = db.Column(db.Float)  # Rating should be a float
    no_of_reviews = db.Column(db.Integer)  # No. of reviews should be an integer
    medical_condition_url = db.Column(db.String(200))
    drug_link = db.Column(db.String(200))

    def __repr__(self):
        return f"<MedicationData {self.drug_name}>"
