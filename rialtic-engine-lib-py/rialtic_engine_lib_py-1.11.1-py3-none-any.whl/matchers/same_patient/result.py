from enum import unique, Enum


@unique
class SamePatientResult(str, Enum):
    Different = "Different Patient"
    Same = "Same Patient"
    Suspected600Y = "Suspected Same Patient with same birth date, gender and first and last name."
    Suspected800Y = "Suspected Same Patient same birth date, gender, first name and address, " \
                    "but different last name"
    Suspected900Y = "Suspected Same Patient with First Name as nickname"
    Error = "Error"

