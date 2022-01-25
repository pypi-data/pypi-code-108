def join_lines(lines: list[str], nl: int = 1) -> str:
    return ''.join(map(lambda l: l.strip('\n') + '\n' * nl if len(l) else '', lines))
