# fetch_files tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from bfit import logger_name
from bdata import bdata, bmerged
from functools import partial
from bfit.backend.fitdata import fitdata
from bfit.backend.entry_color_set import on_focusout, on_entry_click
import bfit.backend.colors as colors
from bfit.global_variables import KEYVARS
from bfit.gui.dataline import dataline
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime, os, logging, glob, re

__doc__="""
    """

# =========================================================================== #
class fetch_files(object):
    """
        Data fields:
            
            asym_type: StringVar, drawing style
            bfit: pointer to parent class
            base_bins = IntVar, number of bins to use as baseline on scan ends
            canvas_frame_id: id number of frame in canvas
            check_rebin: IntVar for handling rebin aspect of checkall
            check_bin_remove: StringVar for handing omission of 1F data
            check_state: BooleanVar for handling check all
            check_state_data: BooleanVar for handling check_all_data
            check_state_fit: BooleanVar for handling check_all_fit
            check_state_res: BooleanVar for handling check_all_res
            data_canvas: canvas object allowing for scrolling 
            dataline_frame: frame holding all the data lines. Exists as a window
                in the data_canvas
            data_lines: dictionary of dataline obj, keyed by run number
            data_lines_old: dictionary of removed dataline obj, keyed by run number
            entry_asym_type: combobox for asym calc and draw type
            entry_run: entry to put in run number string
            fet_entry_frame: frame of fetch tab
            filter_opt: StringVar, holds state of filter radio buttons
            listbox_history: listbox for run input history
            max_number_fetched: max number of files you can fetch
            omit_state: BooleanVar, if true set omit all final incomplete scans
            run: StringVar input to fetch runs.
            runmode_label: display run mode
            runmode: display run mode list of strings
            text_filter: Text box for filter commands input
            year: IntVar of year to fetch runs from 
    """
    
    runmode_relabel = {'20':'SLR (20)', 
                       '1f':'Frequency Scan (1f/1x)', 
                       '1x':'Frequency Scan (1f/1x)', 
                       '1w':'Frequency Comb (1w)', 
                       '2e':'Random Freq. (2e)', 
                       '1n':'Rb Cell Scan (1n)', 
                       '1e':'Field Scan (1e)', 
                       '2h':'Alpha Tagged (2h)'}
                       
    equivalent_modes = [['1f', '1x'], ['20', '2h']]
                       
    run_number_starter_line = '40001 40002+40003 40005-40010 (run numbers)'
    bin_remove_starter_line = '24 100-200 (bins)'
    max_number_fetched = 500
    nhistory = 10
    
    # ======================================================================= #
    def __init__(self, fetch_data_tab, bfit):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')
    
        # initialize
        self.bfit = bfit
        self.data_lines = {}
        self.data_lines_old = {}
        self.fit_input_tabs = {}
        self.check_rebin = IntVar()
        self.check_bin_remove = StringVar()
        self.check_state = BooleanVar()
        self.fetch_data_tab = fetch_data_tab
        
        # Frame for specifying files -----------------------------------------
        fet_entry_frame = ttk.Labelframe(fetch_data_tab, text='Specify Files')
        self.year = IntVar()
        self.run = StringVar()
        
        self.year.set(self.bfit.get_latest_year())
        
        entry_year = Spinbox(fet_entry_frame, textvariable=self.year, width=5, 
                             from_=2000, to=datetime.datetime.today().year)
        entry_run = Entry(fet_entry_frame, textvariable=self.run, width=85)
        entry_run.insert(0, self.run_number_starter_line)
        entry_run.config(foreground=colors.entry_grey)
        
        # history list
        self.listbox_history = Listbox(fetch_data_tab, selectmode=SINGLE)
        entry_fn = partial(on_entry_click, text=self.run_number_starter_line, \
                            entry=entry_run)
        on_focusout_fn = partial(on_focusout, text=self.run_number_starter_line, \
                            entry=entry_run)
        entry_run.bind('<FocusIn>', entry_fn)
        entry_run.bind('<FocusOut>', on_focusout_fn)
        entry_run.bind('<Leave>', lambda event: self.history_hide(event, 'entry'))
        
        entry_run.bind('<Enter>', self.history_show)
        self.listbox_history.bind('<Leave>', lambda event: self.history_hide(event, 'history'))
        self.listbox_history.bind("<<ListboxSelect>>", self.history_set)
        
        # fetch button
        fetch = ttk.Button(fet_entry_frame, text='Fetch', command=self.get_data)
        update = ttk.Button(fet_entry_frame, text='Update', command=self.update_data)
        
        # grid and labels
        fet_entry_frame.grid(column=0, row=0, sticky=(N, W, E), columnspan=2, padx=5, pady=5)
        ttk.Label(fet_entry_frame, text="Year:").grid(column=0, row=0, sticky=W)
        entry_year.grid(column=1, row=0, sticky=(W))
        ttk.Label(fet_entry_frame, text="Run Number:").grid(column=2, row=0, sticky=W)
        entry_run.grid(column=3, row=0, sticky=W)
        fetch.grid(column=4, row=0, sticky=E)
        update.grid(column=5, row=0, sticky=E)
        self.listbox_history.grid(column=3, row=1, sticky=W)
        
        # padding 
        for child in fet_entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
        self.listbox_history.grid_forget()
        
        # Frame for run mode -------------------------------------------------
        runmode_label_frame = ttk.Labelframe(fetch_data_tab, pad=(10, 5, 10, 5), \
                text='Run Mode', )
        
        self.runmode_label = ttk.Label(runmode_label_frame, text="", justify=CENTER)
        
        # Scrolling frame to hold datalines
        yscrollbar = ttk.Scrollbar(fetch_data_tab, orient=VERTICAL)         
        self.data_canvas = Canvas(fetch_data_tab, bd=0,              # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000), confine=True)       # default size
        yscrollbar.config(command=self.data_canvas.yview)           # scroll command send
        dataline_frame = ttk.Frame(self.data_canvas, pad=5)          # holds 
        
        self.canvas_frame_id = self.data_canvas.create_window((0, 0),    # make window which can scroll
                window=dataline_frame, 
                anchor='nw')
        dataline_frame.bind("<Configure>", self.config_canvas) # bind resize to alter scrollable region
        self.data_canvas.bind("<Configure>", self.config_dataline_frame) # bind resize to change size of contained frame
        
        # Frame to hold everything on the right ------------------------------
        bigright_frame = ttk.Frame(fetch_data_tab, pad=5)
        
        # asymmetry calculation
        style_frame = ttk.Labelframe(bigright_frame, text='Asymmetry Calculation', \
                pad=5)
        self.asym_type = StringVar()
        self.asym_type.set('')
        self.entry_asym_type = ttk.Combobox(style_frame, \
                textvariable=self.asym_type, state='readonly', \
                width=20)
        self.entry_asym_type['values'] = ()
        
        style_frame.grid(column=0, row=0, sticky=(W, N, E))
        style_frame.grid_columnconfigure(0, weight=1)
        self.entry_asym_type.grid(column=0, row=0, sticky=(N, E, W), padx=10)
        
        # Frame for group set options ----------------------------------------
        right_frame = ttk.Labelframe(bigright_frame, \
                text='Operations on Active Items', pad=15)
        
        check_remove = ttk.Button(right_frame, text='Remove', \
                command=self.remove_all, pad=5)
        check_draw = ttk.Button(right_frame, text='Draw', \
                command=lambda:self.draw_all('data'), pad=5)
        
        
        # Scan repair options ------------------------------------------------
        frame_scan = ttk.Labelframe(right_frame, \
                text='Scan Repair Options', pad=5)
        
        check_rebin_label = ttk.Label(frame_scan, text="Rebin:", pad=5)
        check_rebin_box = Spinbox(frame_scan, from_=1, to=100, width=3, \
                textvariable=self.check_rebin, 
                command=lambda: self.set_all('rebin'))
        
        check_bin_remove_label = ttk.Label(frame_scan, text="Remove:", pad=5)
        check_bin_remove_entry = Entry(frame_scan, \
                textvariable=self.check_bin_remove, width=20)
        
        self.omit_state = BooleanVar()
        omit_checkbox = ttk.Checkbutton(frame_scan, 
                text='Omit incomplete final scan', variable=self.omit_state, 
                onvalue=True, offvalue=False, pad=5, 
                command=lambda: self.set_all('omit_scan'))
        self.omit_state.set(False)
        
        self.base_bins = IntVar()
        base_label = ttk.Label(frame_scan, text="baseline bins", pad=5)
        base_spinbox = Spinbox(frame_scan, from_=0, to=1000, width=4, \
                               textvariable=self.base_bins, 
                               command=lambda: self.set_all('base_bins'))
        self.base_bins.set(0)
        
        # grid
        check_rebin_label.grid(     column=0, row=0, sticky='e')
        check_rebin_box.grid(       column=1, row=0, sticky='w')
        check_bin_remove_label.grid(column=0, row=1, sticky='e')
        check_bin_remove_entry.grid(column=1, row=1, sticky='w', columnspan=2)
        omit_checkbox.grid(column=0, row=2, sticky='w', columnspan=2)
        base_spinbox.grid(column=0, row=3, sticky='e')
        base_label.grid(column=1, row=3, sticky='w')
        
        # key bindings
        check_bin_remove_entry.bind('<KeyRelease>', lambda x: self.set_all('omit'))
        check_rebin_box.bind('<KeyRelease>', lambda x: self.set_all('rebin'))
        base_spinbox.bind('<KeyRelease>', lambda x: self.set_all('base_bins'))
        
        # checkboxes
        right_checkbox_frame = ttk.Frame(right_frame)
        
        check_all_box = ttk.Checkbutton(right_checkbox_frame, 
                text='State', variable=self.check_state, 
                onvalue=True, offvalue=False, pad=5, command=self.check_all)
        self.check_state.set(True)
        
        self.check_state_data = BooleanVar()        
        check_data_box = ttk.Checkbutton(right_checkbox_frame, 
                text='Data', variable=self.check_state_data, 
                onvalue=True, offvalue=False, pad=5, command=self.check_all_data)
        self.check_state_data.set(True)
        
        self.check_state_fit = BooleanVar()        
        check_fit_box = ttk.Checkbutton(right_checkbox_frame, 
                text='Fit', variable=self.check_state_fit, 
                onvalue=True, offvalue=False, pad=5, command=self.check_all_fit)
        
        self.check_state_res = BooleanVar()        
        check_res_box = ttk.Checkbutton(right_checkbox_frame, 
                text='Res', variable=self.check_state_res, 
                onvalue=True, offvalue=False, pad=5, command=self.check_all_res)
                
        check_toggle_button = ttk.Button(right_frame, \
                text='Toggle All Check States', command=self.toggle_all, pad=5)
        
        # add grey to check_bin_remove_entry
        check_bin_remove_entry.insert(0, self.bin_remove_starter_line)
        
        check_entry_fn = partial(on_entry_click, \
                text=self.bin_remove_starter_line, \
                entry=check_bin_remove_entry)
        
        check_on_focusout_fn = partial(on_focusout, \
                text=self.bin_remove_starter_line, \
                entry=check_bin_remove_entry)
        
        check_bin_remove_entry.bind('<FocusIn>', check_entry_fn)
        check_bin_remove_entry.bind('<FocusOut>', check_on_focusout_fn)
        check_bin_remove_entry.config(foreground=colors.entry_grey)
                    
        # grid
        runmode_label_frame.grid(column=2, row=0, sticky=(N, W, E, S), pady=5, padx=5)
        self.runmode_label.grid(column=0, row=0, sticky=(N, W, E))
        
        bigright_frame.grid(column=2, row=1, rowspan=2, sticky='new')
        
        self.data_canvas.grid(column=0, row=1, sticky=(E, W, S, N), padx=5, pady=5)
        yscrollbar.grid(column=1, row=1, sticky=(W, S, N), pady=5)
        
        check_all_box.grid(        column=0, row=0, sticky=(N))
        check_data_box.grid(        column=1, row=0, sticky=(N))
        check_fit_box.grid(         column=2, row=0, sticky=(N))
        check_res_box.grid(         column=3, row=0, sticky=(N)) 
        
        right_frame.grid(           column=0, row=1, sticky=(N, E, W), pady=5)
        r = 0
        right_checkbox_frame.grid(  column=0, row=r, sticky=(N), columnspan=2); r+= 1
        check_toggle_button.grid(   column=0, row=r, sticky=(N, E, W), columnspan=2, pady=1, padx=5); r+= 1
        check_draw.grid(            column=0, row=r, sticky=(N, W, E), pady=5, padx=5);
        check_remove.grid(          column=1, row=r, sticky=(N, E, W), pady=5, padx=5); r+= 1
        frame_scan.grid(            column=0, row=r, sticky=(N, E, W), pady=5, padx=5, columnspan=2); r+= 1        
        
        # filtering -----------------------------------------------------------
        frame_filter = ttk.Labelframe(bigright_frame, text='Filter Runs', pad=5)
        button_filter_instr = ttk.Button(frame_filter, text='Instructions', 
                                         command=self.show_filter_instructions)
        self.text_filter = Text(frame_filter, width=35, height=5, state='normal', 
                                wrap='none')
        
        frame_filter_button = ttk.Frame(frame_filter, pad=5)
        button_filter = ttk.Button(frame_filter_button, text='Filter', 
                                         command=self.filter_runs)
        self.filter_opt = StringVar()
        self.filter_opt.set('activate')
        radio_filter_activate = ttk.Radiobutton(frame_filter_button, 
                                       variable=self.filter_opt, 
                                       value='activate',
                                       text='By deactivation',
                                       )
        radio_filter_remove = ttk.Radiobutton(frame_filter_button, 
                                       variable=self.filter_opt, 
                                       value='remove',
                                       text='By removal',
                                       )
        
        button_filter.grid(column=0, row=0, rowspan=2, sticky='w', padx=5)
        radio_filter_activate.grid(column=1, row=0, sticky='w', padx=5)
        radio_filter_remove.grid(column=1, row=1, sticky='w', padx=5)
        
        # final grid
        frame_filter.grid(column=0, row=2, sticky='new', pady=5)
        r = 0
        button_filter_instr.grid(column=0, row=r, sticky='new', pady=5); r+= 1
        self.text_filter.grid(column=0, row=r, sticky='new', pady=5); r+= 1
        frame_filter_button.grid(column=0, row=r, sticky='new', pady=5); r+= 1
        
        # resizing
        fetch_data_tab.grid_columnconfigure(0, weight=1)        # main area
        fetch_data_tab.grid_rowconfigure(1, weight=1)            # main area
        
        for i in range(3):
            if i%2 == 0:    fet_entry_frame.grid_columnconfigure(i, weight=2)
        fet_entry_frame.grid_columnconfigure(3, weight=1)
            
        self.data_canvas.grid_columnconfigure(0, weight=1)    # fetch frame 
        self.data_canvas.grid_rowconfigure(0, weight=1)
            
        # passing
        self.entry_run = entry_run
        self.entry_year = entry_year
        self.check_rebin_box = check_rebin_box
        self.check_bin_remove_entry = check_bin_remove_entry
        self.check_all_box = check_all_box
        self.dataline_frame = dataline_frame

        self.logger.debug('Initialization success.')
    
    # ======================================================================= #
    def __del__(self):
        
        # delete lists and dictionaries
        if hasattr(self, 'data_lines'):      del self.data_lines
        if hasattr(self, 'data_lines_old'):  del self.data_lines_old
        
        # kill buttons and frame
        try:
            for child in self.fetch_data_tab.winfo_children():
                child.destroy()
            self.fetch_data_tab.destroy()
        except Exception:
            pass
        
    # ======================================================================= #
    def _check_condition(self, data, string):
        """Check whether a run satisfies the condition given as a string"""
        
        # determine what variable is being tested
        keyvars = np.array(list(KEYVARS.keys()))
        keylens = [len(k) for k in keyvars]
        keyvars = keyvars[np.argsort(keylens)[::-1]]
        
        found = False
        for key in keyvars:
            if key in string:
                found = True
                break
        
        if not found:
            msg = 'Variable not recognized in "%s"' % string
            messagebox.showerror('Filter', msg)
            raise RuntimeError(msg)
        
        # replace key with value
        val, err = data.get_values(KEYVARS[key])
        string = string.replace(key, str(val))
        
        # check for nan
        if 'nan' in string:
            string = string.replace('nan', 'np.nan')
        
        # evaluate
        return eval(string)
    
    # ======================================================================= #
    def _do_check_all(self, state, var, box):
        """
            Force all tickboxes of a given type to be in a given state, assuming 
            the tickbox is active
        """
        
        self.logger.info('Changing state of all %s tickboxes to %s', var, state)
        for dline in self.data_lines.values():
            
            # check if line is selected
            if not dline.check_state.get() and var != 'check_state':
                continue
            
            # check if tickbox is object variable
            if hasattr(dline, box):
                
                # check if tickbox is disabled
                if str(getattr(dline, box)['state']) == 'disabled':
                    continue
                    
            # set value
            getattr(dline, var).set(state)
            
            # run check for other items
            if hasattr(dline, 'do_'+var):
                getattr(dline, 'do_'+var)()
    
    # ======================================================================= #
    def canvas_scroll(self, event):
        """Scroll canvas with files selected."""
        if event.num == 4:
            self.data_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.data_canvas.yview_scroll(1, "units")
    
    # ======================================================================= #
    def check_all(self):  
        self._do_check_all(self.check_state.get(), 'check_state', 'None')
        
    def check_all_data(self):  
        self._do_check_all(self.check_state_data.get(), 'check_data', 'None')
        
    def check_all_fit(self):  
        self._do_check_all(self.check_state_fit.get(), 'check_fit', 'draw_fit_checkbox')
    
    def check_all_res(self):  
        self._do_check_all(self.check_state_res.get(), 'check_res', 'draw_res_checkbox')    
        
    # ======================================================================= #
    def config_canvas(self, event):
        """Alter scrollable region based on canvas bounding box size. 
        (changes scrollbar properties)"""
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))
    
    # ======================================================================= #
    def config_dataline_frame(self, event):
        """Alter size of contained frame in canvas. Allows for inside window to 
        be resized with mouse drag""" 
        self.data_canvas.itemconfig(self.canvas_frame_id, width=event.width)
        
    # ======================================================================= #
    def draw_all(self, figstyle, ignore_check=False):
        """
            Draw all data in data lines
            
            figstyle: one of "data", "fit", or "param" to choose which figure 
                    to draw in
            ignore_check: draw all with no regard to whether the run has been 
                    selected
        """
        
        self.logger.debug('Drawing all data (ignore check: %s)', ignore_check)
        
        # condense drawing into a funtion
        def draw_lines():
            for k, line in self.data_lines.items():
                if line.check_state.get() or ignore_check:
                    line.draw(figstyle)
                
        # get draw style
        style = self.bfit.draw_style.get()
        self.logger.debug('Draw style: "%s"',  style)
        
        # make new figure, draw stacked
        if style == 'stack':
            draw_lines()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            self.bfit.draw_style.set('stack')
            
            if self.bfit.plt.plots[figstyle]:
                self.bfit.plt.clf(figstyle)
            
            draw_lines()
            self.bfit.draw_style.set('redraw')
            
        # make new figure, draw single
        elif style == 'new':
            self.bfit.draw_style.set('stack')
            self.bfit.plt.figure(figstyle)
            draw_lines()
            self.bfit.draw_style.set('new')
        else:
            s = "Draw style not recognized"
            messagebox.showerror(message=s)
            self.logger.error(s)
            raise ValueError(s)
    
        # remove legned if too many drawn values
        n_selected = sum([d.check_state.get() for d in self.data_lines.values()])
        if n_selected > self.bfit.legend_max_draw:
            
            try:
                self.bfit.plt.gca(figstyle).get_legend().remove()
            except AttributeError:
                pass
            else:
                self.bfit.plt.tight_layout(figstyle)
        
    # ======================================================================= #
    def export(self, directory=None):
        """Export all data files as csv"""
        
        # filename
        filename = self.bfit.fileviewer.default_export_filename
        if not filename: return
        self.logger.info('Exporting to file %s', filename)
        
        if directory is None:
            try:
                filename = os.path.join(filedialog.askdirectory(), filename)
            except TypeError:
                pass
        else:
            filename = os.path.join(directory, filename)
        
        # get data and write
        for k in self.bfit.data.keys():
            d = self.bfit.data[k]
            omit = d.omit.get()
            if omit == self.bin_remove_starter_line:    omit = ''
            self.bfit.export(d, filename%(d.year, d.run), rebin=d.rebin.get(), 
                             omit=omit)
        self.logger.debug('Success.')
        
    # ======================================================================= #
    def filter_runs(self):
        """Remove or select runs based on filter conditions"""
        
        # parse input string
        string = self.text_filter.get('1.0', END)
        lines = [l for l in string.split('\n') if l]
        
        # iterate on fetched data
        data_keep = []
        
        for k, d in self.bfit.data.items():
            
            # check conditions
            satisfy = all([self._check_condition(d, line) for line in lines])
            if satisfy:
                data_keep.append(k)
            
        # do filtering by selection
        if self.filter_opt.get() == 'activate':
            for k, d in self.bfit.data.items():
                d.check_state.set(k in data_keep)
                
        elif self.filter_opt.get() == 'remove':
            keys = tuple(self.data_lines.keys())
            for k in keys:
                if k not in data_keep:
                    self.data_lines[k].degrid()
    
    # ======================================================================= #
    def get_data(self):
        """Split data into parts, and assign to dictionary."""
        
        self.logger.debug('Fetching runs')
    
        # make list of run numbers, replace possible deliminators
        try:
            run_numbers = self.string2run(self.run.get())
        except ValueError:
            self.logger.exception('Bad run number string')
            raise ValueError('Bad run number string')
            
        # get list of merged runs
        merged_runs = self.get_merged_runs(self.run.get())
            
        # get the selected year
        year = int(self.year.get())
        
        # get data
        all_data = {}
        s = ['Failed to open run']
        for r in run_numbers:
            
            # read from archive
            try:
                all_data[r] = bdata(r, year=year)
            except (RuntimeError, ValueError):
                s.append("%d (%d)" % (r, year))
                    
        # print error message
        if len(s)>1:
            s = '\n'.join(s)
            print(s)
            self.logger.warning(s)
            messagebox.showinfo(message=s)
        
        # merge runs
        new_data = []
        for merge in merged_runs: 
            
            # collect data
            dat_to_merge = []
            for r in merge: 
                dat_to_merge.append(all_data.pop(r))
            
            # make bjoined object
            new_data.append(bmerged(dat_to_merge))
            
        new_data.extend(list(all_data.values()))
        
        # update object data lists
        data = {}
        for new_dat in new_data:
            
            # get key for data storage
            runkey = self.bfit.get_run_key(new_dat)

            # update data
            if runkey in self.bfit.data.keys():
                self.bfit.data[runkey].read()
                
            # new data
            else:
                data[runkey] = fitdata(self.bfit, new_dat)
    
        # check that data is all the same runtype
        run_types = [d.mode for d in self.bfit.data.values()]
        run_types = run_types + [d.mode for d in data.values()]
        
        # check for equivalent run modes
        selected_mode = [run_types[0]]
        for equiv in self.equivalent_modes:
            if selected_mode[0] in equiv:
                selected_mode = equiv
                break
        
        # different run types: select all runs of same type
        if not all([r in selected_mode for r in run_types]):
            
            # unique run modes
            run_type_unique = np.unique(run_types)
            
            # message for multiple run modes
            message = "Multiple run types detected:\n("
            message += ', '.join(run_type_unique)
            message += ')\n\nSelecting ' + ' and '.join(selected_mode) + ' runs.'
            messagebox.showinfo(message=message)
            
        # get only run_types[0]
        self.logger.debug('Fetching runs of mode %s', selected_mode)
        for k in tuple(data.keys()):
            if data[k].mode in selected_mode:
                self.bfit.data[k] = data[k]
            else:
                del data[k]
        
        # get runmode
        try:
            self.runmode = selected_mode
        except IndexError:
            s = 'No valid runs detected.'
            messagebox.showerror(message=s)
            self.logger.warning(s)
            raise RuntimeError(s)
            
        self.runmode_label['text'] = self.runmode_relabel[self.runmode[0]]
        
        # get area
        area = [d.area for d in self.bfit.data.values()]
        area = ''.join(np.unique(area))
        
        # set asym type comboboxes
        self.bfit.set_asym_calc_mode_box(self.runmode[0], self, area)
        self.bfit.set_asym_calc_mode_box(self.runmode[0], self.bfit.fit_files, area)
        
        keys_list = list(self.bfit.data.keys())
        keys_list.sort()
        
        # make lines
        n = 1
        for r in keys_list:
            
            # new line
            if r not in self.data_lines.keys():
                
                if r in self.data_lines_old.keys():
                    self.data_lines[r] = self.data_lines_old[r]
                    self.data_lines[r].set_label()
                    del self.data_lines_old[r]
                else:
                    self.data_lines[r] = dataline(\
                                            bfit = self.bfit, \
                                            lines_list = self.data_lines, \
                                            lines_list_old = self.data_lines_old, 
                                            fetch_tab_frame = self.dataline_frame, \
                                            bdfit = self.bfit.data[r], \
                                            row = n)
            self.data_lines[r].grid(n)
            n+=1
            
        # remove old runs, modes not selected
        for r in tuple(self.data_lines.keys()):
            if self.data_lines[r].bdfit.mode not in self.runmode:
                self.data_lines[r].degrid()
            
        # set nbm variable
        self.set_nbm()
        
        self.logger.info('Fetched runs %s', list(data.keys()))
        
    # ======================================================================= #
    def get_merged_runs(self, string):
        """
            Parse string, return list of lists of run numbers corresponding to 
            the data to merge
        """
        
        # find plus locations
        idx_plus = [m.start() for m in re.finditer(r'\+', string)]

        # remove spaces around plus
        for i in idx_plus[::-1]:
            if string[i+1] == ' ':
                string = string[:i+1]+string[i+2:]
            if string[i-1] == ' ':
                string = string[:i-1]+string[i:]
            
        # clean input
        string = re.sub('[, ;]', ' ', string)

        # add brackets
        string = ' '.join(['[%s]' % s if '+' in s else s for s in string.split()])

        # remove plusses
        string = re.sub(r'\+', ' ', string)

        # get strings for merging
        merge_strings = [*re.findall(r'\[(.*?)\]', string), 
                         *re.findall(r'\((.*?)\)', string), 
                         *re.findall(r'\{(.*?)\}', string)]

        
        # split up the input string by brackets
        merge_strings = [*re.findall(r'\[(.*?)\]', string), 
                         *re.findall(r'\((.*?)\)', string), 
                         *re.findall(r'\{(.*?)\}', string)]

        # get the run numbers in each of the merged string inputs
        merge_runs = [self.string2run(s) for s in merge_strings]
        
        return merge_runs
        
    # ======================================================================= #
    def history_set(self, x):
        """
            Set the history entry as the current fetch string
        """
        
        idx = self.listbox_history.curselection() 
        if not idx:
            on_focusout_fn(0)
            return 
            
        item = self.listbox_history.get(idx)
        self.listbox_history.delete(idx)
        self.listbox_history.insert(0, item)
        self.entry_run.delete(0, END)
        self.entry_run.insert(0, item)
        self.history_hide()
        self.entry_run.focus_set()
        
    # ======================================================================= #
    def history_show(self, x=None):
        """
            Show list widget with input history
        """
        if self.listbox_history.size()>0:
            self.listbox_history.config(height=self.listbox_history.size())
            x = self.entry_run.winfo_x()
            y = self.entry_run.winfo_y()
            dx = self.entry_run.winfo_width()
            self.listbox_history.place(x=x+6, y=y+30, width=dx)
            self.listbox_history.lift()
            
    # ======================================================================= #
    def history_hide(self, event=None, obj=None):
        """
            Hide list widget with input history
        """

        # don't hide if mousing over history
        if obj == 'entry' and 0 < event.x < self.entry_run.winfo_reqwidth() and event.y > 0:
            return  
        
        # hide the history box    
        self.listbox_history.place_forget()
        string = self.run.get() 
        
        if string != self.listbox_history.get(0) and \
           string != self.run_number_starter_line:
            self.listbox_history.insert(0, string)
            
        if self.listbox_history.size()>self.nhistory:
            self.listbox_history.delete(END)            
    
    # ======================================================================= #
    def remove_all(self):
        """Remove all data files from self.data_lines"""
        
        self.logger.info('Removing all data files')
        del_list = []
        for r in self.data_lines.keys():
            if self.data_lines[r].check_state.get():
                del_list.append(self.data_lines[r])
        
        for d in del_list:
            d.degrid()
    
    # ======================================================================= #
    def return_binder(self):
        """Switch between various functions of the enter button. """
        
        # check where the focus is
        focus_id = self.bfit.root.focus_get()
        
        # run or year entry
        if focus_id in [self.entry_run, self.entry_year]:
            self.logger.debug('Focus is: run or year entry')
            self.get_data()
            self.history_hide()
        
        # check all box
        elif focus_id == self.check_all_box:
            self.logger.debug('Focus is: check all box')
            self.draw_all()
            
        # filter
        elif focus_id == self.text_filter:
            self.logger.debug('Focus is: text_filter')
            self.filter_runs()
            
        else:
            pass

    # ======================================================================= #
    def set_all(self, changed, *args):
        """Set a particular property for all checked items. """
        
        self.logger.info('Set all')
        data = self.bfit.data
        
        # check all file lines
        for dat in data.values():
            
            # if checked
            if dat.check_state.get():
                
                # rebin
                if changed == 'rebin':
                    try:
                        rebin = self.check_rebin.get()
                    except TclError:
                        rebin = 1
                        
                    dat.rebin.set(rebin)
                
                # omit bins
                elif changed == 'omit':
                    dat.omit.set(self.check_bin_remove.get())
                
                # omit scan
                elif changed == 'omit_scan':
                    dat.omit_scan.set(self.omit_state.get())
                
                # baseline corrections
                elif changed == 'base_bins':
                    try:
                        val = self.base_bins.get()
                    except TclError:
                        val = 1
                    dat.base_bins.set(val)
                    
    # ======================================================================= #
    def set_all_labels(self):
        """Set lable text in all items """
        
        self.logger.info('Setting all label text')
        
        # check all file lines
        for r in self.data_lines.keys():
            self.data_lines[r].set_label()
            
        for r in self.data_lines_old.keys():
            self.data_lines_old[r].set_label()

    # ======================================================================= #
    def set_nbm(self):
        """
            Set the nbm variable based on the run mode
        """
        
        # check if data
        if not hasattr(self, 'runmode'):
            return
        
        # check run mode
        mode = self.runmode[0]
        
        self.bfit.set_nbm(mode)
    
    # ======================================================================= #
    def show_filter_instructions(self):
        """Display popup with instructions on filtering"""
        
        # instructions
        msg = 'Write one boolean expression \nper line using the below '+\
              'variables. \n\n'+\
              'Runs which satisfy all expressions \nare kept/activated\n\n'
              
        # variables
        keys = sorted(KEYVARS.keys())
        values = [KEYVARS[k] for k in keys]
        max_keylen = max(tuple(map(len, keys)))
        
        lines = [k.ljust(max_keylen+2) + v for k, v in zip(keys, values)]
              
        msg += '     ' + ('\n     '.join(lines))
        
        # example
        ex = 'ex: "10 < BIAS < 15"'
        msg += '\n\n' + ex
        
        # make window
        win = Toplevel(self.bfit.mainframe)
        win.title('How to filter runs')
        self.bfit.set_icon(win)
        
        frame = ttk.Frame(win, pad=10, relief='sunken')
        frame.grid(column=0, row=0)
        ttk.Label(frame, text=msg, justify='left').grid(column=0, row=0, pady=5)
        ttk.Button(frame, text='Close', 
                   command=lambda: win.destroy()).grid(column=0, row=1, pady=5)
            
    # ======================================================================= #
    def string2run(self, string):
        """Parse string, return list of run numbers"""
        
        # standardize deliminators
        full_string = re.sub(r'[, ;+\[\]\(\)\{\}]', ' ', string)
        full_string = full_string.replace(':', '-')
        part_string = full_string.split()
        
        # get list of run numbers
        run_numbers = []
        for s in part_string:
            
            # select a range
            if '-' in s:
                
                # get runs in range
                try:
                    spl = s.split('-')
                    
                    # look for "range to current run"
                    if spl[1] == '':
                        
                        # look for latest run by run number
                        if int(spl[0]) < 45000:
                            dirloc = os.environ[self.bfit.bnmr_archive_label]
                        else:
                            dirloc = os.environ[self.bfit.bnqr_archive_label]
                            
                        runlist = glob.glob(os.path.join(dirloc, 
                                                         str(self.year.get()), 
                                                         '*.msr'))
                        spl[1] = max([int(os.path.splitext(os.path.basename(r))[0]) 
                                   for r in runlist])
                        
                    rn_lims = tuple(map(int, spl))
                    
                # get bad range first value
                except ValueError:
                    run_numbers.append(int(s.replace('-', '')))
                
                # get range of runs
                else:
                    rns = np.arange(rn_lims[0], rn_lims[1]+1).tolist()
                    run_numbers.extend(rns)
            
            # get single run
            else:
                run_numbers.append(int(s))
        
        # sort
        run_numbers.sort()
        self.logger.debug('Parsed "%s" to run numbers (len: %d) %s', string, 
                          len(run_numbers), run_numbers)
        
        if len(run_numbers) > self.max_number_fetched:
            raise RuntimeWarning("Too many files selected (max %d)." \
                                                    % self.max_number_fetched)
        return run_numbers
    
    # ======================================================================= #
    def toggle_all(self):
        """Toggle all tickboxes"""
        self.logger.info('Toggling all tickboxes')
        for k in self.data_lines.keys():
            state = not self.data_lines[k].check_state.get()
            self.data_lines[k].check_state.set(state)

    # ======================================================================= #
    def update_data(self):
        """
            Re-fetch all fetched runs.
            Update labels
        """
        
        self.logger.info('Updating data')
        
        # fetch
        for dat in self.bfit.data.values():
            dat.read()
            
        # update text
        for line in self.data_lines.values():
            line.set_check_text()
            line.update_label()
