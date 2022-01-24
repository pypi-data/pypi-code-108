from sapply.cmapdefs import cmapdefs
from sapply.charmap import read_charmap
from sapply.flip import flip
from sapply.zalgo import zalgo
from sapply.morse import to_morse
from sapply.tokens import to_string,parse_transforms
from pathlib import Path
from signal import signal, SIGPIPE, SIG_DFL
import sys
import site

signal(SIGPIPE, SIG_DFL)

MAJOR, MINOR, PATCH = '0', '1', '0'

def convert(char_map, text):
    out = ""
    for char in text:
        if char in char_map:
            out += char_map[char]
        elif char.lower() in char_map:
            out += char_map[char.lower()]
        else:
            out += char
    return out

def strikethrough(text, strikeover):
    return ''.join([char + strikeover for char in text])

def mapto(cmap: str):
    file = cmapdefs[cmap]
    form = lambda sitefp: Path(f'{sitefp}/sapply').expanduser()
    root    = f'{form(site.getsitepackages())}/resources/{file}'
    local   = f'{form(site.getusersitepackages())}/resources/{file}'
    path    = root if Path(root).is_dir() else local
    return (read_charmap(path))

def match_effects(cmd: str, text: str, opt=None) -> str:
    out = ''
    opt = u'\u0336' if (opt == '-') else u'\u0334' # - or ~ strikethrough

    match cmd:
        case '--sub'                        : out = convert(mapto('subscript'), text)
        case '--super'                      : out = convert(mapto('superscript'), text)
        case '-ds'      | '--doublestruck'  : out = convert(mapto('doubleStruck'), text)
        case '-oe'      | '--oldeng'        : out = convert(mapto('oldEnglish'), text)
        case '-med'     | '--medieval'      : out = convert(mapto('medieval'), text)
        case '-mono'    | '--monospace'     : out = convert(mapto('monospace'), text)
        case '-b'       | '--bold'          : out = convert(mapto('bold'), text)
        case '-i'       | '--italics'       : out = convert(mapto('italic'), text)
        case '-bs'  | '--boldsans'          : out = convert(mapto('boldSans'), text)
        case '-ib'  | '--italicbold'        : out = convert(mapto('boldItalic'), text)
        case '-is'  | '--italicsans'        : out = convert(mapto('italicSans'), text)
        case '-st'  | '--strike'            : out = strikethrough(text, opt)
    return out

def main():
    cmds = ['flip', 'zalgo', 'morse']

    subcmd = None
    text = None
    effects = None

    for cmd in cmds:
        if cmd in sys.argv:
            subcmd = cmd

    if subcmd is None:
        text = sys.argv[1]
        effects = sys.argv[2:]
    else:
        text    = sys.argv[2]
        effects = sys.argv[3:]

    if not text:
        sys.exit()

    # Subcommands
    match subcmd:
        case 'flip'     : flip(text)
        case 'zalgo'    : zalgo(text)
        case 'morse'    : print(to_morse(text.upper())) # TODO: Pass `effects` off to function for processing
    if (subcmd is not None):
        return

    out = ""
    if (len(effects) < 2):
        cmd = effects[0]
        out = match_effects(cmd, text)

    elif (len(effects) < 3):
        cmd = effects[0]
        opt = effects[1]
        if (opt is None):
            opt = re.match(re.compile(r'-st='), cmd)
        # Handle combinable effects
        match cmd, opt:
            case '--cmap', _:
                cmap = read_charmap(opt)
                out = convert(cmap, text)
            case '-f', _:
                # opt == fp
                token_dict = parse_transforms(opt)
                for effect, text in token_dict.items():
                    if (text == '\n'):
                        out += '\n'
                    else:
                        out += match_effects(effect, text) + ' '
            case _,_: out = match_effects(effect, text, opt)
    print(out)
