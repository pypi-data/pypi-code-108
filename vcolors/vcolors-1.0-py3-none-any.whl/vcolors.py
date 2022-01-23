import colored
from pprint import pprint
from colored import stylize, fg, attr, bg
p_fail = colored.fg('red') + colored.attr('bold')
p_fail_bg = colored.bg('dark_red_1') + colored.fg('red')
p_sucess = colored.fg('green') + colored.attr('bold')
p_sucess_bg = colored.bg('dark_green') + colored.fg('green')
p_warning = colored.fg('yellow') + colored.attr('bold')
p_warning_bg = colored.bg('dark_goldenrod') + colored.fg('yellow')


def printF(text) -> str('Red text'):
    '''Print fail, red text'''
    return pprint((text, p_fail))


def printFBG(text) -> str('Red background'):
    '''Print fail, red text and dark red background'''
    return pprint((text, p_fail_bg))


def printS(text) -> str('Green text'):
    '''Print sucess, green text'''
    return pprint((text, p_sucess))


def printSBG(text) -> str('Green background'):
    '''Print sucess, green text and dark green background'''
    return pprint((text, p_sucess_bg))


def printW(text) -> str('Yellow text'):
    '''Print warning, yellow text'''
    return pprint((text, p_sucess_bg))


def printWBG(text) -> str('Yellow background'):
    '''Print warning, yellow text and dark yellow background'''
    return pprint((text, p_sucess_bg))
