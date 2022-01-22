# -*- coding: utf-8 -*-

"""Attempt at defining themes from Python (probably better to do
   this elsewhere).
"""

# pylint:disable=R0903,W0232
# R0903 Too few public methods
# W0232 class has no __init__ method


def mkpalette(_source, base, colorlist):
    "Convenience function to define a palette."
    base = '#%s' % base
    colorlist = ['#%s' % c for c in colorlist.split()]
    return [base] + colorlist


# http://www.hypergurl.com/colormatch.php


nt_orange_gurl = mkpalette(
    "http://www.hypergurl.com/colormatch.php?color=F1A000",
    'f1a000',
    'cc8800 a66f00 39a9bf aae6f2 b3f2ff 0d0d0d f2f2f2 000000')

nt_orange_spro_mono = mkpalette(
    "http://www.siteprocentral.com/html_color_code.html",
    'f1a000',
    'efc777 efdbb3 9f7c35 4f3e1a b39559 d0bf9c')


class palette:
    """Color palettes from http://colormatch.dk. Colors are named with
       a lower case x in front of the nearest defined colorvalue.
    """
    class LightSkyBlue2:
        LightSkyBlue2 = '#a4d3ee'
        xLightSlateGray = '#6f8ea1'
        xNavajoWhite2 = '#edd7a4'
        xLemonChiffon4 = '#a1896f'
        Gray7 = '#121212'
        Gray93 = '#ededed'
        get = ['#a4d3ee', '#6f8ea1', '#edd7a4', '#a1896f', '#121212', '#ededed']

    class xForrestGreen:
        xForrestGreen = '#257b24'
        xLimeGreen = '#3cc73a'
        xOliveDrab4 = '#5f7a23'
        xYellowGreen = '#9ac73a'
        Gray52 = '#858585'
        Gray48 = '#7a7a7a'
        get = ['#257b24', '#3cc73a', '#5f7a23', '#9ac73a', '#858585', '#7a7a7a']
