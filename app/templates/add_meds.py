# TODO: WHAT IS THIS DOING HERE?
from app import db, Medications

med1 = Medications(
    name="Cyclobenzaprine", description="Tablet", dosage="5mg", price=8.70
)
med2 = Medications(
    name="Cyclobenzaprine", description="Tablet", dosage="7.5mg", price=15.00
)

db.session.add(med1)
db.session.add(med2)
db.session.commit()
