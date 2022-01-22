from curses.ascii import isblank
from ossaudiodev import SOUND_MIXER_TREBLE
import re

from Binop import Binop
from Unop import Unop
class Translator:
    def translate(code):
        asm = ""
        ops= re.findall(r"((.*)\s([=><\+\*-/&\|!%\?(push)(pop)(jump)(call)(cmp)(test)(printstr)(printnum)]+)\s(.*))|(<(.*)>)", code)
        for op in ops:
            if (op[5].strip() != ""):
                asm += op[5].strip() + ":\n"
            elif op[1].strip() != "":
                b = Binop(op[1], op[3], op[2])
                asm += b.asm()
            else:
                u = Unop(op[3], op[2])
                asm += u.asm()
        return asm