from enum import Enum


class TeamModel:
    def __init__(self, name, consultants, home_ward):
        self.name = name
        self.consultants = consultants
        self.home_ward = home_ward

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name.value < other.name.value

    def __gt__(self, other):
        return self.name.value > other.name.value

    def __str__(self):
        return self.name.value

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(name={self.name.value}, home_ward={self.home_ward.value})>"
        )


class Consultant(Enum):
    ALISON_MOODY = "Dr Alison Moody"
    GEORGE_HANDS = "Dr Georgina Hands"
    JAREER_RAZA = "Dr Jareer Raza"

    CHRIS_GIBBS = "Dr Christopher Gibbs"
    DUSHEN_THARMARATNAM = "Dr Dushen Tharmaratnam"
    RAHUL_POTLURI = "Dr Rahul Potluri"
    SUJOY_ROY = "Dr Sujoy Roy"

    BYRON_THERON = "Dr Byron Theron"
    ANDREW_DAVIS = "Dr Andrew Davis"
    ALEX_MORAN = "Dr Alex Moran"
    GIAS_UDDIN = "Dr Gias Uddin"

    VIVEK_ARYA = "Dr Vivek Arya"

    MAZHAR_ARBAB = "Dr Mazhar Arbab"

    RIAZ_LATIF = "Dr Riaz Latif"

    ADETOKUNBOH_MARK = "Dr Adetokunboh Mark"


class TeamName(Enum):
    ARBAB = "Arbab"
    ARYA = "Arya"
    CARDIOLOGY = "Cardiology"
    GASTRO = "Gastro"
    MARK = "Mark"
    RESPIRATORY = "Respiratory"
    STROKE = "Stroke"

    def __str__(self):
        return self.value


class Ward(Enum):
    ALEXANDRA = "Alexandra"
    CAPENER = "Capener"
    CAROLINE_THORPE = "Caroline Thorpe"
    DAY_SURGERY_UNIT = "Day Surgery Unit NDDH"
    FORTESCUE = "Fortescue"
    GLOSSOP = "Glossop"
    KGV = "King George Vth (Surgical Assessment Unit)"
    LUNDY = "Lundy"
    ROBOROUGH = "Roborough"
    STAPLES = "Staples"
    TARKA = "Tarka"
    VICTORIA = "Victoria"


# Team needs to come after the rest of the enums so that the previous enums can be used to
# instantiate shared_models.Team instances
class Team(Enum):
    ARBAB = TeamModel(
        name=TeamName.ARBAB, consultants=[Consultant.MAZHAR_ARBAB], home_ward=Ward.FORTESCUE
    )

    ARYA = TeamModel(
        name=TeamName.ARYA, consultants=[Consultant.VIVEK_ARYA], home_ward=Ward.ALEXANDRA
    )

    CARDIOLOGY = TeamModel(
        name=TeamName.CARDIOLOGY,
        consultants=[
            Consultant.CHRIS_GIBBS,
            Consultant.DUSHEN_THARMARATNAM,
            Consultant.RAHUL_POTLURI,
            Consultant.SUJOY_ROY,
        ],
        home_ward=Ward.VICTORIA,
    )

    GASTRO = TeamModel(
        name=TeamName.GASTRO,
        consultants=[
            Consultant.BYRON_THERON,
            Consultant.ANDREW_DAVIS,
            Consultant.GIAS_UDDIN,
            Consultant.ALEX_MORAN,
        ],
        home_ward=Ward.CAPENER,
    )

    MARK = TeamModel(
        name=TeamName.MARK, consultants=[Consultant.ADETOKUNBOH_MARK], home_ward=Ward.FORTESCUE
    )

    RESPIRATORY = TeamModel(
        name=TeamName.RESPIRATORY,
        consultants=[Consultant.ALISON_MOODY, Consultant.GEORGE_HANDS, Consultant.JAREER_RAZA],
        home_ward=Ward.CAPENER,
    )

    STROKE = TeamModel(
        name=TeamName.STROKE, consultants=[Consultant.RIAZ_LATIF], home_ward=Ward.STAPLES
    )

    @classmethod
    def from_team_name(cls, team_name):
        for name, member in cls.__members__.items():
            if team_name.lower() == name.lower():
                return member.value
        raise ValueError(f"{team_name!r} is not a valid {cls.__name__}")
