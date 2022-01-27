# Terminal access
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import logging, os, sys
import matplotlib.pyplot as plt
import numpy as np

# ========================================================================== #
class popup_terminal(object):
    """
        Popup window for python interpreter access. 
    """

    # ====================================================================== #
    def __init__(self, bfit):
        self.bfit = bfit
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Run Python Commands')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon
        self.bfit.set_icon(self.win)
        
        # Key bindings
        self.win.bind('<Control-Key-Return>', self.do_run)             
        self.win.bind('<Control-Key-KP_Enter>', self.do_run)
        
        # text input 
        self.text = Text(frame, width=80, height=20, state='normal')
        instructions = ttk.Label(frame, text="Press ctrl+enter to execute "+\
                                 "text at and below cursor position.")
        
        # scrollbar
        scrollb = Scrollbar(frame, command=self.text.yview)
        self.text['yscrollcommand'] = scrollb.set
        
        # gridding
        frame.grid(row=0, column=0)
        instructions.grid(column=0, row=0, sticky=(E, W), pady=5)
        self.text.grid(row=1, column=0)
        scrollb.grid(row=1, column=1, sticky='nsew')
        
        # grid frame
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def do_run(self, event):
        """
            Run python commands
        """
        # toplevel access
        bfit = self.bfit
        
        # remove newline
        if event.keysym == 'Return':
            self.text.delete('insert-1c')
        
        # get full text at and after cursor
        line_num = '%d.0' % int(float(self.text.index(INSERT)))
        lines = self.text.get(line_num, END)
        
        # run commands
        self.logger.info('Commands run: "%s"'% ('", "'.join(lines.split('\n')[:-1])))
        
        exec(lines)
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
