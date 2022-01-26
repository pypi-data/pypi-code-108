from enum import Enum, auto


class AutodiagnosisCellValueKind(Enum):
    FAULT_CONTENT = auto()
    CODE_COLUMN_TITLE = auto()
    ELEMENT_COLUMN_TITLE = auto()
    FAULT_DESCRIPTION_COLUMN_TITLE = auto()

