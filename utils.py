import datetime
from collections import defaultdict

from docx.table import _Row

from enums import Ward


class PatientList:
    def __init__(self, home_ward: Ward):
        self.home_ward: Ward = home_ward
        self._patient_list: list = []

    def append(self, patient: "Patient") -> None:
        self._patient_list.append(patient)

    def extend(self, patients: list) -> None:
        self._patient_list.extend(patients)

    def sort(self) -> None:
        """Sort the patient list in place.

        Sorts the home ward patients to the top of the list.
        Sorts the outlier wards alphabetically.
        Sort the patients within each ward by bed.
        """
        grouped_dict = defaultdict(list)
        sorted_list = []
        for pt in self:
            grouped_dict[pt.location.ward].append(pt)

        for ward, pts in grouped_dict.items():
            grouped_dict[ward] = sorted(pts, key=lambda pt: pt.location._bed_sort)

        sorted_list.extend(grouped_dict.pop(self.home_ward, []))

        for key in sorted(grouped_dict.keys(), key=lambda k: k.value):
            sorted_list.extend(grouped_dict[key])

        self._patient_list = sorted_list

    @property
    def patients(self):
        return self._patient_list

    @patients.setter
    def patients(self):
        raise AttributeError(f"{self.__class__.__name__} is a read-only property.")

    def __iter__(self):
        return iter(self._patient_list)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(home_ward={self.home_ward.value}, "
            f"length={len(self._patient_list)})>"
        )


class Location:
    def __init__(self, ward: Ward, bay: str, bed: str):
        self.ward: Ward = ward
        self.bay: str = bay
        self.bed: str = self._parse_bed(bay, bed)

    def _parse_bed(self, bay: str, bed: str) -> str:
        if self.ward == Ward.FORTESCUE:
            # Fortescue uses a different bed naming convention i.e. Blue 1 or SR Lilac
            if bay.lower().endswith("rm"):
                bay_colour = bay[3:-2]
                return f"SR {bay_colour}"
            bay_colour = bay[4:-3].title()
            bed_num = int(bed[-2:])
            return f"{bay_colour} {bed_num}"
        else:
            if self.is_sideroom:
                return f"SR{int(bay[-2:])}"
            return f"{int(bay[-2:])}{bed[-1]}"

    @property
    def _bed_sort(self) -> str:
        """Helper property for use as a sorting key to correctly sort patients in a list by bed.

        The main purpose is to correctly allow for "SR9" being a lower bed number than "SR10"
        and to handle FOrtescue's unique bed-naming convetion
        """
        if self.is_sideroom and self.ward != Ward.FORTESCUE:
            bed_num = int(self.bed.replace("SR", ""))
            return f"SR{bed_num:02d}"
        elif self.is_sideroom:
            # push Fortescue side rooms to the bottom
            return f"z{self.bed}"
        return self.bed

    @property
    def is_sideroom(self) -> bool:
        return "SR" in self.bay

    @classmethod
    def from_table_cell(cls, cell_contents: str, ward: str) -> "Location":
        cell_contents = cell_contents.strip()
        ward = Ward(ward)

        # Fortescue has a different bed-naming convention, so handle it specifically
        if ward == Ward.FORTESCUE:
            if "sr" in cell_contents.lower():
                bay_colour = cell_contents.split()[1]
                bed_num = "01"
                bay = f"FORX{bay_colour}BAY"
            else:
                bay_colour = cell_contents.split()[0]
                bed_num = cell_contents.split()[1]
                bay = f"FOR{bay_colour}RM"

        else:
            room_type = "BAY"
            bay_num = cell_contents[0]
            bed_num = cell_contents[1]
            if "sr" in cell_contents.lower():
                room_type = "SR"
                bay_num = cell_contents.replace("SR", "")
                bed_num = "01"

            # should be something like "GLOBAY02" or "GLOSR17"
            bay = f"{ward.value.upper()[:3]}{room_type}{int(bay_num):02d}"

        return cls(ward=ward, bay=bay, bed=f"Bed{bed_num}")


class Patient:
    def __init__(
        self,
        given_name: str,
        surname: str,
        dob: datetime.date,
        nhs_number: str,
        location: Location = None,
        reason_for_admission: str = None,
        jobs: str = None,
        edd: str = None,
        ds: str = None,
        tta: str = None,
        bloods: str = None,
    ):
        self.given_name: str = given_name
        self.surname: str = surname
        self.dob: datetime.date = dob
        self.nhs_number: str = nhs_number

        self.location: Location = location

        self.reason_for_admission: str = reason_for_admission or ""
        self.jobs: str = jobs or ""
        self.edd: str = edd or ""
        self.ds: str = ds or ""
        self.tta: str = tta or ""
        self.bloods: str = bloods or ""

        self.is_new = False

    @property
    def age(self) -> str:
        today = datetime.date.today()
        return str(
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.surname}"

    @property
    def patient_details(self):
        """Return the patient detail's in the correct format for the patient list."""
        return (
            f"{self.surname.upper()}, {self.given_name.title()}\n"
            f"{self.dob.strftime('%d/%m/%Y')} ({self.age} Yrs)\n"
            f"{self.nhs_number}"
        )

    @property
    def bed(self):
        return self.location.bed

    @classmethod
    def from_table_row(cls, row: _Row, ward: str) -> "Patient":
        """Return a Patient object from the information held in a table row.

        Expects the row to be in the following format:

            Bed | Patient Details | Issues | Jobs | EDD | DS | TTA | Blds


        The "Bed" cell needs to be something like:

             "1A", "SR8", "SR17", "Pink 2" or "SR Lilac"


        The "Patient Details" cell needs to be in the following format:

            SMITH, John
            01/01/1975 (45 Yrs)
            123 456 7890
        """
        pt_details = row.cells[1].text.strip()
        name, dob_age, nhs_number = pt_details.split("\n")

        given_name = name.split(", ")[1]
        surname = name.split(", ")[0].title()
        dob = datetime.datetime.strptime(dob_age.split()[0], "%d/%m/%Y").date()

        location = Location.from_table_cell(row.cells[0].text, ward)

        issues = row.cells[2].text.strip()
        jobs = row.cells[3].text.strip()
        edd = row.cells[4].text.strip()
        ds = row.cells[5].text.strip()
        tta = row.cells[6].text.strip()
        bloods = row.cells[7].text.strip()

        return cls(
            given_name=given_name,
            surname=surname,
            dob=dob,
            nhs_number=nhs_number,
            location=location,
            reason_for_admission=issues,
            jobs=jobs,
            edd=edd,
            ds=ds,
            tta=tta,
            bloods=bloods,
        )

    def __repr__(self):
        cls_name = self.__class__.__name__
        pt = f"<{cls_name}(name={self.full_name}, age={self.age}, nhs_number={self.nhs_number})>"

        if self.location is None:
            return pt
        return (
            f"<{cls_name}(name={self.full_name}, age={self.age}, nhs_number={self.nhs_number}, "
            f"location=Location(ward={self.location.ward.value}, bed={self.location.bed}))>"
        )

    def __eq__(self, other):
        return (self.dob == other.dob) & (self.nhs_number == other.nhs_number)


def remove_table_row(table, row):
    tbl = table._tbl
    tr = row._tr
    tbl.remove(tr)
