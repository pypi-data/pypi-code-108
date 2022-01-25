#------------------------------------------------------------------------------
#   File:       podunk/prefab/color.py
#   Author:     Jim Storch
#------------------------------------------------------------------------------

BLUE = (0,0,1)
GREEN = (.2, .9, .2)
BLACK = (0, 0, 0)
GREY = (.5, .5, .5)
LIGHT_GREY = (.9, .9, .9)
DARK_GREY = (.25, .25, .25)
WHITE = (1, 1, 1)
DARK_GREEN = (0,.4,0)
DARK_RED = (.6, 0, 0)
DARK_BLUE = (0, 0, .4)
GOLDENROD = (.93, .83, .50)
KHAKI = (1, .96, .76)
SIENNA = (.63, .32, .18)
PACIFIC_BLUE = (.21, .35, .42)


def hex2rgb(s):
    """
    Give me a hexidecimal color string and I will return a tuple of
    red, green, and blue in the range of 0 - 255.
    """
    ## trim leading '#' if present
    if s[0] == '#':
        s = s[1:]
    ## expand short hex notation, 'DEF' = 'DDEEFF'    
    if len(s) == 3:
        s = s[0] + s[0] + s[1] + s[1] + s[2] + s[2]
    ## test for bad input
    elif len(s) != 6: 
        raise "Problem: don't like color string length."
    for c in s.upper():
        if c not in "01234567890ABCDEF":
            raise 'Problem: color string contains non-hexidecimal.'
    ## convert to integers
    red = int(s[:2], 16)
    green = int(s[2:4], 16) 
    blue = int(s[4:6], 16)
    return red,green,blue

def hex2percent(s):
    """
    Give me a hexidecimal color string and I will return a tuple of
    red, green, and blue in the range of 0.0 - 1.0.
    """
    ## get the integer values from hex2rgb()
    ri, gi, bi = hex2rgb(s)        
    ## convert to floating points
    red = ri / 255.0 
    green = gi / 255.0
    blue = bi / 255.0
    return red,green,blue
