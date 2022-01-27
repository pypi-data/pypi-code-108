# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from bdata import bdata, bmerged
from bfit import logger_name, __version__
from pandas.plotting import register_matplotlib_converters
from multiprocessing import Queue

from bfit.gui.popup_show_param import popup_show_param
from bfit.gui.popup_param import popup_param
from bfit.gui.popup_fit_results import popup_fit_results
from bfit.gui.popup_fit_constraints import popup_fit_constraints
from bfit.gui.popup_add_param import popup_add_param
from bfit.gui.popup_ongoing_process import popup_ongoing_process
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.backend.raise_window import raise_window
from bfit.gui.fitline import fitline

import numpy as np
import pandas as pd
import bdata as bd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import bfit.backend.colors as colors

import datetime, os, traceback, warnings, logging

register_matplotlib_converters()

# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            annotation:     stringvar: name of quantity for annotating parameters
            annotation_combobox: box for choosing annotation label parameter
            asym_type:      asymmetry calculation type
            canvas_frame_id:id number of frame in canvas
            chi_threshold:  if chi > thres, set color to red
            draw_components:list of titles for labels, options to export, draw.
            entry_asym_type:combobox for asym calculations
            fit_canvas:     canvas object allowing for scrolling
            fit_data_tab:   containing frame (for destruction)
            fit_function_title: StringVar, title of fit function to use
            fit_function_title_box: combobox for fit function names
            fit_input:      fitting input values = (fn_name, ncomp, data_list)
            fit_lines:      Dict storing fitline objects
            fit_lines_old: dictionary of previously used fitline objects, keyed by run
            fit_routine_label: label for fit routine
            fitter:         fitting object from self.bfit.routine_mod
            gchi_label:     Label for global chisquared
            mode:           what type of run is this.

            n_component:    number of fitting components (IntVar)
            n_component_box:Spinbox for number of fitting components
            par_label       StringVar, label for plotting parameter set
            par_label_entry:draw parameter label entry box
            plt:            self.bfit.plt

            pop_addpar:     popup for ading parameters which are combinations of others
            pop_fitres:     modelling popup, for continuity between button presses
            pop_fitconstr:  object for fitting with constrained functions

            probe_label:    Label for probe species
            runframe:       frame for displaying fit results and inputs
            runmode_label:  display run mode
            set_as_group:   BooleanVar() if true, set fit parfor whole group
            set_prior_p0:   BooleanVar() if true, set P0 of newly added runs to
                            P0 of fit with largest run number
            share_var:      BooleanVar() holds share checkbox for all fitlines
            use_rebin:      BoolVar() for rebinning on fitting
            xaxis:          StringVar() for parameter to draw on x axis
            yaxis:          StringVar() for parameter to draw on y axis
            xaxis_combobox: box for choosing x axis draw parameter
            yaxis_combobox: box for choosing y axis draw parameter

            xlo, hi:         StringVar, fit range limits on x axis
    """

    mode = ""
    chi_threshold = 1.5 # threshold for red highlight on bad fits
    n_fitx_pts = 500    # number of points to draw in fitted curves
    
    # ======================================================================= #
    def __init__(self, fit_data_tab, bfit):

        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')

        # initialize
        self.bfit = bfit
        self.fit_output = {}
        self.share_var = {}
        self.fitter = self.bfit.routine_mod.fitter(keyfn = bfit.get_run_key,
                                                   probe_species = bfit.probe_species.get())
        self.draw_components = list(bfit.draw_components)
        self.fit_data_tab = fit_data_tab
        self.plt = self.bfit.plt
        
        self.fit_lines = {}
        self.fit_lines_old = {}

        self.pop_fitconstr = popup_fit_constraints(self.bfit, self)

        # additional button bindings
        self.bfit.root.bind('<Control-Key-u>', self.update_param)

        # make top level frames
        mid_fit_frame = ttk.Labelframe(fit_data_tab,
                                       text='Initial Parameters and Fit Results', pad=5)

        mid_fit_frame.grid(column=0, row=1, rowspan=6, sticky=(S, W, E, N), padx=5, pady=5)

        fit_data_tab.grid_columnconfigure(0, weight=1)   # fitting space
        fit_data_tab.grid_rowconfigure(6, weight=1)      # push bottom window in right frame to top
        mid_fit_frame.grid_columnconfigure(0, weight=1)
        mid_fit_frame.grid_rowconfigure(0, weight=1)

        # TOP FRAME -----------------------------------------------------------

        # fit function select
        fn_select_frame = ttk.Labelframe(fit_data_tab, text='Fit Function')
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame,
                textvariable=self.fit_function_title, state='readonly')
        self.fit_function_title_box.bind('<<ComboboxSelected>>',
                lambda x:self.populate_param(force_modify=True))

        # number of components in fit spinbox
        self.n_component = IntVar()
        self.n_component.set(1)
        self.n_component_box = Spinbox(fn_select_frame, from_=1, to=20,
                textvariable=self.n_component, width=5,
                command=lambda:self.populate_param(force_modify=True))

        # fit and other buttons
        fit_button = ttk.Button(fn_select_frame, text='        Fit        ', command=self.do_fit, \
                                pad=1)
        constraint_button = ttk.Button(fn_select_frame, text='Constrain',
                                       command=self.show_constr_window, pad=1)
        set_param_button = ttk.Button(fn_select_frame, text='   Set Result as P0   ',
                        command=self.do_set_result_as_initial, pad=1)
        reset_param_button = ttk.Button(fn_select_frame, text='     Reset P0     ',
                        command=self.do_reset_initial, pad=1)

        # GRIDDING

        # top frame gridding
        fn_select_frame.grid(column=0, row=0, sticky=(W, E, N), padx=5, pady=5)

        c = 0
        self.fit_function_title_box.grid(column=c, row=0, padx=5); c+=1
        ttk.Label(fn_select_frame, text="Number of Terms:").grid(column=c,
                  row=0, padx=5, pady=5, sticky=W); c+=1
        self.n_component_box.grid(column=c, row=0, padx=5, pady=5, sticky=W); c+=1
        fit_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1
        constraint_button.grid(column=c, row=0, padx=5, pady=1, sticky=(W, E)); c+=1
        set_param_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1
        reset_param_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1

        # MID FRAME -----------------------------------------------------------

        # Scrolling frame to hold fitlines
        yscrollbar = ttk.Scrollbar(mid_fit_frame, orient=VERTICAL)
        self.fit_canvas = Canvas(mid_fit_frame, bd=0,                # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000), confine=True)       # default size
        yscrollbar.config(command=self.fit_canvas.yview)            # scroll command send
        self.runframe = ttk.Frame(self.fit_canvas, pad=5)           # holds

        self.canvas_frame_id = self.fit_canvas.create_window((0, 0),    # make window which can scroll
                window=self.runframe,
                anchor='nw')
        self.runframe.bind("<Configure>", self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>", self.config_runframe) # bind resize to change size of contained frame

        # gridding
        self.fit_canvas.grid(column=0, row=0, sticky=(E, W, S, N))
        yscrollbar.grid(column=1, row=0, sticky=(W, S, N))

        self.runframe.grid_columnconfigure(0, weight=1)
        self.fit_canvas.grid_columnconfigure(0, weight=1)
        self.fit_canvas.grid_rowconfigure(0, weight=1)

        self.runframe.bind("<Configure>", self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>", self.config_runframe) # bind resize to change size of contained frame

        # RIGHT FRAME ---------------------------------------------------------

        # run mode
        fit_runmode_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Run Mode', )
        self.fit_runmode_label = ttk.Label(fit_runmode_label_frame, text="", justify=CENTER)

        # fitting routine
        fit_routine_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Minimizer', )
        self.fit_routine_label = ttk.Label(fit_routine_label_frame, text="",
                                           justify=CENTER)

        # probe species
        probe_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Probe', )
        self.probe_label = ttk.Label(probe_label_frame,
                                     text=self.bfit.probe_species.get(),
                                     justify=CENTER)

        # global chisquared
        gchi_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Global ChiSq', )
        self.gchi_label = ttk.Label(gchi_label_frame, text='', justify=CENTER)

        # asymmetry calculation
        asym_label_frame = ttk.Labelframe(fit_data_tab, pad=(5, 5, 5, 5),
                text='Asymmetry Calculation', )
        self.asym_type = StringVar()
        self.asym_type.set('')
        self.entry_asym_type = ttk.Combobox(asym_label_frame, \
                textvariable=self.asym_type, state='readonly', \
                width=20)
        self.entry_asym_type['values'] = ()

        # other settings
        other_settings_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Switches', )

        # set as group checkbox
        self.set_as_group = BooleanVar()
        set_group_check = ttk.Checkbutton(other_settings_label_frame,
                text='Modify for all', \
                variable=self.set_as_group, onvalue=True, offvalue=False)
        self.set_as_group.set(False)

        # rebin checkbox
        self.use_rebin = BooleanVar()
        set_use_rebin = ttk.Checkbutton(other_settings_label_frame,
                text='Rebin data (set in fetch)', \
                variable=self.use_rebin, onvalue=True, offvalue=False)
        self.use_rebin.set(False)

        # set P0 as prior checkbox
        self.set_prior_p0 = BooleanVar()
        set_prior_p0 = ttk.Checkbutton(other_settings_label_frame,
                text='Set P0 of new run to prior result', \
                variable=self.set_prior_p0, onvalue=True, offvalue=False)
        self.set_prior_p0.set(False)

        # specify x axis --------------------
        xspecify_frame = ttk.Labelframe(fit_data_tab,
            text='Restrict x limits', pad=5)

        self.xlo = StringVar()
        self.xhi = StringVar()
        self.xlo.set('-inf')
        self.xhi.set('inf')

        entry_xspecify_lo = Entry(xspecify_frame, textvariable=self.xlo, width=10)
        entry_xspecify_hi = Entry(xspecify_frame, textvariable=self.xhi, width=10)
        label_xspecify = ttk.Label(xspecify_frame, text=" < x < ")

        # fit results -----------------------
        results_frame = ttk.Labelframe(fit_data_tab,
            text='Fit Results and Run Conditions', pad=5)     # draw fit results

        # draw and export buttons
        button_frame = Frame(results_frame)
        draw_button = ttk.Button(button_frame, text='Draw', command=self.draw_param)
        update_button = ttk.Button(button_frame, text='Update', command=self.update_param)
        export_button = ttk.Button(button_frame, text='Export', command=self.export)
        show_button = ttk.Button(button_frame, text='Compare', command=self.show_all_results)
        model_fit_button = ttk.Button(button_frame, text='Fit a\nModel',
                                      command=self.do_fit_model)

        # menus for x and y values
        x_button = ttk.Button(results_frame, text="x axis:", command=self.do_add_param, pad=0)
        y_button = ttk.Button(results_frame, text="y axis:", command=self.do_add_param, pad=0)
        ann_button = ttk.Button(results_frame, text=" Annotation:", command=self.do_add_param, pad=0)
        label_label = ttk.Label(results_frame, text="Label:")

        self.xaxis = StringVar()
        self.yaxis = StringVar()
        self.annotation = StringVar()
        self.par_label = StringVar()

        self.xaxis.set('')
        self.yaxis.set('')
        self.annotation.set('')
        self.par_label.set('')

        self.xaxis_combobox = ttk.Combobox(results_frame, textvariable=self.xaxis,
                                      state='readonly', width=19)
        self.yaxis_combobox = ttk.Combobox(results_frame, textvariable=self.yaxis,
                                      state='readonly', width=19)
        self.annotation_combobox = ttk.Combobox(results_frame,
                                      textvariable=self.annotation,
                                      state='readonly', width=19)
        self.par_label_entry = Entry(results_frame,
                                    textvariable=self.par_label, width=21)

        # gridding
        button_frame.grid(column=0, row=0, columnspan=2)
        draw_button.grid(column=0, row=0, padx=5, pady=5)
        update_button.grid(column=0, row=1, padx=5, pady=5)
        show_button.grid(column=1, row=0, padx=5, pady=5)
        export_button.grid(column=1, row=1, padx=5, pady=5)
        model_fit_button.grid(column=2, row=0, rowspan=2, pady=5, sticky=(N, S))

        x_button.grid(column=0, row=1, sticky=(E, W), padx=5)
        y_button.grid(column=0, row=2, sticky=(E, W), padx=5)
        ann_button.grid(column=0, row=3, sticky=(E, W), padx=5)
        label_label.grid(column=0, row=4, sticky=(E, W), padx=10)

        self.xaxis_combobox.grid(column=1, row=1, pady=5)
        self.yaxis_combobox.grid(column=1, row=2, pady=5)
        self.annotation_combobox.grid(column=1, row=3, pady=5)
        self.par_label_entry.grid(column=1, row=4, pady=5)

        # save/load state -----------------------
        state_frame = ttk.Labelframe(fit_data_tab, text='Program State', pad=5)
        state_save_button = ttk.Button(state_frame, text='Save', command=self.bfit.save_state)
        state_load_button = ttk.Button(state_frame, text='Load', command=self.bfit.load_state)

        state_save_button.grid(column=1, row=0, padx=5, pady=5)
        state_load_button.grid(column=2, row=0, padx=5, pady=5)
        state_frame.columnconfigure([0, 3], weight=1)

        # gridding
        fit_runmode_label_frame.grid(column=1, row=0, pady=5, padx=2, sticky=(N, E, W))
        self.fit_runmode_label.grid(column=0, row=0, sticky=(E, W))

        fit_routine_label_frame.grid(column=2, row=0, pady=5, padx=2, sticky=(N, E, W))
        self.fit_routine_label.grid(column=0, row=0, sticky=(E, W))

        probe_label_frame.grid(column=1, row=1, columnspan=1, sticky=(E, W, N), pady=2, padx=2)
        self.probe_label.grid(column=0, row=0)

        gchi_label_frame.grid(column=2, row=1, columnspan=1, sticky=(E, W, N), pady=2, padx=2)
        self.gchi_label.grid(column=0, row=0)

        asym_label_frame.grid(column=1, row=2, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        asym_label_frame.columnconfigure([0, 2], weight=1)
        self.entry_asym_type.grid(column=1, row=0)

        other_settings_label_frame.grid(column=1, row=3, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        set_group_check.grid(column=0, row=0, padx=5, pady=1, sticky=W)
        set_use_rebin.grid(column=0, row=1, padx=5, pady=1, sticky=W)
        set_prior_p0.grid(column=0, row=2, padx=5, pady=1, sticky=W)

        entry_xspecify_lo.grid(column=1, row=0)
        label_xspecify.grid(column=2, row=0)
        entry_xspecify_hi.grid(column=3, row=0)
        xspecify_frame.columnconfigure([0, 4], weight=1)

        xspecify_frame.grid(column=1, row=4, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        results_frame.grid(column=1, row=5, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        state_frame.grid(column=1, row=6, columnspan=2, sticky=(E, W, N), pady=2, padx=2)

        # resizing

        # fn select
        fn_select_frame.grid_columnconfigure(1, weight=1)    # Nterms label
        fn_select_frame.grid_columnconfigure(4, weight=100)    # constraints
        fn_select_frame.grid_columnconfigure(5, weight=1)  # set results as p0
        fn_select_frame.grid_columnconfigure(6, weight=1)  # reset p0

        # fitting frame
        self.fit_canvas.grid_columnconfigure(0, weight=1)    # fetch frame
        self.fit_canvas.grid_rowconfigure(0, weight=1)

        # right frame
        for i in range(2):
            results_frame.grid_columnconfigure(i, weight=0)

    # ======================================================================= #
    def __del__(self):

        if hasattr(self, 'fit_lines'):       del self.fit_lines
        if hasattr(self, 'fit_lines_old'):   del self.fit_lines_old
        if hasattr(self, 'fitter'):          del self.fitter

        # kill buttons and frame
        try:
            for child in self.fetch_data_tab.winfo_children():
                child.destroy()
            self.fetch_data_tab.destroy()
        except Exception:
            pass

     # ======================================================================= #
    def _annotate(self, id, x, y, ptlabels, color='k', unique=True):
        """Add annotation"""

        # base case
        if ptlabels is None: return

        # do annotation
        for label, xcoord, ycoord in zip(ptlabels, x, y):
            if type(label) != type(None):
                self.plt.annotate('param', id, label,
                             xy=(xcoord, ycoord),
                             xytext=(-3, 20),
                             textcoords='offset points',
                             ha='right',
                             va='bottom',
                             bbox=dict(boxstyle='round, pad=0.1',
                                       fc=color,
                                       alpha=0.1),
                             arrowprops=dict(arrowstyle = '->',
                                             connectionstyle='arc3, rad=0'),
                             fontsize='xx-small',
                             unique=unique
                            )

    # ======================================================================= #
    def canvas_scroll(self, event):
        """Scroll canvas with files selected."""
        if event.num == 4:
            self.fit_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.fit_canvas.yview_scroll(1, "units")

    # ======================================================================= #
    def config_canvas(self, event):
        """Alter scrollable region based on canvas bounding box size.
        (changes scrollbar properties)"""
        self.fit_canvas.configure(scrollregion=self.fit_canvas.bbox("all"))

    # ======================================================================= #
    def config_runframe(self, event):
        """Alter size of contained frame in canvas. Allows for inside window to
        be resized with mouse drag"""
        self.fit_canvas.itemconfig(self.canvas_frame_id, width=event.width)

    # ======================================================================= #
    def populate(self, *args):
        """
            Make tabs for setting fit input parameters.
        """
        
        # get data
        dl = self.bfit.fetch_files.data_lines
        keylist = [k for k in dl.keys() if dl[k].check_state.get()]
        keylist.sort()
        self.logger.debug('Populating data for %s', keylist)

        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.bfit.data.keys(): break

        # create fit function combobox options
        try:
            if self.mode != self.bfit.data[key_zero].mode:

                # set run mode
                self.mode = self.bfit.data[key_zero].mode
                self.fit_runmode_label['text'] = \
                        self.bfit.fetch_files.runmode_relabel[self.mode]
                self.logger.debug('Set new run mode %s', self.mode)

                # set routine
                self.fit_routine_label['text'] = self.fitter.__name__

                # set run functions
                fn_titles = self.fitter.function_names[self.mode]
                self.fit_function_title_box['values'] = fn_titles
                
                # set current function
                if self.fit_function_title.get() not in fn_titles:
                    self.fit_function_title.set(fn_titles[0])
                    self.n_component.set(1)

        except UnboundLocalError:
            self.fit_function_title_box['values'] = ()
            self.fit_function_title.set("")
            self.fit_runmode_label['text'] = ""
            self.mode = ""
            self.n_component.set(1)
        
        # delete unused fitline objects
        for k in list(self.fit_lines.keys()):       # iterate fit list
            self.fit_lines[k].degrid()
            if k not in keylist:                    # check data list
                self.fit_lines_old[k] = self.fit_lines[k]
                del self.fit_lines[k]

        # make or regrid fitline objects
        n = 0
        parlst = list(self.fitter.gen_param_names(self.fit_function_title.get(),
                                                  self.n_component.get()))
        for k in keylist:
            if k not in self.fit_lines.keys():
                
                # add back old fit line
                if k in self.fit_lines_old.keys():
                    self.fit_lines[k] = self.fit_lines_old[k]
                    del self.fit_lines_old[k]
                                       
                # make new fit line
                else:
                    self.fit_lines[k] = fitline(self.bfit, self.runframe, dl[k].bdfit, n)
                    
            self.fit_lines[k].grid(n)
            n+=1
            
        self.populate_param()

    # ======================================================================= #
    def populate_param(self, *args, force_modify=False):
        """
            Populate the list of parameters

            force_modify: passed to line.populate
        """
       
        self.logger.debug('Populating fit parameters')

        # populate axis comboboxes
        lst = self.draw_components.copy()

        # get list of fit parameters
        try:
            parlst = list(self.fitter.gen_param_names(
                                            self.fit_function_title.get(),
                                            self.n_component.get()),
                          )
        except KeyError:
            self.xaxis_combobox['values'] = []
            self.yaxis_combobox['values'] = []
            self.annotation_combobox['values'] = []
            return

        # set contraints flag
        constr_pop = self.pop_fitconstr
        if force_modify:
            constr_pop.constraints_are_set = False

        # get constrained parameters
        else:
            for d, new in zip(constr_pop.defined, constr_pop.new_par):
                if d in parlst:
                    parlst.extend(new)

        # Sort the parameters
        parlst = list(np.unique(parlst))
        parlst.sort()

        # add parameter beta averaged T1
        if self.fit_function_title.get() == 'Str Exp':
            ncomp = self.n_component.get()

            if ncomp > 1:
                for i in range(ncomp): 
                    parlst.append('Beta-Avg 1/<T1>_%d' % i)
            else:
                parlst.append('Beta-Avg 1/<T1>')

        # add parameter T1 not 1/T1
        T1_lst = []
        if 'Exp' in self.fit_function_title.get():
            ncomp = self.n_component.get()

            if ncomp > 1:
                for i in range(ncomp):
                    T1_lst.append('T1_%d' % i)
                    
                    if self.fit_function_title.get() == 'Bi Exp':
                        T1_lst.append('T1b_%d' % i)
                    
            else:
                T1_lst.append('T1')
                
                if self.fit_function_title.get() == 'Bi Exp':
                    T1_lst.append('T1b')

        if self.fit_function_title.get() == 'Str Exp':
            if ncomp > 1:
                for i in range(ncomp): 
                    T1_lst.append('Beta-Avg <T1>_%d' % i)
            else:
                T1_lst.append('Beta-Avg <T1>')

        self.xaxis_combobox['values'] = [''] + parlst + ['all the above'] + T1_lst + lst
        self.yaxis_combobox['values'] = [''] + parlst + ['all the above'] + T1_lst + lst
        self.annotation_combobox['values'] = [''] + parlst + lst

        # turn off modify all so we don't cause an infinite loop
        modify_all_value = self.set_as_group.get()
        self.set_as_group.set(False)

        # regenerate fitlines
        for fline in self.fit_lines.values():
            fline.populate(force_modify=force_modify)
        
        for fline in self.fit_lines_old.values():
            if self.mode == fline.data.mode:
                fline.populate(force_modify=force_modify)
        
        # reset modify all value
        self.set_as_group.set(modify_all_value)
        
    # ======================================================================= #
    def do_add_param(self, *args):
        """Launch popup for adding user-defined parameters to draw"""

        self.logger.info('Launching add paraemeter popup')

        if hasattr(self, 'pop_addpar'):
            p = self.pop_addpar

            # don't make more than one window
            if Toplevel.winfo_exists(p.win):
                p.win.lift()
                return

            # make a new window, using old inputs and outputs
            self.pop_addpar = popup_add_param(self.bfit,
                                    input_fn_text=p.input_fn_text)

        # make entirely new window
        else:
            self.pop_addpar = popup_add_param(self.bfit)

    # ======================================================================= #
    def do_end_of_fit(self):
        """Things to do after fitting: draw, set checkbox status"""

        # enable fit checkboxes on fetch files tab
        for k in self.bfit.fetch_files.data_lines.keys():
            dline = self.bfit.fetch_files.data_lines[k]
            dline.draw_fit_checkbox['state'] = 'normal'
            dline.draw_res_checkbox['state'] = 'normal'
            dline.check_fit.set(True)
        self.bfit.fetch_files.check_state_fit.set(True)

        # change fetch asymmetry mode to match fit tab
        inv_map = {v: k for k, v in self.bfit.asym_dict.items()}
        asym_mode_fit = inv_map[self.bfit.get_asym_mode(self)]
        asym_mode_fetch = inv_map[self.bfit.get_asym_mode(self.bfit.fetch_files)]
        
        self.bfit.fetch_files.asym_type.set(asym_mode_fit)

        # draw fit results
        if self.bfit.draw_fit.get():
            style = self.bfit.draw_style.get()

            if style in ['stack', 'new']:
                self.bfit.draw_style.set('redraw')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.bfit.fetch_files.draw_all(figstyle='fit', ignore_check=False)

            if len(self.fit_lines.keys()) > self.bfit.legend_max_draw:

                try:
                    self.plt.gca('fit').get_legend().remove()
                except AttributeError:
                    pass
                else:
                    self.plt.tight_layout('fit')

            # reset style
            self.bfit.draw_style.set(style)
            
        # reset asym mode
        self.bfit.fetch_files.asym_type.set(asym_mode_fetch)
    
    # ======================================================================= #
    def do_fit(self, *args):
        # fitter
        fitter = self.fitter
        figstyle = 'fit'

        # get fitter inputs
        fn_name = self.fit_function_title.get()
        ncomp = self.n_component.get()

        xlims = [self.xlo.get(), self.xhi.get()]
        if not xlims[0]:
            xlims[0] = '-inf'
            self.xlo.set('-inf')
        if not xlims[1]:
            xlims[1] = 'inf'
            self.xhi.set('inf')

        try:
            xlims = tuple(map(float, xlims))
        except ValueError as err:
            messagebox.showerror("Error", 'Bad input for xlims')
            self.logger.exception(str(err))
            raise err

        self.logger.info('Fitting with "%s" with %d components', fn_name, ncomp)

        # build data list
        data_list = []
        for key in self.fit_lines:

            # get fit line
            fitline = self.fit_lines[key]

            # bdata object
            bdfit = fitline.data

            # get entry values
            pdict = {}
            for line in fitline.lines:
                inpt = line.get('*')
                pdict[line.pname] = [inpt[k] for k in ('p0', 'blo', 'bhi', 'fixed', 'shared')]

            # doptions
            doptions = {}

            if self.use_rebin.get():
                doptions['rebin'] = bdfit.rebin.get()

            if '1' in self.mode:
                dline = self.bfit.fetch_files.data_lines[key]
                doptions['omit'] = dline.bin_remove.get()
                if doptions['omit'] == dline.bin_remove_starter_line:
                    doptions['omit'] = ''
            elif '2' in self.mode:
                pass
            else:
                msg = 'Fitting mode %s not recognized' % self.mode
                self.logger.error(msg)
                raise RuntimeError(msg)

            # make data list
            data_list.append([bdfit, pdict, doptions])

        # call fitter with error message, potentially
        self.fit_input = (fn_name, ncomp, data_list)

        # set up queue
        que = Queue()

        def run_fit():
            try:
                # fit_output keyed as {run:[key/par/cov/chi/fnpointer]}
                fit_output = fitter(fn_name=fn_name,
                                    ncomp=ncomp,
                                    data_list=data_list,
                                    hist_select=self.bfit.hist_select,
                                    asym_mode=self.bfit.get_asym_mode(self),
                                    xlims=xlims)
            except Exception as errmsg:
                self.logger.exception('Fitting error')
                que.put(str(errmsg))
                raise errmsg from None

            que.put(fit_output)

        # log fitting
        for d in data_list:
            self.logger.info('Fitting run %s: %s', self.bfit.get_run_key(d[0]), d[1:])

        # start fit
        popup = popup_ongoing_process(self.bfit,
                    target = run_fit,
                    message="Fitting in progress...",
                    queue = que,
                    do_disable = lambda : self.input_enable_disable(self.fit_data_tab, state='disabled'),
                    do_enable = lambda : self.input_enable_disable(self.fit_data_tab, state='normal'),
                    )
        output = popup.run()

        # fit success
        if type(output) is tuple: 
            fit_output, gchi = output

        # error message
        elif type(output) is str:
            messagebox.showerror("Error", output)
            return

        # fit cancelled
        elif output is None:
            return

        # get fit functions
        fns = fitter.get_fit_fn(fn_name, ncomp, data_list)
        
        # set output results
        for key, df in fit_output.items(): # iterate run ids
            
            # get fixed and shared
            fs = {'fixed':[], 'shared':[], 'parnames':[]}
            for line in self.fit_lines[key].lines:
                
                fs['parnames'].append(line.pname)
                fs['fixed'].append(line.get('fixed'))
                fs['shared'].append(line.get('shared'))
            
            df2 = pd.concat((df, pd.DataFrame(fs).set_index('parnames')), axis='columns')
            
            # make output
            new_output = {'results': df2, 
                          'fn': fns[key],
                          'gchi': gchi}
          
            self.bfit.data[key].set_fitresult(new_output)
            self.bfit.data[key].fit_title = self.fit_function_title.get()
            self.bfit.data[key].ncomp = self.n_component.get()
            
        # display run results
        for key in self.fit_lines.keys():
            self.fit_lines[key].show_fit_result()

        # show global chi
        self.gchi_label['text'] = str(np.around(gchi, 2))

        self.do_end_of_fit()

    # ======================================================================= #
    def do_fit_model(self):

        self.logger.info('Launching fit model popup')

        if hasattr(self, 'pop_fitres'):
            p = self.pop_fitres

            # don't make more than one window
            if Toplevel.winfo_exists(p.win):
                p.win.lift()
                return

            # make a new window, using old inputs and outputs
            self.pop_fitres = popup_fit_results(self.bfit,
                                    input_fn_text=p.input_fn_text,
                                    output_par_text=p.output_par_text_val,
                                    output_text=p.output_text_val,
                                    chi=p.chi,
                                    x = p.xaxis.get(),
                                    y = p.yaxis.get())

        # make entirely new window
        else:
            self.pop_fitres = popup_fit_results(self.bfit)

    # ======================================================================= #
    def do_gui_param(self, id=''):
        """Set initial parmeters with GUI"""

        self.logger.info('Launching initial fit parameters popup')
        popup_param(self.bfit, id)

    # ======================================================================= #
    def do_set_result_as_initial(self, *args):
        """Set initial parmeters as the fitting results"""

        self.logger.info('Setting initial parameters as fit results')

        # set result to initial value
        for k in self.fit_lines.keys():

            # get line
            fline = self.fit_lines[k]

            # set parameters
            for line in fline.lines:
                val = line.get('res')
                line.set(p0=val)

    # ======================================================================= #
    def do_reset_initial(self, *args):
        """Reset initial parmeters to defaults"""

        self.logger.info('Reset initial parameters')

        # reset lines
        for fline in self.fit_lines.values():
            fline.get_new_parameters(force_modify=True)
            fitpar = fline.data.fitpar
            for line in fline.lines:
                values = {c: fitpar.loc[line.pname, c] for c in fitpar.columns}
                line.set(**values)
            
    # ======================================================================= #
    def draw_param(self, *_):
        """Draw the fit parameters"""
        figstyle = 'param'

        # get draw components
        xdraw = self.xaxis.get()
        ydraw = self.yaxis.get()
        ann = self.annotation.get()
        label = self.par_label.get()

        # check for bad all the above input
        if ydraw == xdraw == 'all the above':
            msg = 'x and y cannot both be "all the above"'
            self.logger.error(msg)
            messagebox.showerror('Error', msg)
            raise RuntimeError(msg)

        # check for all the above - draw recursively
        if ydraw == 'all the above' or xdraw == 'all the above':
            
            self.logger.error("Drawing param as 'all the above'")
            
            # check which one we're modifying
            do_x = xdraw == 'all the above'
            
            # draw in new windows
            draw_style = self.bfit.draw_style.get()
            self.bfit.draw_style.set('new')
            
            for val in self.yaxis_combobox['values']:
                if val == 'all the above':  
                    break
                elif val != '':
                
                    # set axis value
                    if do_x:    self.xaxis.set(val)
                    else:       self.yaxis.set(val)
                    
                    # draw
                    self.draw_param()
                
            # reset axis value
            if do_x:    self.xaxis.set('all the above')
            else:       self.yaxis.set('all the above')
                    
            # reset draw style
            self.bfit.draw_style.set(draw_style)
            
            return
            
        self.logger.info('Draw fit parameters "%s" vs "%s" with annotation "%s"'+\
                         ' and label %s', ydraw, xdraw, ann, label)

        # get plottable data
        try:
            xvals, xerrs = self.get_values(xdraw)
            yvals, yerrs = self.get_values(ydraw)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter selection')
            messagebox.showerror("Error", 'Select two input parameters')
            raise err from None
        except (KeyError, AttributeError) as err:
            self.logger.error('Parameter "%s or "%s" not found for drawing',
                              xdraw, ydraw)
            messagebox.showerror("Error",
                    'Drawing parameter "%s" or "%s" not found' % (xdraw, ydraw))
            raise err from None

        # get asymmetric errors
        if type(xerrs) is tuple:
            xerrs_l = xerrs[0]
            xerrs_h = xerrs[1]
        else:
            xerrs_l = xerrs
            xerrs_h = xerrs

        if type(yerrs) is tuple:
            yerrs_l = yerrs[0]
            yerrs_h = yerrs[1]
        else:
            yerrs_l = yerrs
            yerrs_h = yerrs

        # get annotation
        if ann != '':
            try:
                ann, _ = self.get_values(ann)
            except UnboundLocalError:
                ann = None
            except (KeyError, AttributeError) as err:
                self.logger.error('Bad input annotation value "%s"', ann)
                messagebox.showerror("Error",
                        'Annotation "%s" not found' % (ann))
                raise err from None

        # fix annotation values (blank to none)
        else:
            ann = None

        # get mouseover annotation labels
        mouse_label, _ = self.get_values('Unique Id')

        # sort by x values
        idx = np.argsort(xvals)
        xvals = np.asarray(xvals)[idx]
        yvals = np.asarray(yvals)[idx]

        xerrs_l = np.asarray(xerrs_l)[idx]
        yerrs_l = np.asarray(yerrs_l)[idx]
        xerrs_h = np.asarray(xerrs_h)[idx]
        yerrs_h = np.asarray(yerrs_h)[idx]

        if ann is not None:
            ann = np.asarray(ann)[idx]

        mouse_label = np.asarray(mouse_label)[idx]

        # fix annotation values (round floats)
        if ann is not None:
            number_string = '%.'+'%df' % self.bfit.rounding
            for i, a in enumerate(ann):
                if type(a) in [float, np.float64]:
                    ann[i] = number_string % np.around(a, self.bfit.rounding)

        # get default data_id
        if label:
            draw_id = label
        else:
            draw_id = ''

            if self.bfit.draw_style.get() == 'stack':
                ax = self.plt.gca(figstyle)

        # make new window
        style = self.bfit.draw_style.get()
        if style == 'new' or not self.plt.active[figstyle]:
            self.plt.figure(figstyle)
        elif style == 'redraw':
            self.plt.clf(figstyle)

        # get axis
        ax = self.plt.gca(figstyle)

        # set dates axis
        if xdraw in ('Start Time', ):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d (%H:%M)'))
            xvals = np.array([datetime.datetime.fromtimestamp(x) for x in xvals])
            xerrs = None
            ax.tick_params(axis='x', which='major', labelsize='x-small')
        else:
            try:
                ax.get_xaxis().get_major_formatter().set_useOffset(False)
            except AttributeError:
                pass

        if ydraw in ('Start Time', ):
            ax.yaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d (%H:%M)'))
            yvals = mdates.epoch2num(yvals)
            yerrs = None
            ax.tick_params(axis='y', which='major', labelsize='x-small')
        else:
            try:
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
            except AttributeError:
                pass

        # remove component label
        ncomp = self.n_component.get()
        xsuffix = ''
        ysuffix = ''
        
        if ncomp > 1:

            fn_params = self.fitter.gen_param_names(self.fit_function_title.get(), ncomp)
                        
            if xdraw in fn_params or 'Beta-Avg 1/<T1>' in xdraw or 'T1' in xdraw:
                spl = xdraw.split('_')
                xdraw = '_'.join(spl[:-1])
                xsuffix = ' [%s]' % spl[-1]

            if ydraw in fn_params or 'Beta-Avg 1/<T1>' in ydraw or 'T1' in ydraw:
                spl = ydraw.split('_')
                ydraw = '_'.join(spl[:-1])
                ysuffix = ' [%s]' % spl[-1]
             
        # pretty labels
        xdraw = self.fitter.pretty_param.get(xdraw, xdraw)
        ydraw = self.fitter.pretty_param.get(ydraw, ydraw)

        # add suffix for multiple labels
        xdraw = xdraw + xsuffix
        ydraw = ydraw + ysuffix

        # attempt to insert units and scale
        unit_scale, unit = self.bfit.units.get(self.mode, [1, ''])
        if '%s' in xdraw:
            xdraw = xdraw % unit
            xvals *= unit_scale
            xerrs_h *= unit_scale
            xerrs_l *= unit_scale
        if '%s' in ydraw:
            ydraw = ydraw % unit
            yvals *= unit_scale
            yerrs_h *= unit_scale
            yerrs_l *= unit_scale

        # check for nan errors
        if all(np.isnan(xerrs_h)): xerrs_h = None
        if all(np.isnan(xerrs_l)): xerrs_l = None
        if all(np.isnan(yerrs_h)): yerrs_h = None
        if all(np.isnan(yerrs_l)): yerrs_l = None

        if xerrs_h is None and xerrs_l is None:     xerr = None
        else:                                       xerr = (xerrs_l, xerrs_h)
        if yerrs_h is None and yerrs_l is None:     yerr = None
        else:                                       yerr = (yerrs_l, yerrs_h)

        # draw
        f = self.plt.errorbar(  figstyle,
                                draw_id,
                                xvals,
                                yvals,
                                xerr = xerr,
                                yerr = yerr,
                                label=draw_id,
                                annot_label=mouse_label,
                                **self.bfit.style)
        self._annotate(draw_id, xvals, yvals, ann, color=f[0].get_color(), unique=False)

        # format date x axis
        if xerrs is None:   self.plt.gcf(figstyle).autofmt_xdate()
        
        # plot elements
        self.plt.xlabel(figstyle, xdraw)
        self.plt.ylabel(figstyle, ydraw)
        self.plt.tight_layout(figstyle)

        if draw_id:
            self.plt.legend(figstyle, fontsize='x-small')

        # bring window to front
        raise_window()
        
    # ======================================================================= #
    def export(self, savetofile=True, filename=None):
        """Export the fit parameter and file headers"""
        # get values and errors
        val = {}

        for v in self.xaxis_combobox['values']:
            if v == '': continue

            try:
                v2 = self.get_values(v)

            # value not found
            except (KeyError, AttributeError):
                continue

            # if other error, don't crash but print the result
            except Exception:
                traceback.print_exc()
            else:
                val[v] = v2[0]

                if type(v2[1]) is tuple:
                    val['Error- '+v] = v2[1][0]
                    val['Error+ '+v] = v2[1][1]
                else:
                    val['Error '+v] = v2[1]

        # get fixed and shared, if fitted
        keylist = []
        for k, line in self.fit_lines.items():
            keylist.append(k)
            data = line.data
            
            if not all(data.fitpar['res'].isna()):
            
                for kk in data.fitpar.index:
                    
                    name = 'fixed '+kk
                    if name not in val.keys(): val[name] = []
                    val[name].append(data.fitpar.loc[kk, 'fixed'])
                    
                    name = 'shared '+kk
                    if name not in val.keys(): val[name] = []
                    val[name].append(data.fitpar.loc[kk, 'shared'])

        # make data frame for output
        df = pd.DataFrame(val)
        df.set_index('Run Number', inplace=True)

        # drop completely empty columns
        bad_cols = [c for c in df.columns if all(df[c].isna())]
        for c in bad_cols:
            df.drop(c, axis='columns', inplace=True)

        if savetofile:

            # get file name
            if filename is None:
                filename = filedialog.asksaveasfilename(filetypes=[('csv', '*.csv'),
                                                                   ('allfiles', '*')],
                                                    defaultextension='.csv')
                if not filename:    
                    return
            self.logger.info('Exporting parameters to "%s"', filename)

            # check extension
            if os.path.splitext(filename)[1] == '':
                filename += '.csv'

            # write header
            data = self.bfit.data[list(self.fit_lines.keys())[0]]

            if hasattr(data, 'fit_title'):
                header = ['# Fit function : %s' % data.fit_title,
                          '# Number of components: %d' % data.ncomp,
                          '# Global Chi-Squared: %s' % self.gchi_label['text']
                          ]
                          
                # add constrained equations to header
                if self.pop_fitconstr.defined:
                    head2 = ['# ',
                             '# Constrained parameters',
                             ]
                    header.extend(head2)
                    
                    for d, e in zip(self.pop_fitconstr.defined, self.pop_fitconstr.eqn):
                        header.append('# {defi} = {eqn}'.format(defi=d, eqn=e))
                    
            else:
                header = []

            header.extend(['#\n# Generated by bfit v%s on %s' % (__version__, datetime.datetime.now()),
                          '#\n#\n'])

            with open(filename, 'w') as fid:
                fid.write('\n'.join(header))

            # write data
            df.to_csv(filename, mode='a+')
            self.logger.debug('Export success')
        else:
            self.logger.info('Returned exported parameters')
            return df

    # ======================================================================= #
    def export_fit(self, savetofile=True, directory=None):
        """Export the fit lines as csv files"""

        # filename
        filename = self.bfit.fileviewer.default_export_filename
        filename = '_fit'.join(os.path.splitext(filename))

        if directory is None:
            directory = filedialog.askdirectory()
            if not directory:
                return
        
        filename = os.path.join(directory, filename)

        # asymmetry type
        asym_mode = self.bfit.get_asym_mode(self)

        # get data and write
        for id in self.fit_lines.keys():

            # get data
            data = self.bfit.data[id]
            t, a, da = data.asym(asym_mode)

            # get fit data
            fitx = np.linspace(min(t), max(t), self.n_fitx_pts)

            try:
                fit_par = data.fitpar.loc[data.parnames, 'res']
            except AttributeError:
                continue
            dfit_par_l = data.fitpar.loc[data.parnames, 'dres-']
            dfit_par_h = data.fitpar.loc[data.parnames, 'dres+']
            fity = data.fitfn(fitx, *fit_par)

            if data.mode in self.bfit.units:
                unit = self.bfit.units[data.mode]
                fitxx = fitx*unit[0]
                xlabel = self.bfit.xlabel_dict[self.mode] % unit[1]
            else:
                fitxx = fitx
                xlabel = self.bfit.xlabel_dict[self.mode]

            # write header
            fname = filename%(data.year, data.run)
            header = ['# %s' % data.id,
                      '# %s' % data.title,
                      '# Fit function : %s' % data.fit_title,
                      '# Number of components: %d' % data.ncomp,
                      '# Rebin: %d' % data.rebin.get(),
                      '# Bin Omission: %s' % data.omit.get().replace(
                                self.bfit.fetch_files.bin_remove_starter_line, ''),
                      '# Chi-Squared: %f' % data.chi,
                      '# Parameter names: %s' % ', '.join(data.parnames),
                      '# Parameter values: %s' % ', '.join(list(map(str, fit_par))),
                      '# Parameter errors (-): %s' % ', '.join(list(map(str, dfit_par_l))),
                      '# Parameter errors (+): %s' % ', '.join(list(map(str, dfit_par_h))),
                      '#',
                      '# Generated by bfit v%s on %s' % (__version__, datetime.datetime.now()),
                      '#']

            with open(fname, 'w') as fid:
                fid.write('\n'.join(header) + '\n')

            # write data
            df = pd.DataFrame({xlabel:fitx, 'asymmetry':fity})
            df.to_csv(fname, index=False, mode='a+')
            self.logger.info('Exporting fit to %s', fname)

    # ======================================================================= #
    def get_values(self, select):
        """ Get plottable values from all runs"""
        
        data = self.bfit.data
        dlines = self.bfit.fetch_files.data_lines

        # draw only selected runs
        runs = [dlines[k].id for k in dlines if dlines[k].check_state.get()]
        runs.sort()

        self.logger.debug('Fetching parameter %s', select)
        
        # get values
        out = np.array([data[r].get_values(select) for r in runs], dtype=object)
        
        val = out[:, 0]
        err = np.array(out[:, 1].tolist())
        if len(err.shape) > 1: 
            err = (err[:, 0], err[:, 1])
        
        return (val, err)
        
    # ======================================================================= #
    def input_enable_disable(self, parent, state, first=True):
        """
            Prevent input while fitting by disabling options

            state: "disabled" or "normal"
            first: do non-recursive items (i.e. menus, tabs)
        """

        if first:

            # disable tabs
            self.bfit.notebook.tab(1, state=state)

            # disable menu options
            file = self.bfit.menus['File']
            file.entryconfig("Run Commands", state=state)
            file.entryconfig("Export Fits", state=state)
            file.entryconfig("Save State", state=state)
            file.entryconfig("Load State", state=state)

            settings = self.bfit.menus['Settings']
            settings.entryconfig("Probe Species", state=state)

            draw_mode = self.bfit.menus['Draw Mode']
            draw_mode.entryconfig("Use NBM in asymmetry", state=state)
            draw_mode.entryconfig("Draw 1f/1x as PPM shift", state=state)

            self.bfit.menus['menubar'].entryconfig("Minimizer", state=state)

        # disable everything in fit_tab
        for child in parent.winfo_children():
            
            # exceptions
            if child in (self.xaxis_combobox,
                         self.yaxis_combobox,
                         self.annotation_combobox,
                         self.par_label_entry):
                continue
            
            
            # disable
            try:
                if state == 'disabled':
                    child.old_state = child['state']
                    child.configure(state=state)
                else:
                    child.configure(state=child.old_state)
            except (TclError, AttributeError):
                pass
            self.input_enable_disable(child, state=state, first=False)

    # ======================================================================= #
    def return_binder(self):
        """
            Binding to entery key press, depending on focus.

            FOCUS                   ACTION

            comboboxes or buttons   draw_param
                in right frame
            else                    do_fit
        """

        # get focus
        focus = self.bfit.root.focus_get()

        # right frame items
        draw_par_items = (  self.xaxis_combobox,
                            self.yaxis_combobox,
                            self.annotation_combobox,
                            self.par_label_entry)

        # do action
        if focus in draw_par_items:
            self.draw_param()
        elif focus == self.n_component_box:
            self.populate_param(force_modify=True)
        elif focus == self.bfit.root:
            pass
        else:
            self.do_fit()

    # ======================================================================= #
    def set_lines(self, pname, col, value, skipline=None):
        """
            Modify all input fields of each line to match the altered one
            conditional on self.set_as_group

            pname: string, parameter being changed
            col:   str, column being changed
            value: new value to assign
            skipline: if this line, don't modify
        """
    
        for fitline in self.fit_lines.values():
            
            # trivial case
            if not fitline.lines:
                return
            
            # get line id
            id = [line.pname for line in fitline.lines].index(pname)
            line = fitline.lines[id]
            
            if line == skipline:
                continue
            
            # set 
            line.set(**{col:value})
    
    # ======================================================================= #
    def show_all_results(self):
        """Make a window to display table of fit results"""

        self.logger.info('Launching parameter table popup')

        # get fit results
        df = self.export(savetofile=False)
        popup_show_param(df)

    # ======================================================================= #
    def show_constr_window(self):

        self.logger.info('Launching fit constraints popup')

        p = self.pop_fitconstr

        # don't make more than one window
        if hasattr(p, 'win') and Toplevel.winfo_exists(p.win):
            p.win.lift()
            
        # make a new window, using old inputs and outputs
        else:
            p.show()

    # ======================================================================= #
    def update_param(self, *args):
        """Update all figures with parameters drawn with new fit results"""

        self.logger.info('Updating parameter figures')

        # get list of figure numbers for parameters
        figlist = self.plt.plots['param']

        # set style to redraw
        current_active = self.plt.active['param']
        current_style = self.bfit.draw_style.get()
        self.bfit.draw_style.set('stack')

        # get current labels
        current_xlab = self.xaxis.get()
        current_ylab = self.yaxis.get()

        # get current unit
        unit = self.bfit.units[self.mode]

        # back-translate pretty labels to originals
        ivd = {}
        for  k, v in self.fitter.pretty_param.items():
            
            try:
                v = v % unit[1]
            except TypeError:
                pass    
             
            ivd[v] = k     

        for fig_num in figlist:

            # get figure and drawn axes
            ax = plt.figure(fig_num).axes[0]
            xlab = ax.get_xlabel()
            ylab = ax.get_ylabel()
            
            # remove multi-compoent extension
            try:
                ext_x = xlab.split('[')[1]
            except IndexError:
                ext_x = ''
            else:
                ext_x = ext_x.split(']')[0]
            xlab = xlab.split('[')[0].strip()
            
            try:
                ext_y = ylab.split('[')[1]
            except IndexError:
                ext_y = ''
            else:
                ext_y = ext_y.split(']')[0]
            ylab = ylab.split('[')[0].strip()

            # convert from fancy label to simple label
            xlab = ivd.get(xlab, xlab)
            ylab = ivd.get(ylab, ylab)
            
            # add multi-componet stuff
            if ext_x: xlab += '_%s' % ext_x
            if ext_y: ylab += '_%s' % ext_y
                        
            # set new labels for drawing
            self.xaxis.set(xlab)
            self.yaxis.set(ylab)

            # draw new labels
            self.plt.active['param'] = fig_num
            self.draw_param()

            self.logger.debug('Updated figure %d (%s vs %s)', fig_num, ylab, xlab)

        # reset to old settings
        self.bfit.draw_style.set(current_style)
        self.xaxis.set(current_xlab)
        self.yaxis.set(current_ylab)
        self.plt.active['param'] = current_active
        plt.figure(current_active)
