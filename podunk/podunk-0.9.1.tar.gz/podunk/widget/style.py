#------------------------------------------------------------------------------
#   file:       podunk/widget/style.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.prefab import color
from podunk.prefab import alignment
from podunk.prefab.fonts import HELVETICA

class Style(object):

    def __init__(self):

        self.font = HELVETICA
        self.bold = False
        self.italic = False
        self.size = 7
        self.horizontal_padding = 2
        self.vertical_padding = 3
        self.color = color.BLACK
        self.horizontal_alignment = alignment.LEFT
        self.vertical_alignment = alignment.BOTTOM

    #------------------------------------------------------------------Get Face

    def get_face(self):
        """
        Return the name of the current font, including bold/italic variants.
        """
        if self.bold and self.italic:
            face = self.font.bold_italic
        elif self.bold and not self.italic:
            face = self.font.bold
        elif not self.bold and self.italic:
            face = self.font.italic        
        else:
            face = self.font.plain
        return face
    
    #-----------------------------------------------------------------Get Width

    def get_width(self, canvas, text):
        """
        Return the width of a given string at current font face/size.
        Includes padding on the left and right.
        """
        face = self.get_face()
        return canvas.stringWidth(text, face, self.size) + (
            self.horizontal_padding * 2)

    #----------------------------------------------------------------Get Height

    def get_height(self):
        """
        Return the height of a given string at current font size.
        Includes padding for the top and bottom.
        """     
        return self.size + (self.vertical_padding * 2)

    #------------------------------------------------------------Get Dimensions

    def get_dimensions(self, canvas, text):
        """
        Return the width and height of the given text at current font size.
        Includes padding on all sides.
        """
        width = self.get_width(canvas, text)
        height = self.get_height(text)
        return width,height

    #----------------------------------------------------------------------Draw

    def draw(self, canvas, text, x, y, width, height):
        
        canvas.saveState()
        face = self.get_face()

        ## Set the font characteristics      
        canvas.setFont(self.get_face(), self.size)
        canvas.setFillColor(self.color)

        ## Get the vertical alignment       
        if self.vertical_alignment == alignment.BOTTOM:
            y_off = y + self.vertical_padding

        elif self.vertical_alignment == alignment.TOP:
            y_off = ( y + height ) - ( self.vertical_padding + self.size)

        else: ## alignment.CENTERED
            y_off = y + ( ( height / 2 ) - ( self.size / 2 ) )

        ## Now the horizontal
        if self.horizontal_alignment == alignment.RIGHT:
            x_off = ( x + width ) - self.horizontal_padding
            canvas.drawRightString(x_off, y_off, text)

        elif self.horizontal_alignment == alignment.LEFT:
            x_off = x + self.horizontal_padding
            canvas.drawString(x_off, y_off, text)
        elif self.horizontal_alignment == alignment.ALIGNED:
            x_off = (x + width ) -  (self.horizontal_padding + 12)
            canvas.drawAlignedString(x_off,y_off,text, pivotChar='.')
        else: ## alignment.CENTERED
            x_off = x + ( width / 2)
            canvas.drawCentredString(x_off, y_off, text)      

        canvas.restoreState()
