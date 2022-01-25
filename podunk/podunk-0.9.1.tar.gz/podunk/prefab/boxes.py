#------------------------------------------------------------------------------
#   file:       podunk/prefab/boxes.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.widget.box import Box
from podunk.prefab import color
from podunk.prefab import line

#---------------------------------------------------------------------Blank Box

BLANK_BOX = Box()

#-------------------------------------------------------------------Grey Square

GREY_SQUARE = Box()
GREY_SQUARE.left_border = 1
GREY_SQUARE.top_border = 1
GREY_SQUARE.right_border = 1
GREY_SQUARE.bottom_border = 1
GREY_SQUARE.background_color = color.LIGHT_GREY

#----------------------------------------------------------------------Thin Box

THIN_BOX = Box()
THIN_BOX.left_border = .25
THIN_BOX.top_border = .25
THIN_BOX.right_border = .25
THIN_BOX.bottom_border = .25

#-----------------------------------------------------------------Dotted Bottom

DOTTED_BOTTOM = Box()
DOTTED_BOTTOM.bottom_border = 1
DOTTED_BOTTOM.border_color = color.GREY
DOTTED_BOTTOM.border_style = line.DOTTED

