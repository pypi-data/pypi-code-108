from .bad_gr import BadGR, BadGR_fix
from .bad_l import BadL, BadL_fix
from .bad_phil import BadPHIL, BadPHIL_fix
from .bad_prom_date import BadPROMDATE, BadPROMDATE_fix
from .bad_scra import BadSCRA, BadSCRA_fix
from .bad_space_date import BadSPACEDATE, BadSPACEDATE_fix


def transform(text: str):

    text = BadPROMDATE.sub(BadPROMDATE_fix, text)
    text = BadSPACEDATE.sub(BadSPACEDATE_fix, text)

    for s in BadSCRA:
        text = s.pattern.sub(BadSCRA_fix, text)

    for p in BadPHIL:
        text = p.pattern.sub(BadPHIL_fix, text)

    text = BadGR.sub(BadGR_fix, text)

    text = BadL.sub(BadL_fix, text)

    return text
