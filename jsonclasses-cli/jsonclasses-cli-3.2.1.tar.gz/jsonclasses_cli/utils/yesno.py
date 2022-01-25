from typing import Literal


def yesno(text: Literal['Yes', 'No']) -> bool:
    match text:
        case 'Yes':
            return True
        case 'No':
            return False
