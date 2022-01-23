from enum import Enum


class CrewRole(Enum):
    """
    Role członka kadry.
    """
    PSOR = "Tutor"
    HEADMASTER = "HeadMaster"


class CampLevel(Enum):
    """
    Poziomy obozów.

    :cvar TITAN: starcie tytanów. Tak, z jakiegoś powodu to jest poziom, a nie program/świat (VARIOUS).
    """
    NORMAL = "Normal"
    MASTER = "Master"
    TITAN = "Titan"


class World(Enum):
    """
    Światy, w których organizowane są obozy.

    :cvar ALL: wszystkie 4 światy.
    :cvar VARIOUS: tematyczne turnusy, np. "Smocza Straż", "Sekret Zamkowej Krypty", "Księżniczki i Rycerze".
    """
    WIZARDS = "Wizzards"  # English 100
    PATHFINDERS = "Pathfinders"
    RECRUITS = "Recruits"
    SANGUINS = "Sanguins"

    VARIOUS = "Various"

    ALL = "All"


class Season(Enum):
    """
    Pory roku (w czterech światach są tylko dwie :P).
    """
    SUMMER = "Summer"
    WINTER = "Winter"


class EventReservationOption(Enum):
    """
    Opcje rezerwacji inauguracji.
    """
    CHILD = "Tylko dziecko"
    CHILD_AND_ONE_PARENT = "Dziecko + Rodzic"
    CHILD_AND_TWO_PARENTS = "Dziecko + 2 Rodziców"


class TShirtSize(Enum):
    """
    Rozmiary koszulki.
    """
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class SourcePoll(Enum):
    """
    Źródło dowiedzenia się o Quatromondis.
    """
    INTERNET = "Internet"
    SOCIALS = "Socials"
    RADIO = "Radio"
    TV = "TV"
    FRIENDS = "Friends"
    FLYERS = "Flyers"
    PRESS = "Press"