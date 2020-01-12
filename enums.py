from enum import Enum


class TeamName(Enum):
    RESPIRATORY = "Respiratory"
    GASTRO = "Gastroenterology"
    CARDIOLOGY = "Cardiology"
    STROKE = "Stroke"
    ARYA = "Arya"
    ELAMIN = "Elamin"
    ARBAB = "Arbab"

    def __str__(self):
        return self.value


class Ward(Enum):
    ALEXANDRA = "Alexandra"
    CAPENER = "Capener"
    DAY_SURGERY_UNIT = "Day Surgery Unit NDDH"
    FORTESCUE = "Fortescue"
    GLOSSOP = "Glossop"
    KGV = "King George Vth (Surgical Assessment Unit)"
    LUNDY = "Lundy"
    ROBOROUGH = "Roborough"
    STAPLES = "Staples"
    TARKA = "Tarka"
    VICTORIA = "Victoria"


class Consultant(Enum):
    ALISON_MOODY = "Dr Alison Moody"
    GEORGE_HANDS = "Dr Georgina Hands"
    JAREER_RAZA = "Dr Jareer Raza"

    CHRIS_GIBBS = "Dr Christopher Gibbs"
    DUSHEN_THARMARATNAM = "Dr Dushen Tharmaratnam"
    AMJAD_CHEEMA = "Muhammad Cheema"
    RAHUL_POTLURI = "Dr Rahul Potluri"

    BYRON_THERON = "Dr Byron Theron"
    ANDREW_DAVIS = "Dr Andrew Davis"
    ALEX_MORAN = "Dr Alex Moran"
    GIAS_UDDIN = "Dr Gias Uddin"

    VIVEK_ARYA = "Dr Vivek Arya"

    MAZHAR_ARBAB = "Dr Mazhar Arbab"

    RIAZ_LATIF = "Dr Riaz Latif"

    ELSADIG_ELAMIN = "Dr Elsadig Elamin"
