#------------------------------------------------------------------------------
#   file:       podunk/widget/table.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

from podunk.widget.column import Column

class Table(object):

    def __init__(self):

        self.column_names = []
        self.column_list = []
        self.column_dict = {}
        self.row_padding = 0
        self.column_padding = 4

        ## Used when drawing
        self._drew_header = False
        self._current_row = 0
        self._drew_footer = False

    #----------------------------------------------------------------Add Column

    def add_column(self, name, width=None):
        column = Column(name, width)
        self.column_names.append(name)
        self.column_list.append(column)
        self.column_dict[name] = column
        return column

    #----------------------------------------------------------Get Header Field

    def get_header_field(self, column_name):
        """
        Return the header field object.
        Convenience method if you need to make a lot of tweaks.
        """
        return self.column_dict[column_name].header

    #------------------------------------------------------------Get Data Field

    def get_row_field(self, column_name):
        """
        Return the data field object.
        Convenience method if you need to make a lot of tweaks.
        """
        return self.column_dict[column_name].row

    #----------------------------------------------------------Get Footer Field

    def get_footer_field(self, column_name):
        """
        Return the footer field object.
        Convenience method if you need to make a lot of tweaks.
        """
        return self.column_dict[column_name].footer

    #-------------------------------------------------------------------Add Row

    def add_row(self, values):
        """
        Add a list of data values.  The list added must match the types and
        number of columns in the table.
        """
        for index in range(len(values)):
            self.column_dict[self.column_names[index]].append(values[index])

    #------------------------------------------------------------------Add Dict

    def add_dict(self, kwargs):
        """
        Add a dictionary of {column_name:value} pairs.  You may omit colmuns,
        which will be filled with values of None.
        """

        keys = kwargs.keys()

        ## Insert passed values
        for key in keys:
            self.column_dict[key].append(kwargs[key])

        ## Insert blanks for omitted columns
        for column_name in self.column_names:
            if column_name not in keys:
                self.column_dict[column_name].append(None)

    #--------------------------------------------------------------Count Column

    def count_column(self, column_name):
        column = self.column_dict[column_name]
        count = 0
        for value in column.value_list:  
            if value != None:
                count += 1
        column.footer.value = 'Count: %d' % count

    #----------------------------------------------------------------Sum Column

    def sum_column(self, column_name):
        column = self.column_dict[column_name]
        sum = 0
        for value in column.value_list:  
            if value != None:
                sum += float(value)
        #column.footer.value = 'Sum: %.2f' % sum
        column.footer.value = "{:,.2f} ".format(sum)
        
            
    #------------------------------------------------------------Average Column

    def average_column(self, column_name):
        column = self.column_dict[column_name]
        sum = 0
        count = 0
        for value in column.value_list:  
            if value != None:
                sum += float(value)
                count += 1
        column.footer.value = 'Avg: %.2f' % (sum / count)

    #-------------------------------------------------------------Get Row Count
    
    def get_row_count(self):
        return len(self.column_list[0].value_list)

    #-----------------------------------------------------------------Auto Size

    def auto_width(self, canvas):
        for column in self.column_list:
            column.auto_width(canvas)
 
    #-----------------------------------------------------------------Auto Grow

    def auto_grow(self, canvas, width):
        padding = (len(self.column_names) -1 ) * self.column_padding
        w = float(width - padding)
        self.auto_width(canvas)
        mult = w / ( self.total_width() - padding)
        for column in self.column_list:
            column.width *= mult
        #print self.total_width()      

    #---------------------------------------------------------------Total Width

    def total_width(self):
        width = 0
        for column in self.column_list:
            width += column.width + self.column_padding
        return width - self.column_padding
      
    #-----------------------------------------------------------------Draw Some

    def draw_some(self, canvas, left, right, yoff, vspace):
            
        ## Draws one line at a time, returning the amount of vertical space
        ## consumed. Returns zero when all drawing is complete.

        xoff = ((right + left ) / 2 ) - (self.total_width() / 2 )

        ## Do we need a header?
        if not self._drew_header:

            ## If there's enough room, draw one
            
            if len(self.column_list) > 0:
                height = self.column_list[0].header.height
            else:
                height = 0
            if height < vspace:
                self._draw_header(canvas, xoff, yoff)
                self._drew_header = True
                used = height + self.row_padding


            ## Otherwise, return vspace and force a new page
            else:
                used = vspace  
                   
        ## Do we need a row?
        elif self._current_row < self.get_row_count():
            height = self.column_list[0].row.height
            if height < vspace:
                self._draw_row(canvas, xoff, yoff, self._current_row )
                self._current_row += 1
                used = height + self.row_padding
               
            else:
                used = vspace
                ## Queue up a new header too
                self._drew_header = False

        ## Do we need a footer?
        elif not self._drew_footer:

            ## If there's enough room, draw one
            height = self.column_list[0].footer.height 
            if height < vspace:
                self._draw_footer(canvas, xoff, yoff)
                self._drew_footer = True
                used = height + self.row_padding

            else:
                used = vspace            

        ## Otherwise we must be done
        else:
           used = 0

        return used
            
    #---------------------------------------------------------------Draw Header

    def _draw_header(self, canvas, xoff, yoff):
        for column in self.column_list:
            column.draw_header(canvas, xoff, yoff)
            xoff += column.width + self.column_padding

    #---------------------------------------------------------------Draw Header

    def _draw_row(self, canvas, xoff, yoff, row_number):
        for column in self.column_list:
            column.draw_row(canvas, xoff, yoff, row_number)
            xoff += column.width + self.column_padding

    #---------------------------------------------------------------Draw Footer

    def _draw_footer(self, canvas, xoff, yoff):
        for column in self.column_list:
            column.draw_footer(canvas, xoff, yoff)
            xoff += column.width + self.column_padding
                   



