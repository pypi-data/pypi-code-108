# utility
from colorama import Fore, Back, Style

BOLD = '\033[1;37;48m'
UNDERLINE = '\033[4;37;48m'


class colored:
    def __init__(self, content, fore=None, back=None, style=None, bold=False, underline=False, reset=True):
        self.content = content
        self.fore = fore
        self.back = back
        self.style = style
        self.reset = reset
        self.bold = bold
        self.underline = underline

    def __str__(self):
        ret = []
        if(self.fore is not None):
            ret.append(eval("Fore.%s" % self.fore))
        if(self.back is not None):
            ret.append(eval("Back.%s" % self.back))
        if(self.style is not None):
            ret.append(eval("Style.%s" % self.Style))
        if(self.bold):
            ret.append(BOLD)
        if(self.underline):
            ret.append(UNDERLINE)
        ret.append(str(self.content))
        if(self.reset):
            ret.append(Style.RESET_ALL)
        return ''.join(ret)
