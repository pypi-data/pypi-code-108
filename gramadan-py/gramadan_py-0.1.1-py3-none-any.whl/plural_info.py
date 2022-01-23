import re
from dataclasses import dataclass, field
from .features import FormSg, Form, FormPlGen, Strength
from .opers import Opers

# FIXME
# IMPORTANT NOTE: the original C# tester does not seem
# to cover these classes, so Python testing is non-existent
# for these so far.

@dataclass
class PluralInfo:
    strength: Strength
    nominative: list[Form] = field(default_factory=list)
    genitive: list[Form] = field(default_factory=list)
    vocative: list[Form] = field(default_factory=list)

    def print(self) -> str:
        ret: str = ""
        ret += "NOM: "
        f: Form
        for f in self.nominative:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "GEN: "

        for f in self.genitive:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "VOC: "

        for f in self.vocative:
            ret += "[" + f.value + "] "
        ret += "\n"
        return ret


# Plural class LgC: weak, plural formed by slenderization.
class PluralInfoLgC(PluralInfo):
    def __init__(self, bayse: str, slenderizationTarget: str = "", v2: bool = False):
        super().__init__(strength=Strength.Weak)

        # generate the genitive:
        form: str = Opers.Broaden(bayse)
        self.genitive.append(Form(form))

        # generate the vocative:
        form = form + "a"
        self.vocative.append(Form(form))

        # generate the nominative:
        form = bayse
        form = re.sub("ch$", "gh", form)
        # eg. bacach > bacaigh
        form = Opers.SlenderizeWithTarget(form, slenderizationTarget, v2=v2)
        self.nominative.append(Form(form))


# Plural class LgE: weak, plural formed by suffix "-e".
class PluralInfoLgE(PluralInfo):
    def __init__(self, bayse: str, slenderizationTarget: str = "", v2: bool = False):
        super().__init__(strength=Strength.Weak)

        form: str = bayse
        form = Opers.SlenderizeWithTarget(form, slenderizationTarget, v2=v2) + "e"

        self.nominative.append(Form(form))
        self.genitive.append(Form(Opers.Broaden(bayse)))
        self.vocative.append(Form(form))


# Plural class LgA: weak, plural formed by suffix "-a".
class PluralInfoLgA(PluralInfo):
    def __init__(self, bayse: str, broadeningTarget: str = ""):
        super().__init__(strength=Strength.Weak)

        form: str = bayse
        form = Opers.BroadenWithTarget(form, broadeningTarget) + "a"

        self.nominative.append(Form(form))
        self.genitive.append(Form(Opers.Broaden(bayse)))
        self.vocative.append(Form(form))


# Plural class Tr: strong.
class PluralInfoTr(PluralInfo):
    def __init__(self, bayse: str):
        super().__init__(strength=Strength.Strong)
        self.nominative.append(Form(bayse))
        self.genitive.append(Form(bayse))
        self.vocative.append(Form(bayse))
