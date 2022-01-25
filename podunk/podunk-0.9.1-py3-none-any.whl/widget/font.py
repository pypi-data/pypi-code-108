#------------------------------------------------------------------------------
#   file:       podunk/widget/font.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

import os
from reportlab.pdfbase import pdfmetrics

"""
This class is designed so that the report coder can treat built-in and embedded
fonts in exactly the same manner.  If you specify a path in the keyword dict
then it will load them from disk, otherwise it just holds names.
"""

class Font(object):

    def __init__(self, kwargs):

        self.plain = kwargs['plain']
        self.bold = kwargs['bold']
        self.italic = kwargs['italic']
        self.bold_italic = kwargs['bold_italic']

        if kwargs.__contains__('path'):

            path = kwargs['path']

            if path:
                self.embed_font(path, self.plain)
                self.embed_font(path, self.bold)
                self.embed_font(path, self.italic)
                self.embed_font(path, self.bold_italic)    

    #------------------------------------------------------------Embed Font

    def embed_font(self, path, face_name):
        """
        Register a font face with ReportLab an (if used) embed in the target PDF.
        """
        ## Based on snippet from http://www.reportlab.org/devfaq.html
        afm = os.path.join(path, face_name + '.afm')
        pfb = os.path.join(path, face_name + '.pfb')
        face = pdfmetrics.EmbeddedType1Face(afm, pfb)         
        pdfmetrics.registerTypeFace(face)
        font = pdfmetrics.Font(face_name, face_name, 'WinAnsiEncoding')
        pdfmetrics.registerFont(font)


