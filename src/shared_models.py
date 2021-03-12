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
    patient_id_pattern = re.compile(
        r"(?:((?<=\s|\))|^)(\d{3}[ \t]*\d{3}[ \t]*\d{4})(\s+|)|\d{7})", flags=re.M
    )

    reg_number = db.Column("RegNumber", db.Text(), primary_key=True)
    _nhs_number = db.Column("NHSNumber", utils.NHSNumber(), default="")
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
        patient_id,
        reason_for_admission=None,
        progress=None,
        jobs=None,
        edd=None,
        tta_ds=None,
        bloods=None,
    ):
        # __init__ is /not/ called when SQLAlchemy loads an row from the database. This
        # method is just for when we create Patient objects in from_table_row
        self.patient_id = "".join(patient_id.split())
        self.reason_for_admission = reason_for_admission or ""
        self.progress = progress or ""
        self.jobs = jobs or ""
        self.edd = edd or ""
        self.tta_ds = tta_ds or ""
        self.bloods = bloods or ""

    @property
    def patient_id(self):
        """Return the patient ID which is preferably the NHS number or falls back to reg_number."""
        # reg_number is never None, so it is valid to use it as a fallback
        return self.nhs_number or self.reg_number

    @patient_id.setter
    def patient_id(self, patient_id: str):
        # patient_id is one either the NHS number or the Trak registration number. They can be
        # differentiated by their length: NHS numbers are 10 digits long, whilst Trak numbers
        # are 7 characters long
        if len(patient_id) == 10:
            self.nhs_number = patient_id
        elif len(patient_id) == 7:
            self.reg_number = patient_id
        else:
            raise ValueError("Patient ID not recognised!")

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
        return ""

    @nhs_number.setter
    def nhs_number(self, value):
        if value:
            value = "".join(value.split())
        self._nhs_number = value

    @hybrid_property
    def age(self) -> int:
        if self.dob is None:
            return

        today = datetime.date.today()
        return (
            today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @hybrid_property
    def is_birthday(self):
        if not self.dob:
            return False

        today = datetime.date.today()
        birthday = self.dob.replace(year=today.year)
        if today == birthday:
            return True
        return False

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
        # default to NHS number, but fall back to Trak reg number
        patient_id = self.nhs_number or self.reg_number
        return f"{self.list_name}\n" f"{self.dob:%d/%m/%Y} ({self.age} Yrs)\n" f"{patient_id}"

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

            Bed | Patient Details | Issues | Inpatient Progress | Jobs | EDD | TTA/DS | Blds

        NOTE:
        Although we assume the above column headers, the only ones that this program actually
        overwrites are Bed, Patient Details and, when adding a "new" patient, Issues. The only
        requirement thereafter is for there to be 8 columns in total. As such, the names of
        columns[3:] don't actually need to match with the variable names allocated below.

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
        patient_id = cls.patient_id_pattern.search(patient_details)

        if patient_id is None:
            # no match found by the regex
            raise ValueError(
                f"No NHS number found in the table "
                f"cell with the following contents:\n{patient_details}"
            )
        else:
            # retrieves the NHS number from the successful regex match
            patient_id = patient_id[0]

        issues = row.cells[2].text.strip()
        progress = row.cells[3].text.strip()
        jobs = row.cells[4].text.strip()
        edd = row.cells[5].text.strip()
        tta_ds = row.cells[6].text.strip()
        bloods = row.cells[7].text.strip()

        patient = cls(
            patient_id=patient_id,
            reason_for_admission=issues,
            progress=progress,
            jobs=jobs,
            edd=edd,
            tta_ds=tta_ds,
            bloods=bloods,
        )

        patient.is_new = False

        return patient

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

        attrs_to_merge = [
            "reason_for_admission",
            "progress",
            "jobs",
            "edd",
            "tta_ds",
            "bloods",
            "is_new",
        ]

        for attr in attrs_to_merge:
            other_pt_attr = getattr(other_patient, attr)
            setattr(self, attr, other_pt_attr)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.patient_id == other.patient_id

    def __repr__(self):
        cls_name = self.__class__.__name__
        pt = f"<{cls_name}(name={self.list_name}, patient_id={self.patient_id})>"
        if self.location is None:
            return pt
        return (
            f"<{cls_name}(name={self.list_name}, patient_id={self.patient_id}, "
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
            return f"{bay_colour.title()} {bed_number}"

        # then sort out Caroline Thorpe bays
        if self.ward == Ward.CAROLINE_THORPE:
            bay_number = int(self.number_pattern.search(room)[0])
            bed_number = bed[-1]
            return f"Bay {bay_number} Bed {bed_number}"

        # this should then cover the rest of the beds
        bay_number = int(self.number_pattern.search(room)[0])
        bed_letter = bed[-1]
        return f"{bay_number}{bed_letter}"

    @property
    def _bed_sort(self) -> str:
        """Helper property for use as a sorting key to correctly sort patients in a list by bed.

        The main purpose is to correctly allow for "SR9" being a lower bed number than "SR10"
        and to handle Fortescue's unique bed-naming convention.
        """
        if self.ward == Ward.FORTESCUE:
            # first, deal with Fortescue. The order of the bays matches the physical layout
            # of the ward, rather than the alphabetical position of the bay colour
            bay_order = {
                "Green": 1,
                "Yellow": 2,
                "Lilac": 3,
                "Blue": 4,
                "Pink": 5,
            }
            if self.is_sideroom:
                # siderooms forced to the bottom
                room_colour = self.bed.split()[1]
                return f"Z{bay_order[room_colour]}"
            else:
                # again, sort beds by physical bay location
                bay_colour = self.bed.split()[0]
                bed_number = self.bed.split()[1]
                return f"{bay_order[bay_colour]}{bed_number}"

        # handle the rest of the wards
        if self.is_sideroom:
            # 0-pad single digit room numbers (9 -> 09) so that SR9 is sorted after SR10
            bed_num = int(self.bed.replace("SR", ""))
            return f"SR{bed_num:02d}"
        elif self.bed == "DA":
            # and discharge areas right to the bottom
            return "ZBDA"
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
