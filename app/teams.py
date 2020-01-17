from typing import List

from app.enums import Consultant, TeamName, Ward


class Team:
    def __init__(self, name: TeamName, consultants: List[Consultant], home_ward: Ward):
        self.name: TeamName = name
        self.consultants: List[Consultant] = consultants
        self.home_ward: Ward = home_ward

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name.value < other.name.value

    def __gt__(self, other):
        return self.name.value > other.name.value

    def __str__(self):
        return self.name.value

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name.value}, home_ward={self.home_ward.value})>"


TEAMS = {
    TeamName.RESPIRATORY: Team(
        name=TeamName.RESPIRATORY,
        consultants=[
            Consultant.ALISON_MOODY,
            Consultant.GEORGE_HANDS,
            Consultant.JAREER_RAZA,
        ],
        home_ward=Ward.GLOSSOP,
    ),
    TeamName.GASTRO: Team(
        name=TeamName.GASTRO,
        consultants=[
            Consultant.BYRON_THERON,
            Consultant.ANDREW_DAVIS,
            Consultant.ALEX_MORAN,
            Consultant.GIAS_UDDIN,
        ],
        home_ward=Ward.CAPENER,
    ),
    TeamName.CARDIOLOGY: Team(
        name=TeamName.CARDIOLOGY,
        consultants=[
            Consultant.CHRIS_GIBBS,
            Consultant.DUSHEN_THARMARATNAM,
            Consultant.AMJAD_CHEEMA,
            Consultant.RAHUL_POTLURI,
        ],
        home_ward=Ward.VICTORIA,
    ),
    TeamName.STROKE: Team(
        name=TeamName.STROKE,
        consultants=[Consultant.RIAZ_LATIF],
        home_ward=Ward.STAPLES,
    ),
    TeamName.ARYA: Team(
        name=TeamName.ARYA,
        consultants=[Consultant.VIVEK_ARYA],
        home_ward=Ward.ALEXANDRA,
    ),
    TeamName.ELAMIN: Team(
        name=TeamName.ELAMIN,
        consultants=[Consultant.ELSADIG_ELAMIN],
        home_ward=Ward.CAPENER,
    ),
    TeamName.ARBAB: Team(
        name=TeamName.ARBAB,
        consultants=[Consultant.MAZHAR_ARBAB],
        home_ward=Ward.FORTESCUE,
    ),
}
