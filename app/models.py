import datetime
import re
from collections import defaultdict
from typing import Union

import pyodbc
from docx.table import _Row

from app.enums import Ward


class PatientList:
    def __init__(self, home_ward: Ward):
        self.home_ward: Ward = home_ward
        # a mapping of {nhs_number: Patient}
        self._patient_mapping: dict = {}

    def append(self, patient: "Patient") -> None:
        self[patient] = patient

    def extend(self, patients: list) -> None:
        for patient in patients:
            self.append(patient)

    def sort(self) -> None:
        """Sort the patient list in place.

        Applies the following sorting strategy:
            1) Sort the home ward patients to the top of the list
            2) Sort the remaining outlier wards alphabetically
            3) Sort the patients within each ward by bed
        """
        sorted_dict = {}
        grouped_dict = defaultdict(list)
        # create a mapping of {ward: [Patient]}
        for patient in self:
            grouped_dict[patient.location.ward].append(patient)

        # sort the patients by bed on a per-ward basis
        for ward, pts in grouped_dict.items():
            grouped_dict[ward] = sorted(pts, key=lambda patient: patient.location._bed_sort)

        # populate the new list with the Home Ward patients first
        for patient in grouped_dict.pop(self.home_ward, []):
            sorted_dict[patient.nhs_number] = patient

        # then populate the new list with the outlier patients sorted by ward alphabetically
        for ward in sorted(grouped_dict.keys(), key=lambda k: k.value):
            for patient in grouped_dict[ward]:
                sorted_dict[patient.nhs_number] = patient

        self._patient_mapping = sorted_dict

    @property
    def patients(self):
        return list(self)

    @patients.setter
    def patients(self, value):
        raise AttributeError(f"{self.__class__.__name__}.patients is a read-only property.")

    def __getitem__(self, key: Union[str, "Patient"]) -> "Patient":
        """Return a Patient from the list with a given Patient or NHS number."""
        if isinstance(key, Patient):
            key = key.nhs_number
        try:
            return self._patient_mapping[key]
        except KeyError:
            raise KeyError(f"No patient with the NHS number '{key}' found in the list")

    def __setitem__(self, _: str, value: "Patient"):
        if not isinstance(value, Patient):
            raise TypeError

        self._patient_mapping[value.nhs_number] = value

    def __contains__(self, key: Union[str, "Patient"]) -> bool:
        """Assert whether a given patient (where type(key) == Patient) is in the list."""
        if isinstance(key, Patient):
            key = key.nhs_number
        return key in self._patient_mapping

    def __iter__(self):
        return iter(self._patient_mapping.values())

    def __len__(self):
        return len(self._patient_mapping)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}("
            f"home_ward={self.home_ward.value}, "
            f"patient_count={len(self)}, "
            f"new_patient_count={len([pt for pt in self if pt.is_new])})>"
        )


class Location:
    number_pattern = re.compile(r"\d{1,2}")

    def __init__(self, ward: Ward, bay: str, bed: str):
        self.ward: Ward = ward
        self.bay: str = bay
        self.bed: str = self._parse_bed(bay, bed)

    def _parse_bed(self, bay: str, bed: str) -> str:
        """Take the bay/bed as given by TrakCare and convert it to a user-friendly format."""
        # sort out the side rooms first
        bay = bay.lower()
        if "room" in bay:
            # it is a side room
            if self.ward == Ward.FORTESCUE:
                # Fortescue uses colours rather than numbers
                room_colour = bay.split()[0]
                return f"SR {room_colour.title()}"
            room_number = int(self.number_pattern.search(bay)[0])
            return f"SR{room_number}"

        # then sort out the irregularly named bays
        if bay == "lundy bay on capener ward":
            return f"LBOC {bed[-1]}"

        if "discharge area" in bay:
            return "DA"

        if self.ward == Ward.FORTESCUE:
            bay_colour = bay.split()[0]
            bed_number = int(self.number_pattern.search(bed)[0])
            if bay_colour == "yellow":
                bay_colour = "yell"
            return f"{bay_colour.title()} {bed_number}"

        # then sort out Caroline Thorpe bays
        if self.ward == Ward.CAROLINE_THORPE:
            bay_number = int(self.number_pattern.search(bay)[0])
            bed_number = bed[-1]
            return f"B{bay_number} B{bed_number}"

        # this should then cover the rest of the beds
        bay_number = int(self.number_pattern.search(bay)[0])
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
            return f"ZDA"
        return self.bed

    @property
    def is_sideroom(self) -> bool:
        return "SR" in self.bed

    def __repr__(self):
        return f"{self.__class__.__name__}(ward={self.ward.value}, bay={self.bay})"


