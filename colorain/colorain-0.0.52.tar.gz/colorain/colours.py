from .errors import *


##################################################
# version info #
##################################################
VERSION = "0.0.51"


##################################################
# Styling codes #
##################################################
CLR_CODE = {
    'black':0,
    'red':1,
    'green':2,
    'yellow':3,
    'blue':4,
    'purple':5,
    'cyan':6,
    'gray':7
}

FMT_CODE = {
    'B':1, # bold
    'I': 3, # italic
    'U':4 # underline
}

FMT_NAMES = {'B': 'bold', 'I': 'italic', 'U': 'underline'}


##################################################
# Block Elements #
##################################################
BLOCK_FULL = chr(9608)
BLOCK_THREEQTR = chr(9619)
BLOCK_HALF = chr(9618)
BLOCK_QTR = chr(9817)

BLOCKS = [BLOCK_FULL, BLOCK_THREEQTR, BLOCK_HALF, BLOCK_QTR]


##################################################
# Foreground and background #
##################################################
GRD_CODE = {'BG':4, 'FG':3}


##################################################
# Making the colour codes #
##################################################
def gcode(ground):
    return lambda clr: f"{GRD_CODE[ground]}{CLR_CODE[clr]}"


##################################################
# Making and parsing tokens for each colour #
##################################################
def make_tokens(ground, names):
    tokens = {}
    for key in names:
        if 'black'==key: 
            alias = 'k'
        elif 'gray'==key: 
            alias = 'gr'
        else:
            alias = key[0]
        if ground=='FG':
            if 'light' in key:
                if 'black' in key: alias+='k'
                elif 'gray' in key: alias+='gr'
                else:
                    alias += key[key.find('light')+len('light')]

        tokens[key] = f'{"f" if ground=="FG" else "b"}={alias}'
    
    return tokens


def parse_token(token):
    parsed_token = {}
    fmt_tags = ['B', 'I', 'U']

    for subtoken in token:
        if len(subtoken):
            if subtoken[0] in ['f','b']:
                abbrs = fg_abbrs if subtoken[0]=='f' else bg_abbrs
                prop_val = subtoken.split('=')[1].strip()
                if prop_val not in abbrs:
                    if prop_val:
                        raise InvalidValueError(subtoken[0], prop_val)
                    else:
                        raise MissingValueError(subtoken[0])
                if subtoken[0]=='f':
                    parsed_token['fg'] = fg_abbrs[prop_val]
                else:
                    parsed_token['bg'] = bg_abbrs[prop_val]

            elif subtoken[0] in fmt_tags:
                parsed_token[subtoken[0]] = True

            elif subtoken[0]=='/':
                parsed_token['end'] = True

            else:
                raise InvalidPropError(subtoken[0])

    return parsed_token_to_code(**parsed_token)


def parsed_token_to_code(bg = None, fg = None, B=None, I=None, U=None, end=None):
    code = '\033['

    if bg: code += f"{bgcodes[bg]};"
    if fg: code += f"{fgcodes[fg]};"
    if B: code += f"{FMT_CODE['B']};"
    if U: code += f"{FMT_CODE['U']};"
    if I: code += f"{FMT_CODE['I']};"
    if end: code += f"{fgcodes['end']};"

    code = code.strip(';')
    code += "m"

    return code


def make_clrcodes():
    fgcodes = {}
    bgcodes = {}
    
    make_fgcode = gcode('FG')
    make_bgcode = gcode('BG')
    
    for clr in CLR_CODE:
        fgcodes['orange' if clr=='yellow' else clr] = make_fgcode(clr)
        bgcodes[clr] = make_bgcode(clr)
    for clr in CLR_CODE:
        fgcodes[clr if clr=='yellow' else ('gray' if clr=='black' else 'light'+clr)] = f'1;{make_fgcode(clr)}'
    bgcodes['gray'] = make_bgcode('gray')
    
    return fgcodes, bgcodes


fgcodes, bgcodes = make_clrcodes()
fgcodes['end'], bgcodes['end'] = '0','0'

fgtokens = make_tokens('FG',fgcodes.keys())
bgtokens = make_tokens('BG', bgcodes.keys())

fg_abbrs = {fgtokens[k].split('=')[1]:k for k in fgtokens}
bg_abbrs = {bgtokens[k].split('=')[1]:k for k in bgtokens}

fgtokens['end'] = '/'
bgtokens['end'] = '/'