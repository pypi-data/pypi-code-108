class SlashTypeError(Exception):
    def __init__(self, text): ...


class SlashRulesError(Exception):
    def __init__(self, text): ...


class SlashBadColumnNameError(Exception):
    def __init__(self, text): ...


class SlashBadAction(Exception):
    def __init__(self, text): ...


class SlashPatternMismatch(Exception):
    def __init__(self, text): ...