class Patient:
    nhs_num_pattern = re.compile(r"((?<=\s|\))|^)(\d{3}[ \t]*\d{3}[ \t]*\d{4})(\s+|)", flags=re.M)

    def __init__(
        self,
        nhs_number: str,
        forename: str = None,
        surname: str = None,
        dob: datetime.date = None,
        location: Location = None,
        reason_for_admission: str = None,
        jobs: str = None,
        edd: str = None,
        ds: str = None,
        tta: str = None,
        bloods: str = None,
    ):
        self._nhs_number: str = "".join(nhs_number.split())

        self.forename: str = forename
        self.surname: str = surname
        self.dob: datetime.date = dob

        self.location: Location = location

        self.reason_for_admission: str = reason_for_admission or ""
        self.jobs: str = jobs or ""
        self.edd: str = edd or ""
        self.ds: str = ds or ""
        self.tta: str = tta or ""
        self.bloods: str = bloods or ""

        self.is_new = False

    @property
    def nhs_number(self) -> str:
        return f"{self._nhs_number[:3]} {self._nhs_number[3:6]} {self._nhs_number[6:]}"

    @property
    def age(self) -> str:
        if self.dob is None:
            return

        today = datetime.date.today()
        return (
            today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @property
    def list_name(self) -> str:
        if self.forename is None or self.surname is None:
            return "UNKNOWN, Unknown"

        return f"{self.surname.upper()}, {self.forename.title()}"

    @property
    def patient_details(self) -> str:
        """Return the patient detail's in the correct format for the patient list."""
        if not all([self.surname, self.forename, self.dob, self.nhs_number]):
            return "UNKNOWN"

        return f"{self.list_name}\n" f"{self.dob:%d/%m/%Y} ({self.age} Yrs)\n" f"{self.nhs_number}"

    @property
    def bed(self) -> str:
        if self.location:
            return self.location.bed

    @classmethod
    def from_trakcare(cls, trakcare_patient: pyodbc.Row) -> "Patient":
        """Return a Patient object from a row returned by the TrakCare database query."""
        # TODO: check the date format provided by the TrakCare database compared to the format
        # string we provided below
        # TODO: check the Location bit is at all correct
        return cls(
            forename=trakcare_patient.forename,
            surname=trakcare_patient.surname,
            dob=datetime.datetime.strptime(trakcare_patient.dob, "%d-%b-%Y").date(),
            nhs_number=trakcare_patient.nhs_number,
            location=Location(
                ward=Ward(trakcare_patient.ward),
                bay=trakcare_patient.room,
                bed=trakcare_patient.bed,
            ),
        )

    @classmethod
    def from_table_row(cls, row: _Row) -> "Patient":
        """Return a Patient object from the information held in a table row.

        Expects the row to be in the following format:

            Bed | Patient Details | Issues | Jobs | EDD | DS | TTA | Blds


        The "Bed" cell needs to be something like:

             "1A", "SR8", "SR17", "Pink 2" or "SR Lilac"


        The "Patient Details" cell needs to be in the following format:

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

    def merge(self, other_patient: "Patient") -> None:
        """Merge 'other_patient''s details into self in place.

        This method operates on two instances of the /same/ patient:
            1) 'self': Patient populated from CareFlow with up to date location but no jobs, edd etc
            2) 'other_patient': Patient populated from the handover list with up to date jobs,
                edd etc but missing/outdated patient identifiers

        ...and merges the two together.

        The result should be a fully populated Patient with an up to date location from CareFlow
        as well as up to date information about jobs, edd etc"""
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
        pt = f"<{cls_name}(name={self.list_name}, age={self.age}, nhs_number={self.nhs_number})>"

        if self.location is None:
            return pt
        return (
            f"<{cls_name}(name={self.list_name}, age={self.age}, nhs_number={self.nhs_number}, "
            f"location=Location(ward={self.location.ward.value}, bed={self.location.bed}))>"
        )
