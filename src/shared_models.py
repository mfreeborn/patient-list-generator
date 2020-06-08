import datetime
import re

from sqlalchemy.ext.hybrid import hybrid_property

from . import utils
from .front_end.app import db
from .shared_enums import Consultant
from .shared_enums import Team as TeamEnum
from .shared_enums import TeamName, Ward


class Patient(db.Model):
    """Database table representing a live view of inpatients at NDDH from TrakCare."""

    __tablename__ = "vwPathologyCurrentInpatients"
    nhs_num_pattern = re.compile(r"((?<=\s|\))|^)(\d{3}[ \t]*\d{3}[ \t]*\d{4})(\s+|)", flags=re.M)

    reg_number = db.Column("RegNumber", db.Text(), primary_key=True)
    _nhs_number = db.Column("NHSNumber", utils.NHSNumber())
    forename = db.Column("Forename", db.Text())
    surname = db.Column("Surname", db.Text())
    admission_date = db.Column("AdmissionDate", db.Date)
    dob = db.Column("DateOfBirth", db.Date)
    ward = db.Column(
        "Ward", db.Enum(Ward, values_callable=lambda enum: [name.value for name in enum]),
    )
    room = db.Column("Room", db.Text())
    _bed = db.Column("Bed", db.Text())
    _reason_for_admission = db.Column("ReasonForAdmission", db.Text())
    consultant = db.Column(
        "Consultant",
        db.Enum(Consultant, values_callable=lambda enum: [name.value for name in enum]),
    )

    location = None

    def __init__(
        self,
        nhs_number=None,
        reason_for_admission=None,
        jobs=None,
        edd=None,
        ds=None,
        tta=None,
        bloods=None,
    ):
        # __init__ is /not/ called when SQLAlchemy loads an row from the database. This
        # method is just for when we create Patient objects in from_table_row
        nhs_number = nhs_number or ""
        self.nhs_number = "".join(nhs_number.split())
        self.reason_for_admission = reason_for_admission or ""
        self.jobs = jobs or ""
        self.edd = edd or ""
        self.ds = ds or ""
        self.tta = tta or ""
        self.bloods = bloods or ""

    @property
    def bed(self):
        if self.location:
            return self.location.bed

    @bed.setter
    def bed(self, value):
        self._bed = value

    @property
    def nhs_number(self):
        if self._nhs_number:
            value = "".join(self._nhs_number.split())
            return f"{value[:3]} {value[3:6]} {value[6:]}"
        return

    @nhs_number.setter
    def nhs_number(self, value):
        self._nhs_number = "".join(value.split())

    @hybrid_property
    def age(self) -> int:
        if self.dob is None:
            return

        today = datetime.date.today()
        return (
            today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @hybrid_property
    def length_of_stay(self) -> int:
        """Return the integer number of days since admission."""
        return (datetime.date.today() - self.admission_date).days

    @hybrid_property
    def list_name(self):
        if self.surname and self.forename:
            return f"{self.surname.upper()}, {self.forename.title()}"
        elif self.surname and not self.forename:
            return f"{self.surname.upper()}, Unknown"
        elif not self.surname and self.forename:
            return f"UNKNOWN, {self.forename.title()}"
        return "UNKNOWN, Unknown"

    @hybrid_property
    def location(self):
        location_attrs = [self.ward, self.room, self._bed]
        if all(location_attrs):
            return Location(self.ward, self.room, self._bed)

    @hybrid_property
    def patient_details(self) -> str:
        """Return the patient detail's in the correct format for the patient list."""
        if not all([self.surname, self.forename, self.dob, self.nhs_number]):
            return "UNKNOWN"

        return f"{self.list_name}\n" f"{self.dob:%d/%m/%Y} ({self.age} Yrs)\n" f"{self.nhs_number}"

    @hybrid_property
    def reason_for_admission(self):
        if self._reason_for_admission:
            return " ".join(self._reason_for_admission.split())
        return self._reason_for_admission

    @reason_for_admission.setter
    def reason_for_admission(self, value):
        self._reason_for_admission = value

    @hybrid_property
    def team(self):
        for team in TeamEnum:
            if self.consultant in team.consultants:
                return team.name.value
        else:
            # this should be unreachable
            pass

    @team.expression
    def team(cls):
        return db.case(
            [
                (
                    cls.consultant.in_(TeamEnum.from_team_name(TeamName.ARBAB.value).consultants),
                    TeamName.ARBAB.value,
                ),
                (
                    cls.consultant.in_(TeamEnum.from_team_name(TeamName.ARYA.value).consultants),
                    TeamName.ARYA.value,
                ),
                (
                    cls.consultant.in_(
                        TeamEnum.from_team_name(TeamName.CARDIOLOGY.value).consultants
                    ),
                    TeamName.CARDIOLOGY.value,
                ),
                (
                    cls.consultant.in_(TeamEnum.from_team_name(TeamName.GASTRO.value).consultants),
                    TeamName.GASTRO.value,
                ),
                (
                    cls.consultant.in_(TeamEnum.from_team_name(TeamName.MARK.value).consultants),
                    TeamName.MARK.value,
                ),
                (
                    cls.consultant.in_(
                        TeamEnum.from_team_name(TeamName.RESPIRATORY.value).consultants
                    ),
                    TeamName.RESPIRATORY.value,
                ),
                (
                    cls.consultant.in_(TeamEnum.from_team_name(TeamName.STROKE.value).consultants),
                    TeamName.STROKE.value,
                ),
            ]
        )

    @classmethod
    def from_table_row(cls, row):
        """Return a Patient object from the information held in a table row.

        Expects the row to be in the following format:

            Bed | Patient Details | Issues | Jobs | EDD | DS | TTA | Blds

        The "Patient Details" cell needs to be something like the following format:

            SMITH, John
            01/01/1975 (45 Yrs)
            123 456 7890

        The only identifier that we try and parse from the table is the NHS
        number. The goal is to have as small a requirement of a "correctly"
        formatted list as possible in order to minimise parsing errors when
        trying to extract a patient from the Word list.
        """

        patient_details = row.cells[1].text.strip()
        nhs_number = cls.nhs_num_pattern.search(patient_details)

        if nhs_number is None:
            # no match found by the regex
            raise ValueError(
                f"No NHS number found in the table "
                f"cell with the following contents: {patient_details}"
            )
        else:
            # retrieves the NHS number from the successful regex match
            nhs_number = nhs_number[0]

        issues = row.cells[2].text.strip()
        jobs = row.cells[3].text.strip()
        edd = row.cells[4].text.strip()
        ds = row.cells[5].text.strip()
        tta = row.cells[6].text.strip()
        bloods = row.cells[7].text.strip()

        return cls(
            nhs_number=nhs_number,
            reason_for_admission=issues,
            jobs=jobs,
            edd=edd,
            ds=ds,
            tta=tta,
            bloods=bloods,
        )

    def merge(self, other_patient) -> None:
        """Merge 'other_patient''s details into self in place.

        This method operates on two instances of the /same/ patient:
            1) 'self': Patient populated from TrakCare with up to date location but no jobs, edd etc
            2) 'other_patient': Patient populated from the handover list with up to date jobs,
                edd etc but missing/outdated patient identifiers

        ...and merges the two together.

        The result should be a fully populated Patient with an up to date location from TrakCare
        as well as up to date information about jobs, edd etc."""
        # the two Patients must represent the same underlying person
        if self != other_patient:
            raise ValueError

        attrs_to_merge = ["reason_for_admission", "jobs", "edd", "ds", "tta", "bloods"]

        for attr in attrs_to_merge:
            other_pt_attr = getattr(other_patient, attr)
            setattr(self, attr, other_pt_attr)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.nhs_number == other.nhs_number

    def __repr__(self):
        cls_name = self.__class__.__name__
        pt = f"<{cls_name}(name={self.surname}, age={self.age}, nhs_number={self.nhs_number})>"
        return pt
        if self.location is None:
            return pt
        return (
            f"<{cls_name}(name={self.surname}, age={self.age}, nhs_number={self.nhs_number}, "
            f"location=Location(ward={self.location.ward.value}, bed={self.location.bed}))>"
        )


class Location:
    number_pattern = re.compile(r"\d{1,2}")

    def __init__(self, ward, room: str, bed: str):
        self.ward = ward
        self.room = room
        self.bed = self._parse_bed(room, bed)

    def _parse_bed(self, room: str, bed: str) -> str:
        """Take the room/bed as given by TrakCare and convert it to a user-friendly format."""
        # sort out the side rooms first
        room = room.lower()
        if "room" in room:
            # it is a side room
            if self.ward == Ward.FORTESCUE:
                # Fortescue uses colours rather than numbers
                room_colour = room.split()[0]
                return f"SR {room_colour.title()}"
            room_number = int(self.number_pattern.search(room)[0])
            return f"SR{room_number}"

        # then sort out the irregularly named bays
        if room == "lundy bay on capener ward":
            return f"LBOC {bed[-1]}"

        if "discharge area" in room:
            return "DA"

        if self.ward == Ward.FORTESCUE:
            bay_colour = room.split()[0]
            bed_number = int(self.number_pattern.search(bed)[0])
            if bay_colour == "yellow":
                bay_colour = "yell"
            return f"{bay_colour.title()} {bed_number}"

        # then sort out Caroline Thorpe bays
        if self.ward == Ward.CAROLINE_THORPE:
            bay_number = int(self.number_pattern.search(room)[0])
            bed_number = bed[-1]
            return f"B{bay_number} B{bed_number}"

        # this should then cover the rest of the beds
        bay_number = int(self.number_pattern.search(room)[0])
        bed_letter = bed[-1]
        return f"{bay_number}{bed_letter}"

    @property
    def _bed_sort(self) -> str:
        """Helper property for use as a sorting key to correctly sort patients in a list by bed.

        The main purpose is to correctly allow for "SR9" being a lower bed number than "SR10"
        and to handle Fortescue's unique bed-naming convetion.
        """
        if self.is_sideroom and self.ward != Ward.FORTESCUE:
            bed_num = int(self.bed.replace("SR", ""))
            return f"SR{bed_num:02d}"
        elif self.is_sideroom:
            # push side rooms to the bottom, but above discharge areas
            return f"Y{self.bed}"
        elif self.bed == "DA":
            # and discharge areas right to the bottom
            return "ZDA"
        return self.bed

    @property
    def is_sideroom(self) -> bool:
        return "SR" in self.bed

    def __eq__(self, other):
        if isinstance(other, type(self)) and (
            self.ward == other.ward and self.room == other.room and self.bed == other.bed
        ):
            return True
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(ward={self.ward.value}, bay={self.room}, bed={self.bed})"
