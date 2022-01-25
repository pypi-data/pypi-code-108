#------------------------------------------------------------------------------
#   file:       podunk/prefab/styles.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.widget.style import Style
from podunk.prefab import color
from podunk.prefab import alignment

#-------------------------------------------------------------------------Money

from podunk.prefab.fonts import DEJAVU_SANS_MONO
MONEY = Style()
MONEY.font = DEJAVU_SANS_MONO
MONEY.horizontal_alignment = alignment.RIGHT


