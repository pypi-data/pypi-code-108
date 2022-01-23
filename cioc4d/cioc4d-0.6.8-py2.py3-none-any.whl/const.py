"""
Contains definitions of common constants.


This file must be kept at the same level as the plugin "pyp" file so we can extract the version.
"""
import os
import re
import c4d

LABEL_WIDTH = 180
LABEL_HEIGHT = 14
INT_FIELD_WIDTH = 100

# PLUGIN_ID = 1055243 # registered for Conductor at Maxon
# (In S24): RuntimeError:The plugin ID '1055243' collides with another plugin ID in 'Ca.xlib'.

# New plugin ID due to above clash
# com.conductortech.cioc4d
# comconductortechcioc4d	1057859	2021-07-08 21:09:46
PLUGIN_ID = 1057859 # registered for Conductor at Maxon

PLUGIN_LOCALIZE_ID = 1057860 #tmp

C4D_VERSION = int(c4d.GetC4DVersion() / 1000)
 

PLUGIN_DIR = os.path.dirname(__file__)

CONDUCTOR_COMMAND_PATH = os.path.join(os.path.dirname(PLUGIN_DIR), "bin","conductor")

VERSION = "dev.999"
try:
    with open(os.path.join(PLUGIN_DIR, "VERSION")) as version_file:
        VERSION = version_file.read().strip()
except BaseException:
    pass


FIXTURES_DIR = os.path.expanduser(os.path.join("~","conductor_fixtures" ))
 

RENDERERS = {
 'standard': c4d.RDATA_RENDERENGINE_STANDARD,
 'physical':c4d.RDATA_RENDERENGINE_PHYSICAL,
 'arnold':1029988,
 'vray':1019782,
 'redshift':1036219
}
