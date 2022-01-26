from typing import List

from xlsx_lib.domain.generic_replacements.replacement import Replacement


def replacements_to_json(replacements: List[Replacement]) -> List[dict]:
    return list(
        map(
            lambda replacement: replacement.to_json(),
            replacements
        )
    )
