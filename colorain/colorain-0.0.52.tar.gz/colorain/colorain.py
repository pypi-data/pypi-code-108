from .colours import *
from .errors import *
import re

##################################################
# Core styling class: StyledText. Every object in
# this library is a StyledText object or inherits
# from it.
##################################################
class StyledText:
    def __init__(self, text):
        if isinstance(text, str):
            self.text = text
        elif isinstance(text, StyledText):
            self.text = text.text
        else:
            raise InvalidInputError(str(type(text)))

        self.parsed = self.parse_color()
   
    def parse_color(self):
        return self.parse_tokens('color')
   
    def raw_text(self):
        return self.parse_tokens('raw')
   
    def parse_tokens(self, replacer):
        parsed_text = self.text
        
        # Defining token pattern
        TAG_PTN = r'<(B|I|U|/|(?:f=.{0,2})|(?:b=.{0,2}))' +\
                    r'(?:;\s*(B|I|U|(?:f=.{0,2})|(?:b=.{0,2})))?'*4 + '>'
        
        tags = re.findall(TAG_PTN, parsed_text)
        if len(tags):
            if self.text.count('</>')==0:
                raise MissingEndTagError

            for tag in tags:
                mx_replacer = parse_token(tag) if replacer=='color' else ''
                parsed_text = parsed_text.replace(f"<{';'.join(tag).strip(';')}>", mx_replacer)
        
        return parsed_text
   
    def add_fg_color(self, color):
        self.text = f'<{fgtokens[color]}>{self.raw_text()}<{fgtokens["end"]}>'
        self.parsed = self.parse_color()
    
    def add_bg_color(self, color):
        self.text = f'<{bgtokens[color]}>{self.raw_text()}<{fgtokens["end"]}>'
        self.parsed = self.parse_color()
    
    def __repr__(self):
        return self.parsed
    
    def __add__(self, clrtxt):
        if 'str' in str(type(clrtxt)):
            return StyledText(self.text+clrtxt)
        if 'colorain' in str(type(clrtxt)):
            return StyledText(self.text+clrtxt.text)


##################################################
# Foreground colouring: wrapper classes #
##################################################
class FGColor(StyledText):
    def __init__(self, text, color):
        super().__init__(text)
        self.add_fg_color(color)

class FGYellow(FGColor):
    def __init__(self, text):
        super().__init__(text,'yellow')

class FGRed(FGColor):
    def __init__(self, text):
        super().__init__(text, 'red')

class FGGray(FGColor):
    def __init__(self, text):
        super().__init__(text, 'darkgray')

class FGCyan(FGColor):
    def __init__(self, text):
        super().__init__(text, 'cyan')

class FGOrange(FGColor):
    def __init__(self, text):
        super().__init__(text, 'orange')

class FGGreen(FGColor):
    def __init__(self, text):
        super().__init__(text, 'green')

class FGPurple(FGColor):
    def __init__(self, text):
        super().__init__(text, 'purple')

class FGBlue(FGColor):
    def __init__(self, text):
        super().__init__(text, 'blue')

class FGLtRed(FGColor):
    def __init__(self, text):
        super().__init__(text, 'lightred')

class FGLtGreen(FGColor):
    def __init__(self, text):
        super().__init__(text, 'lightgreen')

class FGLtCyan(FGColor):
    def __init__(self, text):
        super().__init__(text, 'lightcyan')

class FGLtPurple(FGColor):
    def __init__(self, text):
        super().__init__(text, 'lightpurple')

class FGLtBlue(FGColor):
    def __init__(self, text):
        super().__init__(text, 'lightblue')

Stx = StyledText


##################################################
# Background colouring: wrapper classes #
##################################################
class BGColor(StyledText):
    def __init__(self, text, color):
        super().__init__(text)
        self.add_bg_color(color)

class BGYellow(BGColor):
    def __init__(self, text):
        super().__init__(text, 'yellow')

class BGRed(BGColor):
    def __init__(self, text):
        super().__init__(text, 'red')

class BGGreen(BGColor):
    def __init__(self, text):
        super().__init__(text, 'green')

class BGGray(BGColor):
    def __init__(self, text):
        super().__init__(text, 'darkgray')

class BGCyan(BGColor):
    def __init__(self, text):
        super().__init__(text, 'cyan')

class BGBlue(BGColor):
    def __init__(self, text):
        super().__init__(text, 'blue')

class BGPurple(BGColor):
    def __init__(self, text):
        super().__init__(text, 'purple')


##################################################
# General formatting: wrapper classes #
##################################################
class FmtText(StyledText):
    def __init__(self, text, fmt):
        super().__init__(f"<{fmt}>{text}</>")

class Italic(FmtText):
    def __init__(self, text):
        super().__init__(text, 'I') 

class Bold(FmtText):
    def __init__(self, text):
        super().__init__(text, 'B')

class Underline(FmtText):
    def __init__(self, text):
        super().__init__(text, 'U')


##################################################
# Helper function for viewing available styles #
##################################################
def styles_guide():
    print(StyledText("<f=y;b=r;U>Foreground:</>"))
    for fmt in FMT_CODE:
        print(StyledText(f"<{fmt}>{FMT_NAMES[fmt]}</>: <<f=lr>{fmt}</>>"))
    for clr in fgtokens:
        token = fgtokens[clr]
        print(StyledText(f"<{token}>{clr}</>: <<f=lr>{token}</>>"))

    print(StyledText("<f=y;b=r;U>Background:</>"))
    for clr in bgtokens:
        token = bgtokens[clr]
        print(StyledText(f"<{token}>{clr}</>: <<f=lr>{token}</>>"))


##################################################
# Welcome message in interactive mode #
##################################################
import __main__ as main
if not hasattr(main, '__file__'):
    print(StyledText("<f=o>############################################################</>"))
    print(StyledText(f"<f=lc>Welcome to</> <f=lr>c<f=o>o<f=y>l<f=g>o<f=b>r<f=gr>a<f=lr>i<f=c>n </> <B>{VERSION}</>!"))
    print(StyledText("<f=lc>For getting help on styling, run <f=r>styles_guide()</>. <f=y>Have fun!</>"))
    print(StyledText("<f=o>############################################################</>"))
    print()