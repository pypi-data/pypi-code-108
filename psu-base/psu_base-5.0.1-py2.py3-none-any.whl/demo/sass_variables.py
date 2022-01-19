# Any SASS variables that you would like to override may be defined in this file
# If you'd rather use a default value, either set the value to None, or remove it altogether.

# Every time you change the values, delete your sass_build directory to re-generate the css

# ---- COLORS ----
# Colors may be defined as their HTML color name, hex code, or as RGB or RGBA tuples
# Color names may contain non-word characters for readability, and are not case-sensitive
#     Example: "Light_Slate-Gray" would be converted to "lightslategray"
PRIMARY_BG_COLOR = None
PRIMARY_FG_COLOR = None
HEADING_COLOR = None
TEXT_COLOR = None
CODE_COLOR = None

# PSU Logo will be automatically filtered to match the primary_fg_color (if other than the default; white)
# This JS processing can be avoided by pasting the resulting css filter here (get it by inspecting the filtered logo)
# This may also be set to "none" (as a string) to leave the logo as white when non-white text was specified
PSU_LOGO_FILTER = None

# Navigation tabs should be white, unless it conflicts with other color definitions
ACTIVE_TAB_BG_COLOR = None              # white
ACTIVE_TAB_FG_COLOR = None              # primary bg color

# By default, primary and default (i.e. btn-primary, btn-default) colors are based on primary bg and fg colors above
# Depending on what you selected, the default variations of them may look awful!
BOOTSTRAP_PRIMARY = None                # psu-green
BOOTSTRAP_PRIMARY_COMPLIMENT = None     # white
BOOTSTRAP_DEFAULT = None                # psu-gray
BOOTSTRAP_DEFAULT_COMPLIMENT = None     # white

# Standard danger, warning, etc colors
BOOTSTRAP_DANGER = None                 # psu-red
BOOTSTRAP_DANGER_COMPLIMENT = None      # white
BOOTSTRAP_WARNING = None                # psu-orange (yellowish)
BOOTSTRAP_WARNING_COMPLIMENT = None     # psu-brown
BOOTSTRAP_INFO = None                   # psu-blue
BOOTSTRAP_INFO_COMPLIMENT = None        # white
BOOTSTRAP_SUCCESS = None                # psu-accent-green
BOOTSTRAP_SUCCESS_COMPLIMENT = None     # white

# ---- FONTS ----
HEADING_FONT = None
TEXT_FONT = None
CODE_FONT = None



