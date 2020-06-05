from enum import Enum


class TeamName(Enum):
    RESPIRATORY = "Respiratory"
    GASTRO = "Gastroenterology"
    CARDIOLOGY = "Cardiology"
    STROKE = "Stroke"
    ARYA = "Arya"
    MARK = "Mark"
    ARBAB = "Arbab"

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
