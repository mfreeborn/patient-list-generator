from app.enums import Consultant, TeamName, Ward
from app.models import Team


TEAMS = {
    TeamName.RESPIRATORY: Team(
        name=TeamName.RESPIRATORY,
        consultants=[Consultant.ALISON_MOODY, Consultant.GEORGE_HANDS, Consultant.JAREER_RAZA],
        home_ward=Ward.CAPENER,
    ),
    TeamName.GASTRO: Team(
        name=TeamName.GASTRO,
        consultants=[Consultant.BYRON_THERON, Consultant.ANDREW_DAVIS, Consultant.ALEX_MORAN],
        home_ward=Ward.CAPENER,
    ),
    TeamName.CARDIOLOGY: Team(
        name=TeamName.CARDIOLOGY,
        consultants=[
            Consultant.CHRIS_GIBBS,
            Consultant.DUSHEN_THARMARATNAM,
            Consultant.RAHUL_POTLURI,
            Consultant.SUJOY_ROY,
        ],
        home_ward=Ward.VICTORIA,
    ),
    TeamName.STROKE: Team(
        name=TeamName.STROKE, consultants=[Consultant.RIAZ_LATIF], home_ward=Ward.STAPLES,
    ),
    TeamName.ARYA: Team(
        name=TeamName.ARYA, consultants=[Consultant.VIVEK_ARYA], home_ward=Ward.ALEXANDRA,
    ),
    TeamName.MARK: Team(
        name=TeamName.MARK, consultants=[Consultant.ADETOKUNBOH_MARK], home_ward=Ward.FORTESCUE,
    ),
    TeamName.ARBAB: Team(
        name=TeamName.ARBAB, consultants=[Consultant.MAZHAR_ARBAB], home_ward=Ward.FORTESCUE,
    ),
}
