#------------------------------------------------------------------------------
#   file:       podunk/widget/heading.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.widget.field import Field
from podunk.prefab.formats import format_title
from podunk.prefab import alignment

class Heading(object):

    def __init__(self, value):
    
        self.field = Field(value)
        self.field.style.vertical_padding = 2
        self.field.style.bold = True
        self.field.style.size = 9
        self.field.style.horizontal_alignment = alignment.CENTER
        self.skip = 10
        self._drew_skip = False
        self._drew_title = False

    #-----------------------------------------------------------------Draw Some

    def draw_some(self, canvas, left, right, yoff, vspace):

        if not self._drew_skip:
            height = self.skip
            if height < vspace:
                used = height
            else:
                used = vspace
            self._drew_skip = True


        elif not self._drew_title:
            height = self.field.get_height()
            ## Is there enought room for the title?
            if height < vspace:
                self.field.width = right - left
                self.field.draw(canvas, left, yoff)
                self._drew_title = True
                used = height

            ## If not, force a new page
            else:
                used = vspace
                
        ## We're done            
        else:
            used = 0

        return used

