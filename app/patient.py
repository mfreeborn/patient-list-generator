import datetime
import re
from collections import defaultdict

from docx.table import _Row

from app.enums import Ward


class PatientList:
    def __init__(self, home_ward: Ward):
        self.home_ward: Ward = home_ward
        # a mapping of {nhs_number: Patient}
        self._patient_mapping: dict = {}

    def append(self, patient: "Patient") -> None:
        self._patient_mapping[patient.nhs_number] = patient

    def extend(self, patients: list) -> None:
        for pt in patients:
            self.append(pt)

    def sort(self) -> None:
        """Sort the patient list in place.

        Sorts the home ward patients to the top of the list.
        Sorts the outlier wards alphabetically.
        Sort the patients within each ward by bed.
        """
        sorted_dict = {}
        grouped_dict = defaultdict(list)
        # create a mapping of {ward: [Patient]}
        for pt in self:
            grouped_dict[pt.location.ward].append(pt)

        # sort the patients by bed on a per-ward basis
        for ward, pts in grouped_dict.items():
            grouped_dict[ward] = sorted(pts, key=lambda pt: pt.location._bed_sort)

        # populate the new list with the Home Ward patients first
        for pt in grouped_dict.pop(self.home_ward, []):
            sorted_dict[pt.nhs_number] = pt

        # then populate the new list with the outlier patients sorted by ward alphabetically
        for ward in sorted(grouped_dict.keys(), key=lambda k: k.value):
            for pt in grouped_dict[ward]:
                sorted_dict[pt.nhs_number] = pt

        self._patient_mapping = sorted_dict

    @property
    def patients(self):
        return list(self._patient_mapping.values())

    @patients.setter
    def patients(self, value):
        raise AttributeError(
            f"{self.__class__.__name__}.patients is a read-only property."
        )

    def __getitem__(self, key: str) -> "Patient":
        """Return a Patient from the list with a given NHS number."""
        try:
            return self._patient_mapping[key]
        except KeyError:
            raise KeyError(f"No patient with the NHS number '{key}' found in the list")

    def __contains__(self, key: "Patient"):
        """Assert whether a given patient (where type(key) == Patient) is in the list."""
        return key.nhs_number in self._patient_mapping

    def __iter__(self):
        return iter(self._patient_mapping.values())

    def __len__(self):
        return len(self._patient_mapping)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(home_ward={self.home_ward.value}, "
            f"length={len(self._patient_mapping)})>"
        )


class Location:
    fortescue_bay_pattern = re.compile(r"FOR\d(\D{4,6}){1}(BAY)?$")

    def __init__(self, ward: Ward, bay: str, bed: str):
        self.ward: Ward = ward
        self.bay: str = bay
        self.bed: str = self._parse_bed(bay, bed)

    def _parse_bed(self, bay: str, bed: str) -> str:
        """Take the bay/bed as given by the CareFlow API and convert it to a user-friendly format."""
        if self.ward == Ward.FORTESCUE:
            # Fortescue uses a different bed naming convention i.e. Blue 1 or SR Lilac
            if bay.lower().endswith("rm"):
                bay_colour = bay[3:-2].title()
                return f"SR {bay_colour}"

            bay_colour = self.fortescue_bay_pattern.search(bay)[1].title()
            bed_num = int(bed[-1])
            return f"{bay_colour} {bed_num}"
        else:
            if self.is_sideroom:
                return f"SR{int(bay[-2:])}"
            if self.ward == Ward.LUNDY and self.bay.startswith("CAP"):
                self.ward = Ward.CAPENER
            return f"{int(bay[-2:])}{bed[-1]}"

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
            # push side rooms to the bottom
            return f"Z{self.bed}"
        return self.bed

    @property
    def is_sideroom(self) -> bool:
        return "SR" in self.bay or "RM" in self.bay


class Patient:
    nhs_num_pattern = re.compile(r"\d{3}\s?\d{3}\s?\d{4}")

    def __init__(
        self,
        nhs_number: str,
        given_name: str = None,
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

        self._nhs_number: str = nhs_number.replace(" ", "")

        self.given_name: str = given_name
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
    def nhs_number(self):
        return f"{self._nhs_number[:3]} {self._nhs_number[3:6]} {self._nhs_number[6:]}"

    @property
    def age(self) -> str:
        if self.dob is None:
            return

        today = datetime.date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @property
    def list_name(self) -> str:
        if self.given_name is None or self.surname is None:
            return "UNKNOWN, Unknown"

        return f"{self.surname.upper()}, {self.given_name.title()}"

    @property
    def patient_details(self):
        """Return the patient detail's in the correct format for the patient list."""
        if not all([self.surname, self.given_name, self.dob, self.nhs_number]):
            return "UNKNOWN"

        return (
            f"{self.list_name}\n"
            f"{self.dob:%d/%m/%Y} ({self.age} Yrs)\n"
            f"{self.nhs_number}"
        )

    @property
    def bed(self):
        if self.location:
            return self.location.bed

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

        pt_details = row.cells[1].text.strip()
        nhs_number = cls.nhs_num_pattern.search(pt_details)

        if nhs_number is None:
            # no match found by the regex
            raise Exception(
                f"No NHS number found in the table cell with the following contents: {pt_details}"
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
        """Merge 'other_patient''s details into self in place."""
        attrs_to_merge = ["reason_for_admission", "jobs", "edd", "ds", "tta", "bloods"]

        for attr in attrs_to_merge:
            other_pt_attr = getattr(other_patient, attr)
            setattr(self, attr, other_pt_attr)

    def __repr__(self):
        cls_name = self.__class__.__name__
        pt = f"<{cls_name}(name={self.list_name}, age={self.age}, nhs_number={self.nhs_number})>"

        if self.location is None:
            return pt
        return (
            f"<{cls_name}(name={self.list_name}, age={self.age}, nhs_number={self.nhs_number}, "
            f"location=Location(ward={self.location.ward.value}, bed={self.location.bed}))>"
        )
