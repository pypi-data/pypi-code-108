from random import randint
from .dialetos import DialetoMiguxes

import re


def camelizar(s: str) -> str:
    str_minuscula = [*s.lower()]
    str_camelizada = map(lambda x: x if randint(0, 1) else x.upper(), str_minuscula)
    return ''.join(str_camelizada)


def miguxar(s: str, dialeto: DialetoMiguxes = DialetoMiguxes.MIGUXES_ARCAICO) -> str:
    regexes = DialetoMiguxes.pegar_regex_por_dialeto(dialeto)

    s = s.lower()

    for pattern, repl in regexes:
        s = re.sub(pattern, repl, s)

    if dialeto == DialetoMiguxes.NEO_MIGUXES:
        s = re.sub(r'x', 'xXx', s)
        s = re.sub(r'ss', 'XX', s)
        s = camelizar(s)
    return s
