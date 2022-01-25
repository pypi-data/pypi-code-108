#------------------------------------------------------------------------------
#   file:       podunk/prefab/fonts.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.widget.font import Font

#---------------------------------------------------------------------Helvetica

font_info = {
    'plain':'Helvetica',         
    'bold':'Helvetica-Bold',
    'italic':'Helvetica-Oblique',
    'bold_italic':'Helvetica-BoldOblique',
    }

HELVETICA = Font(font_info)

#-----------------------------------------------------------------------Courier

font_info = {
    'plain':'Courier',         
    'bold':'Courier-Bold',
    'italic':'Courier-Oblique',
    'bold_italic':'Courier-BoldOblique',
    }

COURIER = Font(font_info)

#-------------------------------------------------------------------Times Roman

font_info = {
    'plain':'Times-Roman',         
    'bold':'Times-Bold',
    'italic':'Times-Italic',
    'bold_italic':'Times-BoldItalic',
    }

TIMES_ROMAN = Font(font_info)

#-----------------------------------------------------------------------Gentium
# Copyright (c) SIL International, 2003-2008.
# See included zip file for Gentium's licensing information

font_info = {
    'plain':'GentiumBasic',         
    'bold':'GentiumBasic-Bold',
    'italic':'GentiumBasic-Italic',
    'bold_italic':'GentiumBasic-BoldItalic',
    'path':'podunk/media/fonts/Gentium',
    }

GENTIUM = Font(font_info)

#-------------------------------------------------------------Deja Vu Sans Mono
# Copyright (c) 2003 by Bitstream
# See included tar file for DejaVu Sans Mono licensing information

font_info = {
    'plain':'DejaVuSansMono',         
    'bold':'DejaVuSansMono-Bold',
    'italic':'DejaVuSansMono-Oblique',
    'bold_italic':'DejaVuSansMono-BoldOblique',
    'path':'podunk/media/fonts/DejaVuSansMono',
    }

DEJAVU_SANS_MONO = Font(font_info)


