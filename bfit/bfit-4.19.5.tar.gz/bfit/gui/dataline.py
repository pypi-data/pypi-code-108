
from tkinter import *
from tkinter import ttk
from functools import partial

from bfit import logger_name
from bfit.gui.popup_prepare_data import popup_prepare_data
from bfit.backend.entry_color_set import on_focusout, on_entry_click
import bfit.backend.colors as colors

import numpy as np
import logging

# =========================================================================== #
class dataline(object):
    """
        A line of objects to display run properties and remove bins and whatnot.
        
        bdfit:          fitdata object 
        bfit:           pointer to root 
        bin_remove:     StringVar for specifying which bins to remove in 1f runs
        check:          Checkbox for selection (related to check_state)
        check_data:     BooleanVar for specifying to draw data
        check_fit:      BooleanVar for specifying to draw fit
        check_res:      BooleanVar for specifying to draw residual
        check_state:    BooleanVar for specifying check state
        draw_fit_checkbox: Checkbutton linked to check_fit
        draw_res_checkbox: Checkbutton linked to check_res
        id:             Str key for unique idenfication
        label:          StringVar for labelling runs in legends
        label_entry:    Entry object for labelling runs in legends
        line_frame:     Frame that object is placed in
        lines_list:     dictionary of datalines
        lines_list_old: dictionary of datalines
        mode:           bdata run mode
        rebin:          IntVar for SLR rebin
        row:            position in list
        run:            bdata run number
        year:           bdata year
    """
        
    bin_remove_starter_line = '24 100-200 (bins)'
    
    # ======================================================================= #
    def __init__(self, bfit, lines_list, lines_list_old, fetch_tab_frame, bdfit, row):
        """
            Inputs:
                fetch_tab_frame: parent in which to place line
                bdfit: fitdata object corresponding to the file which is placed here. 
                row: where to grid this object
        """
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing run %d (%d)', bdfit.run, bdfit.year)
    
        # variables
        self.bfit = bfit
        self.row = row
        
        # variables from fitdata object
        self.bdfit = bdfit
        bd = bdfit.bd
        
        self.bin_remove = bdfit.omit
        self.label = bdfit.label
        self.rebin = bdfit.rebin
        self.check_state = bdfit.check_state
        self.mode = bdfit.mode
        self.run =  bdfit.run
        self.year = bdfit.year
        self.lines_list = lines_list
        self.lines_list_old = lines_list_old
        self.id = bdfit.id
        self.bdfit.dataline = self
        
        self.check_data = bdfit.check_draw_data
        self.check_fit = bdfit.check_draw_fit
        self.check_res = bdfit.check_draw_res
        
        # build objects
        line_frame = Frame(fetch_tab_frame)
        line_frame.bind('<Enter>', self.on_line_enter)
        line_frame.bind('<Leave>', self.on_line_leave)
        
        label_label = ttk.Label(line_frame, text="Label:", pad=5)
        self.label_entry = Entry(line_frame, textvariable=self.label, \
                width=22)
                
        remove_button = ttk.Button(line_frame, text='Remove', \
                command=self.degrid, pad=1)
        draw_button = ttk.Button(line_frame, text='Draw', 
                                 command=lambda:self.draw(figstyle='data'), 
                                 pad=1)
        
        draw_data_checkbox = ttk.Checkbutton(line_frame, text='Data', 
                variable=self.check_data, onvalue=True, offvalue=False, pad=5, 
                command=self.do_check_data)
        
        self.draw_fit_checkbox = ttk.Checkbutton(line_frame, text='Fit', 
                variable=self.check_fit, onvalue=True, offvalue=False, pad=5, 
                state=DISABLED, command=self.do_check_fit)
        
        self.draw_res_checkbox = ttk.Checkbutton(line_frame, text='Res', 
                variable=self.check_res, onvalue=True, offvalue=False, pad=5, 
                state=DISABLED, command=self.do_check_res)
        
        rebin_label = ttk.Label(line_frame, text="Rebin:", pad=5)
        rebin_box = Spinbox(line_frame, from_=1, to=100, width=3, \
                            textvariable=self.rebin)
        self.rebin.set(self.bfit.fetch_files.check_rebin.get())
                
        self.check_state.set(bfit.fetch_files.check_state.get())
        self.check = ttk.Checkbutton(line_frame, variable=self.check_state, \
                onvalue=True, offvalue=False, pad=5)
         
        self.set_check_text()
        
        # add button for data prep
        button_prep_data = ttk.Button(line_frame, text='Prep Data', 
                                      command=lambda : popup_prepare_data(self.bfit, self.bdfit), 
                                      pad=1)
         
        # add grey text to label
        self.set_label()
                
        # grid
        c = 1
        self.check.grid(column=c, row=0, sticky=E); c+=1
        button_prep_data.grid(column=c, row=0, sticky=E); c+=1
        rebin_label.grid(column=c, row=0, sticky=E); c+=1
        rebin_box.grid(column=c, row=0, sticky=E); c+=1
        label_label.grid(column=c, row=0, sticky=E); c+=1
        self.label_entry.grid(column=c, row=0, sticky=E); c+=1
        draw_data_checkbox.grid(column=c, row=0, sticky=E); c+=1
        self.draw_fit_checkbox.grid(column=c, row=0, sticky=E); c+=1
        self.draw_res_checkbox.grid(column=c, row=0, sticky=E); c+=1
        draw_button.grid(column=c, row=0, sticky=E); c+=1
        remove_button.grid(column=c, row=0, sticky=E); c+=1
        
        # resizing
        fetch_tab_frame.grid_columnconfigure(0, weight=1)   # big frame
        for i in (3, 5, 7):
            line_frame.grid_columnconfigure(i, weight=100)    # input labels
        for i in (4, 6, 8):
            line_frame.grid_columnconfigure(i, weight=1)  # input fields
        
        # passing
        self.line_frame = line_frame
                
    # ======================================================================= #
    def __del__(self):
        
        # kill buttons and frame
        try:
            for child in self.line_frame.winfo_children():
                child.destroy()
        except Exception:
            pass
            
    # ======================================================================= #
    def grid(self, row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.line_frame.grid(column=0, row=row, columnspan=2, sticky=(W, N))
        self.line_frame.update_idletasks()
        self.bfit.data[self.id] = self.bdfit
        self.set_check_text()
        
    # ======================================================================= #
    def degrid(self):
        """Hide displayed dataline object from file selection. """
        
        self.logger.info('Degridding run %s', self.id)
        
        # degrid
        self.line_frame.grid_forget()
        self.line_frame.update_idletasks()
        
        self.lines_list_old[self.id] = self.lines_list[self.id]
        del self.lines_list[self.id]
        del self.bfit.data[self.id]
        
        # uncheck the fit
        self.check_fit.set(False)
        self.draw_fit_checkbox.config(state='disabled')
        
        # remove data from storage
        if len(self.lines_list) == 0:
            self.bfit.fetch_files.runmode_label['text'] = ''
            self.bfit.fit_files.pop_fitconstr.constraints_are_set = False
                
    # ======================================================================= #
    def do_check_data(self):
        """Prevent resdiuals and fit/data checks from being true at the same time"""
        
        # get residual check value
        status = self.check_data.get()
            
        # set residuals
        if str(self.draw_res_checkbox['state']) == 'normal' and status:
            self.check_res.set(False)
    
    # ======================================================================= #
    def do_check_fit(self):
        """Prevent resdiuals and fit/data checks from being true at the same time"""
        
        # get residual check value
        status = self.check_fit.get()
            
        # set residuals
        if status:
            self.check_res.set(False)
    
    # ======================================================================= #
    def do_check_res(self):
        """Prevent resdiuals and fit/data checks from being true at the same time"""
        
        # get residual check value
        status = self.check_res.get()
            
        # set data and fit
        self.check_data.set(not status)
        self.check_fit.set(not status)    
    
    # ======================================================================= #
    def draw(self, figstyle):
        """
            Draw single data file.
            
            figstyle: one of "data", "fit", or "param" to choose which figure 
                    to draw in
        """
        
        # draw data
        if self.check_data.get():
            self.logger.info('Draw run %d (%d)', self.run, self.year)
                    
            # get new data file
            data = self.bfit.data[self.bfit.get_run_key(self.bdfit.bd)]
            data.read()
            
            # get data file run type
            d = self.bfit.fetch_files.asym_type.get()
            d = self.bfit.asym_dict[d]
            
            # draw
            data.draw(d, figstyle=figstyle, label=self.label.get())
            
        # draw fit
        if self.check_fit.get():
            if self.check_data.get():
                mode = self.bfit.draw_style.get()
                self.bfit.draw_style.set('stack')
                self.bdfit.draw_fit(unique=False, 
                                    asym_mode=self.bfit.get_asym_mode(self.bfit.fetch_files), 
                                    figstyle=figstyle)
                self.bfit.draw_style.set(mode)
            else:
                self.bdfit.draw_fit(figstyle=figstyle, 
                                    asym_mode=self.bfit.get_asym_mode(self.bfit.fetch_files))
                
        # draw residual
        if self.check_res.get():
            self.bdfit.draw_residual(figstyle=figstyle, 
                                     rebin=self.rebin.get())

    # ======================================================================= #
    def set_check_text(self):
        """Update the string for the check state box"""
        
        bdfit = self.bdfit
        
        # temperature
        try:
            self.temperature = int(np.round(bdfit.temperature.mean))
        except (ValueError, AttributeError):
            self.temperature = np.nan
            
        # field (Tesla)
        if bdfit.field > 0.1:
            self.field = np.around(bdfit.field, 2)
            
            try:
                field_text = "%3.2fT"%self.field
            except TypeError:
                field_text = ' '
        else:
            self.field = np.round(bdfit.field*1e4)
            
            try:
                field_text = "%3.0fG"%self.field
            except TypeError:
                field_text = ' '
        
        # bias
        self.bias = self.bdfit.bias
        try:
            bias_text = "%4.2fkV"%self.bias
        except TypeError:
            bias_text = ' '
        
        # duration 
        try: 
            duration_text = "%02d:%02d" % divmod(self.bdfit.duration, 60)
        except AttributeError:
            duration_text = ' '
        
        # set the text    
        if '+' in bdfit.id:
            unique_id = '%s+' % bdfit.id.split('+')[0]
        else:
            unique_id = '%s,' % bdfit.id
        
        
        T = '%3dK' % self.temperature if not np.isnan(self.temperature) else 'nan'
        
        info_str = "%s %s, %s, %s, %s" %  (unique_id, 
                                             T, field_text, 
                                             bias_text, duration_text)
        self.check.config(text=info_str)
    
    # ======================================================================= #
    def set_label(self):
        """Set default label text"""
        
        # get default label
        try:
            label = self.bfit.get_label(self.bfit.data[self.id])
        except KeyError:
            return
        
        # clear old text
        self.label_entry.delete(0, 'end')
        
        # set
        self.label_entry.insert(0, label)
        
        # make function to clear and replace with default text
        entry_fn_lab = partial(on_entry_click, text=label, 
                               entry=self.label_entry)
        on_focusout_fn_lab = partial(on_focusout, text=label, 
                                 entry=self.label_entry)
                                 
        # bindings
        self.label_entry.bind('<FocusIn>', entry_fn_lab)
        self.label_entry.bind('<FocusOut>', on_focusout_fn_lab)
        self.label_entry.config(foreground=colors.entry_grey)
        
    # ======================================================================= #
    def on_line_enter(self, *args):
        """Make the dataline grey on mouseover"""
        self.line_frame.config(bg=colors.focusbackground)
    
    # ======================================================================= #
    def on_line_leave(self, *args):
        """Make the dataline black on stop mouseover"""
        self.line_frame.config(bg=colors.background)

    # ======================================================================= #
    def update_label(self):
        """Set label unless values are user-defined"""
        
        if str(self.label_entry.config()['foreground'][4]) == colors.entry_grey:
            self.set_label()
