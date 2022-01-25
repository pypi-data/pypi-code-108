#------------------------------------------------------------------------------
#   file:       podunk/project/report.py
#   author:     Jim Storch
#------------------------------------------------------------------------------

import datetime

from reportlab.pdfgen.canvas import Canvas

from podunk.prefab import alignment
from podunk.prefab import paper
from podunk.prefab.formats import format_report_date
from podunk.widget.field import Field


class Report(object):

    def __init__(self, pdf_file=None, page_format=paper.LETTER_PORTRAIT, date_format=format_report_date):

        self.pdf_file = pdf_file
        self.title = 'Untitled Report'
        self.author = 'rdempc-accountingsystem'
        self.subject = 'RDEMPC Generated Report'
        self.page_width, self.page_height = page_format

        self.left_margin = 54
        self.top_margin = 72
        self.right_margin = 54
        self.bottom_margin = 72
 
        ## Metrics        
        self._top_edge = self.page_height - 1
        self._right_edge = self.page_width - 1
        self._bottom_edge = 0
        self._left_edge = 0
        self._working_width = self.page_width - (
            self.right_margin + self.left_margin )
        self._working_height = self.page_height - (
            self.top_margin + self.bottom_margin )
         
        ## Create the ReportLab Canvas
        self.canvas = Canvas(self.pdf_file, pagesize = (self.page_width,
            self.page_height))

        ## Create the page header
        self.header = Field()
        self.header.box.bottom_border = 2
        self.header.box.line_cap = 1
        #self.header.box.border_color = (.6,.6,.6)        
        self.header.style.vertical_padding = 6
        self.header.style.bold = True
        self.header.style.size = 10
        #self.header.style.color = (.6,.6,.6)
        self.header.style.horizontal_alignment = alignment.RIGHT
        self.header.width = self._working_width

        ## Create the page footer
        self.footer = Field()
        self.footer.box.top_border = 1
        self.footer.box.line_cap = 1
        #self.footer.box.border_color = (.6,.6,.6)
        self.footer.style.horizontal_alignment = alignment.CENTER
        self.footer.style.vertical_alignment = alignment.TOP
        #self.footer.style.color = (.6,.6,.6)   
        self.footer.width = self._working_width
        self.footer.style.size = 8

        ## Create the date label
        self.date = Field(datetime.datetime.today())
        self.date.format = date_format
        self.date.style.vertical_alignment = alignment.TOP
        #self.date.style.color = (.6,.6,.6)
        #self.date.style.horizontal_padding = 0
        self.date.style.size = 8

        ## Create the page number label; 'Page X of'
        self.page_num = Field()
        self.page_num.style.horizontal_alignment = alignment.RIGHT
        self.page_num.style.vertical_alignment = alignment.TOP
        self.page_num.width = self._working_width - 13
        #self.page_num.style.color = (.6,.6,.6)
        self.page_num.horizontal_padding = 0
        self.page_num.style.size = 8

        ## Create the last page number label
        self.last_page = Field()
        #self.last_page.style.horizontal_alignment = alignment.LEFT
        self.last_page.style.vertical_alignment = alignment.TOP
        #self.last_page.width = self._working_width
        #self.last_page.style.color = (.6,.6,.6)
        self.last_page.horizontal_padding = 0
        self.last_page.style.size = 8

        ## Objects to be drawn
        self.draw_list = []

        self._page_count = 1
        self.with_footer = True

    #-----------------------------------------------------------------------Add

    def setWithFooter(self,foot_setter):
        self.with_footer = foot_setter
        
    def add(self, item):
        ## Add any object that, duck-typingly, has a 'draw_some' method
        self.draw_list.append(item)

    #--------------------------------------------------------------------Create

    def create(self):
        self.canvas.setAuthor(self.author)
        self.canvas.setTitle(self.title)
        self.canvas.setSubject(self.subject)
        self._draw_header()
        self._draw_footer()
        vspace = self._working_height
        left = self.left_margin   
        right = self.page_width - self.right_margin
        page_count = 1

        for item in self.draw_list:
           
            while True:

                if vspace < 1:
                    self._start_new_page()
                    vspace = self._working_height  

                yoff = self.bottom_margin + vspace
                used = item.draw_some(self.canvas, left, right, yoff, vspace)
                
                if used == 0:
                    break
                    page_count = page_count + 1

                else:
                    vspace -= used

        ## Add the numbering for last page
        ## We have to do this as a PDF 'Form' object since we don't know in
        ## advance how many pages there will be.

        
        self.canvas.beginForm('last_page')
        self.canvas.saveState()
        self.last_page.value = '%d' % self._page_count
        self.last_page.draw(self.canvas, 
            self._right_edge - ( self.right_margin + 14),
            self.bottom_margin * .65)
        self.canvas.restoreState()
        self.canvas.endForm()

        ## Close the PDF
        self.canvas.save()

    #----------------------------------------------------------------Start Page

    def _start_new_page(self):
        self._page_count += 1
        self.canvas.showPage()
        self._draw_header()
        self._draw_footer()

    #---------------------------------------------------------------Draw Header

    def _draw_header(self):
        self.header.value = self.title
        self.header.draw(self.canvas, self.left_margin, self._top_edge - 
            (self.top_margin * .65) )

    #---------------------------------------------------------------Draw Footer

    def _draw_footer(self):
        if self.with_footer or ( not self.with_footer and self._page_count > 1) :            
            self.footer.value = self.author
            self.footer.draw(self.canvas, self.left_margin, 
                self.bottom_margin * .65)
            self.date.draw(self.canvas, self.left_margin,
                self.bottom_margin * .65)
            self.page_num.value = 'Page %d of ' % self._page_count
            self.page_num.draw(self.canvas, self.left_margin,
                self.bottom_margin * .65)
            self.canvas.doForm('last_page') 

