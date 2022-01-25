#------------------------------------------------------------------------------
#   file:       podunk/widget/box.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.prefab import color
from podunk.prefab import line

class Box(object):

    def __init__(self):

        self.left_border = 0
        self.top_border = 0
        self.right_border = 0
        self.bottom_border = 0
        self.border_color = color.BLACK
        self.border_style = line.SOLID
        self.background_color = None
        self.line_cap = 2

    #----------------------------------------------------------------------Draw

    def draw(self, canvas, x, y, width, height):

        canvas.saveState()

        ## draw the background rectangle
        if self.background_color != None:
            canvas.setFillColor(self.background_color)
            canvas.rect(x,y, width, height, fill=1, stroke=0)

        ## draw the borders
        canvas.setStrokeColor(self.border_color)
        canvas.setDash(self.border_style)
        canvas.setLineCap(self.line_cap)

        ## Left border
        if self.left_border:
            canvas.setLineWidth(self.left_border)
            canvas.line(x,y,x,y+height)

        ## Top border
        if self.top_border:
            canvas.setLineWidth(self.top_border)
            canvas.line(x,y+height,x+width,y+height)

        ## Right border
        if self.right_border:
            canvas.setLineWidth(self.right_border)
            canvas.line(x+width,y,x+width,y+height)
        
        ## Bottom border
        if self.bottom_border:
            canvas.setLineWidth(self.bottom_border)
            canvas.line(x,y,x+width,y)
        
        canvas.restoreState()       


