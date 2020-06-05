import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from .app import db
from .. import shared_enums


class Inpatient(db.Model):
    """Database table representing a live view of inpatients at NDDH from TrakCare."""

    __tablename__ = "vwPathologyCurrentInpatients"

    reg_number = db.Column("RegNumber", db.Text(), primary_key=True)
    nhs_number = db.Column("NHSNumber", db.Text())
    forename = db.Column("Forename", db.Text())
    surname = db.Column("Surname", db.Text())
    admission_date = db.Column("AdmissionDate", db.Date)
    dob = db.Column("DateOfBirth", db.Date)
    ward = db.Column("Ward", db.Text())
    room = db.Column("Room", db.Text())
    consultant = db.Column(
        "Consultant",
        db.Enum(
            shared_enums.Consultant, values_callable=lambda enum: [name.value for name in enum]
        ),
    )

    @hybrid_property
    def length_of_stay(self) -> int:
        """Return the integer number of days since admission."""
        return (datetime.date.today() - self.admission_date).days
