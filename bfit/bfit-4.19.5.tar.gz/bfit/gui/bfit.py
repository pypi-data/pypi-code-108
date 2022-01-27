#!/usr/bin/python3
# Fit and draw BNMR data 
# Derek Fujimoto
# November 2017

from tkinter import *
from tkinter import ttk, filedialog, messagebox
from bdata import bdata, bmerged
from scipy.optimize import curve_fit

try:
    import matplotlib as mpl
except ImportError:
    pass

try:
    from mpl_toolkits.mplot3d import Axes3D
except ImportError as errmsg:
    print('No 3D axes drawing available')
    print(errmsg)

import sys, os, datetime, textwrap, yaml
import webbrowser, subprocess, importlib, logging, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bdata as bd
import weakref as wref

from multiprocessing import Queue
import queue

from bfit import __version__, logger_name, icon_path
from bfit.gui.tab_fileviewer import fileviewer
from bfit.gui.tab_fetch_files import fetch_files
from bfit.gui.tab_fit_files import fit_files
from bfit.gui.calculator_nqr_B0 import calculator_nqr_B0
from bfit.gui.calculator_nqr_B0_hh6 import calculator_nqr_B0_hh6
from bfit.gui.calculator_nmr_B1 import calculator_nmr_B1
from bfit.gui.calculator_nmr_atten import calculator_nmr_atten
from bfit.gui.popup_drawstyle import popup_drawstyle
from bfit.gui.popup_deadtime import popup_deadtime
from bfit.gui.popup_redraw_period import popup_redraw_period
from bfit.gui.popup_terminal import popup_terminal
from bfit.gui.popup_units import popup_units
from bfit.gui.popup_set_ppm_reference import popup_set_ppm_reference
from bfit.gui.popup_ongoing_process import popup_ongoing_process
from bfit.gui.popup_set_histograms import popup_set_histograms
from bfit.backend.PltTracker import PltTracker
from bfit.backend.fitdata import fitdata
import bfit.backend.colors as colors

# interactive plotting
plt.ion()

# filter warnings related to new dkeys on read
warnings.simplefilter('ignore', bd.exceptions.DkeyWarning)
    

__doc__="""
    BNMR/BNQR data visualization and curve fitting.
    
    Hotkeys:
    
        General
            Command-------------Effect
            ctrl+n:             set draw mode "new"
            ctrl+s:             set draw mode "stack"
            ctrl+r:             set draw mode "redraw"
    
        File Details
            Command-------------Effect
            return:             fetch file
            ctrl+return:        draw file
            shift+return:       draw file
            ctrl+a:             toggle check all
        Fit 
            Fetch Data
                Command---------Focus-----------------------Effect    
                return:         run/year entry:             fetch
                                SLR rebin:                  set checked
                                bin omit entry (checked):   set checked
                ctrl+return:                                draw file
                shift+return:                               draw file
                
            Fit Data
            
        View Fit Results
    
    Derek Fujimoto
    November 2017
    """

# =========================================================================== #
class bfit(object):
    """
        Build the mainframe and set up the runloop for the tkinter GUI. 
        
        Data Fields:
            asym_dict_keys: asym calc and draw types
            bnmr_data_dir:  string, directory for bnmr data
            bnqr_data_dir:  string, directory for bnqr data
            data:           dict of fitdata objects for drawing/fitting, keyed by run #
            deadtime:       float, value of deadtime in s or scaling for local calcs
            deadtime_switch:BooleanVar, if true, use deadtime correction
            deadtime_global:BooleanVar, if true, deadtime value is dt, else is scaling
            draw_style:     StringVar, draw window types # stack, redraw, new
            draw_components:list of titles for labels, options to export, draw.
            draw_fit:       BooleanVar, if true draw fits after fitting
            draw_ppm:       BoolVar for drawing as ppm shift
            draw_rel_peak0: BoolVar for drawing frequencies relative to peak0
            draw_standardized_res: BoolVar for drawing residuals as standardized
            norm_with_param:BoolVar, if true estimate normalization from data only
            hist_select:    histogram selection for asym calcs (blank for defaults)
            label_default:  StringVar() name of label defaults for fetch
            logger:         logging object 
            logger_name:    string of unique logger name
            mainframe:      main frame for the object
            menus:          dict {title: Menu} of menubar options
            minimizer:      StringVar: path to python module with fitter object
            notebook:       contains all tabs for operations:
                fileviewer
                fetch_files
                fit_files
            plt:            PltTracker for tracking figures
            ppm_reference:  reference freq in Hz for ppm calulations
            probe_species:  StringVar() name of probe species, bdata.life key.
            root:           tkinter root instance
            rounding:       number of decimal places to round results to in display
            routine_mod:    module with fitting routines
            style:          dict, drawing styles
            thermo_channel: StringVar for tracking how temperature is calculated
            units:          dict:(float, str). conversion rate from original to display units
            update_period:  int, update spacing in s. 
            use_nbm:        BooleanVar, use NBM in asym calculations
            
    """
    bnmr_archive_label = "BNMR_ARCHIVE"
    bnqr_archive_label = "BNQR_ARCHIVE"
    rounding = 3       # number of significant figures to round results to in display
    norm_alph_diff_time = 0.1   # number of seconds to take average over when 
                                # normalizing alpha diffusion runs
    legend_max_draw = 8 # max number of items to draw before removing the legend
    
    # csymmetry calculation options
    asym_dict_keys = {'20':["Combined Helicity", 
                            "Split Helicity", 
                            "Combined Normalized", 
                            "Matched Helicity", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1f':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Shifted Split", 
                            "Shifted Combined", 
                            "Combined Normalized", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1x':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Shifted Split", 
                            "Shifted Combined", 
                            "Combined Normalized", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1n':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Matched Peak Finding", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1e':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1d':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1c':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '1w':["Combined Helicity", 
                            "Split Helicity", 
                            "Raw Scans", 
                            "Shifted Split", 
                            "Shifted Combined", 
                            "Combined Normalized", 
                            "Histograms", 
                            "Positive Helicity", 
                            "Negative Helicity", 
                            ], 
                      '2e':["Combined Hel Slopes", 
                            "Combined Hel Diff", 
                            "Combined Hel Raw", 
                            "Split Hel Slopes", 
                            "Split Hel Diff", 
                            "Split Hel Raw", 
                            "Split Slopes Shifted", 
                            "Split Diff Shifted", 
                            "Split Raw Shifted", 
                            ], 
                      '2h':["Combined Helicity", 
                            "Split Helicity", 
                            "Combined Normalized", 
                            "Positive Helicity", 
                            "Alpha Diffusion", 
                            "Alpha Diff Normalized", 
                            "Combined Hel (Alpha Tag)", 
                            "Split Hel (Alpha Tag)", 
                            "Combined Hel (!Alpha Tag)", 
                            "Split Hel (!Alpha Tag)", 
                            "Histograms", 
                            "Negative Helicity", 
                            "Matched Helicity", 
                            ]}
    
    # asymmetry calculation codes
    asym_dict = {"Combined Helicity"        :'c', 
                 "Split Helicity"           :'h', 
                 "Positive Helicity"        :'p', 
                 "Negative Helicity"        :'n', 
                 "Forward Counter"          :'fc', 
                 "Backward Counter"         :'bc', 
                 "Right Counter"            :'rc', 
                 "Left Counter"             :'lc', 
                 "Matched Helicity"         :'hm', 
                 "Shifted Split"            :'hs', 
                 "Shifted Combined"         :'cs', 
                 "Combined Normalized"      :'cn',
                 "Matched Peak Finding"     :'hp', 
                 "Raw Scans"                :'r', 
                 "Histograms"               :'rhist', 
                 "Combined Hel Raw"         :'raw_c', 
                 "Combined Hel Slopes"      :'sl_c', 
                 "Combined Hel Diff"        :'dif_c', 
                 "Split Hel Raw"            :'raw_h', 
                 "Split Hel Slopes"         :'sl_h', 
                 "Split Hel Diff"           :'dif_h', 
                 "Split Raw Shifted"        :'raw_hs', 
                 "Split Slopes Shifted"     :'sl_hs', 
                 "Split Diff Shifted"       :'dif_hs', 
                 "Alpha Diffusion"          :'ad', 
                 "Alpha Diff Normalized"    :'adn', 
                 "Combined Hel (Alpha Tag)" :"at_c", 
                 "Split Hel (Alpha Tag)"    :"at_h", 
                 "Combined Hel (!Alpha Tag)":"nat_c", 
                 "Split Hel (!Alpha Tag)"   :"nat_h", 
                 }
    
    # valid thermometer channels to read from
    thermo_keys = ('A', 'B', '(A+B)/2')
    
    # draw axis labels
    xlabel_dict={'20':"Time (%s)", 
                 '2h':"Time (%s)", 
                 '2e':'Frequency (%s)', 
                 '1f':'Frequency (%s)', 
                 '1x':'Frequency (%s)', 
                 '1w':'x Parameter (%s)', 
                 '1e':'Field (G)', 
                 '1d':'Laser Power', 
                 '1c':'Camp Variable', 
                 '1n':'Voltage (%s)'}
                 
    ylabel_dict={'ad':r'$N_\alpha~/~N_\beta$', # otherwise, label as Asymmetry
                 'adn':r'$N_\alpha~~N_\beta$', 
                 'hs':r'$\mathcal{A}~-~\mathcal{A}(\nu_\mathrm{max}$)', 
                 'cs':r'$\mathcal{A}~-~\mathcal{A}(\nu_\mathrm{max}$)', 
                 'csf':r'$\mathcal{A}~-$ Baseline', 
                 'cn1':r'$\mathcal{A}~/~\mathcal{A}(\nu_\mathrm{max}$)', 
                 'cn1f':r'$\mathcal{A}$ / Baseline', 
                 'cn2':r'$\mathcal{A}~/~\mathcal{A}(t_\mathrm{min}$)', 
                 'cn2f':r'$\mathcal{A}$ / Amplitude', 
                 'rhist':'Counts'}
    
    # histogram names for x axis
    x_tag={'20':"time_s", 
           '2h':"time_s", 
           '2e':"time", 
           '1f':'freq', 
           '1x':'freq', 
           '1w':'xpar', 
           '1d':'las', 
           '1e':'mA', 
           '1c':'camp', 
           '1n':'mV'}
    
    # minimizers
    minimizers = {'curve_fit (trf)':'bfit.fitting.fitter_curve_fit', 
                  'migrad (hesse)':'bfit.fitting.fitter_migrad_hesse', 
                  'migrad (minos)':'bfit.fitting.fitter_migrad_minos', 
                  }
    
    # define draw componeents in draw_param and labels
    draw_components = ('Temperature (K)', '1000/T (1/K)', 'Impl. Energy (keV)', 
                       'Platform Bias (kV)', 'Run Number', 'B0 Field (T)', 
                       'Unique Id', 'Sample', 'RF Level DAC', 'Chi-Squared', 
                       'Run Duration (s)', 'Start Time', 'Title', 'Year', 
                       'Cryo Lift Set (mm)', 'Cryo Lift Read (mm)', 
                       'He Mass Flow', 'CryoEx Mass Flow', 'Needle Set (turns)', 
                       'Needle Read (turns)', 'Laser Power (V)', 'Laser Wavelength (nm)', 
                       'Laser Wavenumber (1/cm)', 'Target Bias (kV)', 'NBM Rate (count/s)', 
                       'Sample Rate (count/s)', 'NBM Counts', 'Sample Counts')
        
    # ======================================================================= #
    def __init__(self, testfn=None, commandline=False):
        """
            testfn: if not none, expect a function handle with input self to run
                    automate setting parameters, button pushes, etc for rapid 
                    testing
            commandline:    if True leave user in interactive mode with no mainloop running
        """
        # logging
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing v%s' % __version__ + '-'*50)
        self.logger.info('bdata: v%s' % bd.__version__)
        
        # default settings
        self.update_period = 10  # s
        self.ppm_reference = 41270000 # Hz
        self.hist_select = ''    # histogram selection for asym calculations
        self.use_nbm_settings = {'default':False,
                                 '1n':True}
        self.style = {'linestyle':'None', 
                      'linewidth':mpl.rcParams['lines.linewidth'], 
                      'marker':'.', 
                      'markersize':mpl.rcParams['lines.markersize'], 
                      'capsize':0., 
                      'elinewidth':mpl.rcParams['lines.linewidth'], 
                      'alpha':1., 
                      'fillstyle':'full'}
        
        # units: mode:[conversion rate from original to display units, unit]
        self.units = {  '1f':[1e-6, 'MHz'], 
                        '1x':[1e-6, 'MHz'], 
                        '2e':[1e-6, 'MHz'], 
                        '1w':[1, 'Hz'], 
                        '1n':[0.001, 'V'],
                        '1e':[0.001, 'A'],
                        '20':[1, 's'],
                        '2h':[1, 's'],
                        }
        
        # for fitdata objects        
        self.data = {}   

        # set data directories
        try: 
            self.bnmr_data_dir = os.environ[self.bnmr_archive_label]
            self.bnqr_data_dir = os.environ[self.bnqr_archive_label]
        except(AttributeError, KeyError):
            self.bnmr_data_dir = os.getcwd()
            self.bnqr_data_dir = os.getcwd()
        
        # plot tracker 
        self.plt = PltTracker()
        
        # root 
        root = Tk()
        self.root = root
        root.title("bfit: β-NMR and β-NQR Data Analysis "+\
                   "(version %s)" % __version__)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # styling
        root.option_add('*tearOff', FALSE)
        root.option_add("*Font", colors.font)
        root.option_add("*Background",          colors.background)
        root.option_add("*DisabledBackground",  colors.background)
        root.option_add("*ReadonlyBackground",  colors.readonly)
        root.option_add("*Borderwidth", 2)
        
        # don't change all foregrounds or you will break the filedialog windows
        root.option_add("*Menu*Foreground",     colors.foreground)
        root.option_add("*Spinbox*Foreground",  colors.foreground)
        root.option_add("*Listbox*Foreground",  colors.foreground)
        root.option_add("*Text*Foreground",     colors.foreground)     
        root.option_add("*Scrollbar.Background",colors.foreground)

        root.option_add("*Entry.Foreground",    colors.insertbackground)
        root.option_add("*Entry.Background",    colors.fieldbackground)
        root.option_add("*Entry.HighlightBackground",colors.background)
        root.option_add("*Entry.DisabledBackground",colors.entry_disabled)
        
        ttk_style = ttk.Style()
        ttk_style.configure('.',   font=colors.font, 
                                   background=colors.background, 
                                   foreground=colors.foreground, 
                                   arrowcolor=colors.foreground, 
                                   borderwidth=2)
            
        ttk_style.configure("TEntry", foreground=colors.foreground, 
                                      fieldbackground=colors.fieldbackground)

        ttk_style.map('.', background=[('disabled', colors.background)], 
                           fieldbackground=[('selected', colors.selected)])
                                         
        ttk_style.configure('TNotebook.Tab', padding=[50, 2])
        ttk_style.configure("TNotebook.Tab", background=colors.background)
        ttk_style.map("TNotebook.Tab", background=[("selected", colors.tab)])
        
        ttk_style.map("TCheckbutton", foreground=[('selected', colors.selected), 
                                                 ('disabled', colors.disabled)], 
                                      indicatorcolor=[('selected', colors.selected)])
        ttk_style.map("TRadiobutton", foreground=[('selected', colors.selected), 
                                                  ('disabled', colors.foreground)], 
                                      indicatorcolor=[('selected', colors.selected)])
        ttk_style.map('TCombobox', fieldbackground=[('readonly', colors.background)])
        
        ttk_style.configure('TSpinbox', borderwidth=0, background=colors.background)
        ttk_style.map('TSpinbox', borderwidth=[('selected', 1)])
        
        ttk_style.configure('TProgressbar', 
                            borderwidth=1, 
                            background=colors.background)
        
        # icon
        self.set_icon(root)
            
        # key bindings
        root.bind('<Return>', self.return_binder)             
        root.bind('<KP_Enter>', self.return_binder)
        root.bind('<Control-Key-Return>', self.draw_binder)      
        root.bind('<Control-Key-KP_Enter>', self.draw_binder)
        root.bind('<Shift-Key-Return>', self.draw_binder)
        root.bind('<Shift-Key-KP_Enter>', self.draw_binder)
        
        root.bind('<Control-Key-n>', self.set_style_new)
        root.bind('<Control-Key-s>', self.set_style_stack)
        root.bind('<Control-Key-r>', self.set_style_redraw)
        root.bind('<Control-Key-a>', self.set_check_all)
        
        root.bind('<Control-Key-1>', lambda x: self.set_focus_tab(idn=0))
        root.bind('<Control-Key-2>', lambda x: self.set_focus_tab(idn=1))
        root.bind('<Control-Key-3>', lambda x: self.set_focus_tab(idn=2))
        
        root.bind("<Button-4>", self.scroll_binder) 
        root.bind("<Button-5>", self.scroll_binder)
        
        root.bind("<Control-Key-o>", lambda x: self.load_state())
        
        # event bindings
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
                                                        
        # main frame
        mainframe = ttk.Frame(root, pad=5)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # nbm variables
        self.nbm_dict = {''  :BooleanVar(),
                         '1n':BooleanVar()}
    
        self.nbm_dict[''].set(False)
        self.nbm_dict['1n'].set(True)
        
        # deadtime switches
        self.deadtime_switch = BooleanVar()
        self.deadtime_switch.set(False)
        self.deadtime_global = BooleanVar()
        self.deadtime_global.set(True)
        self.deadtime = 0 # deadtime in s, or neg asymmetry scaling for deadtime 
                          # calculations, depending on the value of self.global_deadtime
    
        
        # Menu bar options ----------------------------------------------------
        root.option_add('*tearOff', FALSE)
        menubar = Menu(root)
        root['menu'] = menubar
        
        # File
        menu_file = Menu(menubar, title='File')
        menu_file.add_command(label='Search archive', command=self.search_archive)
        menu_file.add_command(label='Run Commands', command=lambda:popup_terminal(wref.proxy(self)))
        menu_file.add_command(label='Export Data', command=self.do_export)
        menu_file.add_command(label='Export Fits', command=self.do_export_fit)
        menu_file.add_command(label='Save State', command=self.save_state)
        menu_file.add_command(label='Load State', command=self.load_state)
        menu_file.add_command(label='Close All Figures', command=self.do_close_all)
        menu_file.add_command(label='Exit', command=sys.exit)
        menubar.add_cascade(menu=menu_file, label='File')
        
        # Settings
        menu_settings = Menu(menubar, title='Settings')
        menubar.add_cascade(menu=menu_settings, label='Settings')
        menu_settings_dir = Menu(menu_settings)
        menu_settings_lab = Menu(menu_settings)
        menu_settings_probe = Menu(menu_settings, selectcolor=colors.selected)
        menu_settings_thermo = Menu(menu_settings, selectcolor=colors.selected)
        
        # Settings cascade commands
        menu_settings.add_cascade(menu=menu_settings_dir, label='Data directory')
        menu_settings.add_command(label='Drawing style', 
                command=self.set_draw_style)
        menu_settings.add_command(label='Histograms', 
                command=self.set_histograms)
        menu_settings.add_cascade(menu=menu_settings_lab, label='Labels default')                
        menu_settings.add_command(label='PPM Reference Frequecy', 
                command=self.set_ppm_reference)
        menu_settings.add_cascade(menu=menu_settings_probe, label='Probe Species')
        menu_settings.add_command(label='Redraw period', 
                command=self.set_redraw_period)
        menu_settings.add_command(label="System matplotlibrc", 
                command=self.set_matplotlib)
        menu_settings.add_cascade(menu=menu_settings_thermo, label='Thermometer Channel')
        menu_settings.add_command(label="Units", 
                command=self.set_units)
        
        # Settings: data directory
        menu_settings_dir.add_command(label="β-NMR", command=self.set_bnmr_dir)
        menu_settings_dir.add_command(label="β-NQR", command=self.set_bnqr_dir)
        
        # Settings: set label default
        self.label_default = StringVar()
        self.label_default.set('Unique Id')
        for dc in sorted(self.draw_components):
            menu_settings_lab.add_radiobutton(label=dc, 
                variable=self.label_default, value=dc, command=self.set_all_labels, 
                selectcolor=colors.selected)
        
        # Settings: set probe species
        self.probe_species = StringVar()
        self.probe_species.set('Li8')
        lifekeys = list(bd.life.keys())
        lifekeys.sort()
        for k in lifekeys:
            if 'err' not in k: 
                menu_settings_probe.add_radiobutton(label=k, 
                        variable=self.probe_species, 
                        value=k, 
                        command=self.set_probe_species)
        
        # Settings: set thermometer channel
        self.thermo_channel = StringVar()
        self.thermo_channel.set(self.thermo_keys[0])
        for k in self.thermo_keys:
            menu_settings_thermo.add_radiobutton(label=k, 
                    variable=self.thermo_channel, 
                    value=k, 
                    command=self.set_thermo_channel)
        
        # calculate
        menu_calculate = Menu(menubar, title='Calculate')
        menubar.add_cascade(menu=menu_calculate, label='Calculate')
        menu_calculate.add_command(label='Deadtime correction', 
                command=self.set_deadtime)
        menu_calculate.add_command(label='NQR B0 (HH3)', command=calculator_nqr_B0)
        menu_calculate.add_command(label='NQR B0 (HH6)', command=calculator_nqr_B0_hh6)
        menu_calculate.add_command(label='NMR B1', command=calculator_nmr_B1)
        menu_calculate.add_command(label='NMR B1 Attenuation', command=calculator_nmr_atten)
        
        # Draw style
        self.draw_style = StringVar()
        self.draw_style.set("stack")
        self.draw_ppm = BooleanVar()
        self.draw_ppm.set(False)
        self.draw_rel_peak0 = BooleanVar()
        self.draw_rel_peak0.set(False)
        self.draw_standardized_res = BooleanVar()
        self.draw_standardized_res.set(True)
        self.use_nbm = self.nbm_dict['']
        self.norm_with_param = BooleanVar()
        self.norm_with_param.set(True)
        self.draw_fit = BooleanVar()
        self.draw_fit.set(True)
        
        menu_draw = Menu(menubar, title='Draw Mode')
        menubar.add_cascade(menu=menu_draw, label='Draw Mode')
        menu_draw.add_radiobutton(label="Draw in new window",
                variable=self.draw_style, value='new', underline=8, 
                selectcolor=colors.selected)
        menu_draw.add_radiobutton(label="Stack in existing window",
                variable=self.draw_style, value='stack', underline=0, 
                selectcolor=colors.selected)
        menu_draw.add_radiobutton(label="Redraw in existing window",
                variable=self.draw_style, value='redraw', underline=0, 
                selectcolor=colors.selected)
        
        menu_draw.add_separator()
        menu_draw.add_checkbutton(label="Draw after fitting",
                variable=self.draw_fit, selectcolor=colors.selected)
        menu_draw.add_checkbutton(label="Normalize with fit results",
                variable=self.norm_with_param, selectcolor=colors.selected)
        menu_draw.add_checkbutton(label="Draw residuals as standardized",
                variable=self.draw_standardized_res, selectcolor=colors.selected)
        menu_draw.add_checkbutton(label="Draw 1f/1x as PPM shift",
                variable=self.draw_ppm, selectcolor=colors.selected, 
                command = lambda : self.set_1f_shift_style('ppm'))
        menu_draw.add_checkbutton(label="Draw 1f/1x relative to peak_0",
                variable = self.draw_rel_peak0, selectcolor = colors.selected,
                command = lambda : self.set_1f_shift_style('peak'))
        
        menu_draw.add_separator()
        menu_draw.add_checkbutton(label="Use NBM in asymmetry", \
                variable=self.nbm_dict[''], selectcolor=colors.selected)        
        
        # Fitting minimizers
        menu_mini = Menu(menubar, title='Minimizer')
        menubar.add_cascade(menu=menu_mini, label='Minimizer')
        
        self.minimizer = StringVar()
        self.minimizer.set(list(self.minimizers.values())[0])
        for k, m in self.minimizers.items():
            menu_mini.add_radiobutton(label=k, \
                    variable=self.minimizer, 
                    value=m, 
                    selectcolor=colors.selected, 
                    command=self.set_fit_routine)
        menu_mini.add_checkbutton(label='Other', \
                variable=self.minimizer, 
                selectcolor=colors.selected, 
                command=self.set_fit_routine_with_popup)
        
        # Help
        menu_help = Menu(menubar, title='Help')
        menubar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='Show help wiki', command=self.help)
        menu_help.add_command(label='Cite bfit', command=self.citation)
        menu_help.add_command(label='Update bfit', command=self.update_bfit)
        menu_help.add_command(label="What's new?", command=self.whatsnew)
        menu_help.add_command(label='Report an issue', command=self.report_issue)

        # load default fitting routines
        self.routine_mod = importlib.import_module(self.minimizer.get())
        
        # Top Notebook: File Viewer, Fit, Fit Viewer -------------------------
        noteframe = ttk.Frame(mainframe, relief='sunken', pad=5)
        notebook = ttk.Notebook(noteframe)
        file_viewer_tab = ttk.Frame(notebook)
        fetch_files_tab = ttk.Frame(notebook)
        fit_files_tab = ttk.Frame(notebook)
        
        notebook.add(file_viewer_tab, text='Inspect')
        notebook.add(fetch_files_tab, text=' Fetch ')
        notebook.add(fit_files_tab,  text='  Fit  ')
        
        # set drawing styles
        notebook.bind("<<NotebookTabChanged>>", self.set_tab_change)
    
        # gridding
        notebook.grid(column=0, row=0, sticky=(N, E, W, S))
        noteframe.grid(column=0, row=0, sticky=(N, E, W, S))
        noteframe.columnconfigure(0, weight=1)
        noteframe.rowconfigure(0, weight=1)
        
        # Notetabs
        self.fileviewer = fileviewer(file_viewer_tab, self)
        self.fetch_files = fetch_files(fetch_files_tab, self)
        self.fit_files = fit_files(fit_files_tab, self)
        
        # set instance variables ---------------------------------------------
        self.mainframe = mainframe
        self.notebook = notebook
        
        # save menus
        self.menus = {'menubar': menubar}
        for child in menubar.winfo_children():
            self.menus[child['title']] = child
            
        # testing
        if testfn is not None: 
            testfn(self)
        
        # logging 
        self.logger.debug('Initialization success. Starting mainloop.')
        
        # runloop
        if commandline:
            root.update_idletasks()
            root.update()
        else:
            self.root.mainloop()
    
    # ======================================================================= #
    def __del__(self):
        if hasattr(self, 'fileviewer'):  del self.fileviewer
        if hasattr(self, 'fetch_files'): del self.fetch_files
        if hasattr(self, 'fitviewer'):   del self.fitviewer
    
        try:
            plt.close('all')
        except ImportError:
            pass
    
    # ======================================================================= #
    def citation(self):
        """Display publication page"""
        self.logger.info('Opening https://joss.theoj.org/papers/10.21105/joss.03598')
        webbrowser.open('https://joss.theoj.org/papers/10.21105/joss.03598')    
    
    # ======================================================================= #
    def do_close_all(self):
        """Close all open figures"""
        plt.close('all')
        for k in self.plt.plots:    self.plt.plots[k] = []
        for k in self.plt.active:   self.plt.active[k] = 0
        
    # ======================================================================= #
    def do_export(self):
        """Export selected files to csv format. Calls the appropriate function 
        depending on what tab is selected. """ 
        
        idx = self.notebook.index('current')
        self.logger.debug('Exporting for notebook index %d', idx)
        if idx == 0:        # data viewer
            self.fileviewer.export()
        elif idx == 1:        # data fetch_files
            self.fetch_files.export()
        elif idx == 2:        # fit viewer
            self.fetch_files.export()
        else:
            pass
    
    # ======================================================================= #
    def do_export_fit(self): self.fit_files.export_fit()
        
    # ======================================================================= #
    def draw_binder(self, *args):
        """
            Switch between various functions of the shift+enter button. 
            Bound to ctrl+enter
        """
        
        idx = self.notebook.index('current')
        self.logger.debug('Drawing for notebook index %d', idx)
        if idx == 0:        # data viewer
            self.fileviewer.draw(figstyle='inspect')
        elif idx == 1:        # data fetch_files
            self.fetch_files.draw_all(figstyle='data')
        elif idx == 2:        # fit viewer
            self.fit_files.draw_param()
        else:
            pass
                 
    # ======================================================================= #
    def export(self, data, filename, rebin=1, omit=''):
        """Export single data file as csv"""
        
        self.logger.info('Exporting single run (%d) as "%s"', data.run, filename)
        
        # settings
        title_dict = {'c':"combined", 
                      'p':"positive_helicity", 
                      'n':"negative_helicity", 
                      'f':'forward_counter', 
                      'b':'backward_counter', 
                      'r':'right_counter', 
                      'l':'left_counter', 
                      'time_s':'time_s', 
                      'freq':"freq_Hz", 
                      'mV':'voltage_mV', 
                      'xpar':'x_parameter'}
                        
        index_list = ['time_s', 'freq_Hz', 'voltage_mV', 'x_parameter'] 
        
        # get asymmetry
        asym = data.asym(hist_select=self.hist_select, omit=omit, 
                         rebin=rebin, nbm=self.use_nbm.get())
        
        # get new keys
        asym_out = {}
        for k in asym.keys():
            
            if len(asym[k]) == 2:
                
                asym_out[title_dict[k]] = asym[k][0]
                asym_out[title_dict[k]+"_err"] = asym[k][1]
            else:
                asym_out[title_dict[k]] = asym[k]
        
        # make pandas dataframe
        df = pd.DataFrame.from_dict(asym_out)
        
        # set index
        for i in index_list:
            if i in asym_out.keys():
                df.set_index(i, inplace=True)
                break
        
        # make header
        header = [  '# %s' % data.id, 
                    '# %s' % data.title, 
                    '# Rebin: %d' % rebin, 
                    '# Bin omission string: "%s"' % omit, 
                    '# Alternate histogram selection string: "%s"' % self.hist_select, 
                    '# Data computed from NBM: %s' % self.use_nbm.get(),
                    '# ', 
                    '# Generated by bfit v%s on %s' % (__version__, datetime.datetime.now()), 
                    '#']
        
        # write to file
        with open(filename, 'w') as fid:
            fid.write('\n'.join(header) + '\n')
            
        try:
            df.to_csv(filename, mode='a+')
        except AttributeError:
            self.logger.exception('Export file write failed')
            pass
    
    # ======================================================================= #
    def get_asym_mode(self, obj):
        """ Get asymmetry calculation type"""
        id_string = obj.asym_type.get()
        return self.asym_dict[id_string]
        
    # ======================================================================= #
    def get_label(self, data):
        """ Get label for plot
            Input: fitdata object. 
        """
        
        # the thing to switch on
        select = self.label_default.get()
        self.logger.debug('Fetching plot label for "%s" (run %d)', select, data.run)
        
        # Data file options
        try:
            if select == 'Temperature (K)':
                label = "%d K" % int(round(data.temperature.mean))
                
            elif select == 'B0 Field (T)':
                if data.field > 0.1:
                    label = "%3.2f T"% np.around(data.field, 2)  # field (Tesla)
                else:
                    label = "%3.2f G" % np.round(data.field*1e4)# field (Gauss)
                
            elif select == 'RF Level DAC':
                label = str(int(data.bd.camp.rf_dac.mean))
                
            elif select == 'Platform Bias (kV)':
                label = "%.2f kV" % np.around(data.bias, 2)
                    
            elif select == 'Impl. Energy (keV)':
                label = "%.2f keV" % np.around(data.bd.beam_kev(), 2)
                
            elif select == 'Run Duration (s)':
                label = "%d s" % int(data.bd.duration)
                
            elif select == 'Run Number':
                label = str(data.run)
                
            elif select == 'Sample':
                label = data.bd.sample
                
            elif select == 'Start Time':
                label = data.bd.start_date
            
            elif select == 'Title':
                label = data.bd.title
                
            elif select == '1000/T (1/K)':
                label = '%3.3f 1/K' % np.around(1000/data.temperature.mean, 2)
                
            elif select == 'Chi-Squared':
                try:
                    label = "%.2f" % np.around(data.chi)
                except(KeyError, AttributeError):
                    label = ""
                
            elif select == 'Year':
                label = '%d' % data.year
            
            elif select == 'Unique Id':
                label = '%s' % data.id
                
            elif 'Cryo Lift Set (mm)' in select:
                label = '%3.2f mm' % np.around(data.bd.camp.clift_set.mean, 2)
                
            elif 'Cryo Lift Read (mm)' in select:
                label = '%3.2f mm' % np.around(data.bd.camp.clift_read.mean, 2)
                
            elif 'He Mass Flow' in select:
                var = 'mass_read' if data.area == 'BNMR' else 'he_read'
                label = '%3.2f' % np.around(data.bd.camp[var].mean, 2)
                
            elif 'CryoEx Mass Flow' in select:
                label = '%3.2f' % np.around(data.bd.camp.cryo_read.mean, 2)
                
            elif 'Needle Set (turns)' in select:
                label = '%3.2f turns' % np.around(data.bd.camp.needle_set.mean, 2)
                
            elif 'Needle Read (turns)' in select:
                label = '%3.2f turns' % np.around(data.bd.camp.needle_pos.mean, 2)
                
            elif 'Laser Power (V)' in select:
                label = '%3.2f' % np.around(data.bd.epics.las_pwr.mean, 2)
                
            elif 'Laser Wavelength (nm)' in select:
                label = '%3.2f' % np.around(data.bd.epics.las_lambda.mean, 2)
                
            elif 'Laser Wavenumber (1/cm)' in select:
                label = '%3.5f' % np.around(data.bd.epics.las_wavenum.mean, 5)
                
            elif 'Target Bias (kV)' in select:
                label = '%3.2f kV' % np.around(data.bd.epics.target_bias.mean, 2)
                
            elif 'NBM Rate (count/s)' in select:
                rate = np.sum([data.hist['NBM'+h].data \
                               for h in ('F+', 'F-', 'B-', 'B+')])/data.duration            
                label = '%3.2f count/s' % np.around(rate, 2)
                
            elif 'Sample Rate (count/s)' in select:
                hist = ('F+', 'F-', 'B-', 'B+') if data.area == 'BNMR' \
                                             else ('L+', 'L-', 'R-', 'R+')
                    
                rate = np.sum([data.hist[h].data for h in hist])/data.duration
                label = '%3.2f count/s' % np.around(rate, 2)
                
            else:
                label = str(data.run)
        except Exception as err:
            label = '%d (Error)' % data.run
            
        return label
    
    # ======================================================================= #
    def get_latest_year(self):
        """Get the year which has the last data set in it."""
        
        # get the current year
        year = datetime.datetime.now().year
        
        # get paths 
        try:
            nmr_path = os.environ[self.bnmr_archive_label]
            nqr_path = os.environ[self.bnqr_archive_label]
        except KeyError:
            nmr_path = os.path.join(bd._mud_data, 'bnmr')
            nqr_path = os.path.join(bd._mud_data, 'bnqr')
        
        # functions to check for data (NMR or NQR)
        no_nmr = lambda y: not os.path.isdir(os.path.join(nmr_path, str(y)))
        no_nqr = lambda y: not os.path.isdir(os.path.join(nqr_path, str(y)))
        
        # check data
        while (no_nmr(year) and no_nqr(year)) and year > 0:
            year -= 1
            
        self.logger.debug('Latest year with data: %d (NMR: %s, NQR: %s)', 
                          year, not no_nmr(year), not no_nqr(year))
        return year
    
    # ======================================================================= #
    def get_run_key(self, data=None, r=-1, y=-1):
        """For indexing data dictionary"""
        
        if type(data) is bdata:
            return '.'.join(map(str, (data.year, data.run)))
        elif type(data) is bmerged:
            runs = textwrap.wrap(str(data.run), 5)
            years = textwrap.wrap(str(data.year), 4)
            return '+'.join(['%s.%s' % (y, r) for y, r in zip(years, runs)])
        elif type(data) is fitdata:
            return data.id
        elif r>0 and y>0:
            return '.'.join(map(str, (y, r)))
        else:
            raise RuntimeError('Bad run key input')
    
    # ======================================================================= #
    def help(self):
        """Display help wiki"""
        self.logger.info('Opening help wiki')
        webbrowser.open('https://github.com/dfujim/bfit/wiki')
    
    # ======================================================================= #
    def load_state(self, filename=None):
        """
            Load the state of the gui
        """

        # get the filename
        if filename is None:
            filename = filedialog.askopenfilename(filetypes=[('yaml', '*.yaml'),
                                                             ('allfiles', '*')])
            if not filename:
                return

        self.logger.info('Loading program state from %s', filename)

        # load the object with the data
        with open(filename, 'r') as fid:
            from_file = yaml.safe_load(fid)

        # clear loaded runs
        fetch_tab = self.fetch_files
        fetch_tab.remove_all()

        # bfit parameters
        self.style = from_file['style']
        self.hist_select = from_file['hist_select']
        self.draw_style.set(from_file['draw_style'])
        self.draw_fit.set(from_file['draw_fit'])
        
        self.probe_species.set(from_file['probe_species'])
        self.set_probe_species()
        
        self.minimizer.set(from_file['minimizer'])
        self.set_fit_routine()
        
        self.norm_with_param.set(from_file['norm_with_param'])
        self.draw_standardized_res.set(from_file['draw_standardized_res'])
        self.use_nbm.set(from_file['use_nbm'])
        self.draw_ppm.set(from_file['draw_ppm'])
        self.draw_rel_peak0.set(from_file['draw_rel_peak0'])
        self.thermo_channel.set(from_file['thermo_channel'])
        self.units = from_file['units']
        self.label_default.set(from_file['label_default'])
        self.ppm_reference = from_file['ppm_reference']
        self.update_period = from_file['update_period']
        self.bnmr_data_dir = from_file['bnmr_data_dir']
        self.bnqr_data_dir = from_file['bnqr_data_dir']
        
        # set deadtime correction
        self.deadtime = from_file['deadtime']
        self.deadtime_switch.set(from_file['deadtime_switch'])
        self.deadtime_global.set(from_file['deadtime_global'])
        
        # fileviewer
        fileviewer_tab = self.fileviewer
        fileviewer_tab.year.set(from_file['fileview_year'])
        fileviewer_tab.runn.set(from_file['fileview_run'])
        
        try:
            fileviewer_tab.get_data()
        except RuntimeError:
            pass
        else:
            fileviewer_tab.asym_type.set(from_file['fileview_asym_type'])
            fileviewer_tab.rebin.set(from_file['fileview_rebin'])
            fileviewer_tab.is_updating.set(from_file['fileview_is_updating'])

        # fetch files
        fetch_files = self.fetch_files
        fetch_files.year.set(from_file['fetch_year'])
        fetch_files.run.set(from_file['fetch_run'])
        fetch_files.check_state.set(from_file['fetch_check_state'])
        fetch_files.check_state_data.set(from_file['fetch_check_state_data'])
        fetch_files.check_state_fit.set(from_file['fetch_check_state_fit'])
        fetch_files.check_state_res.set(from_file['fetch_check_state_res'])
        fetch_files.check_rebin.set(from_file['fetch_check_rebin'])
        fetch_files.check_bin_remove.set(from_file['fetch_check_bin_remove'])
        fetch_files.asym_type.set(from_file['fetch_asym_type'])
        fetch_files.omit_state.set(from_file['fetch_omit_state'])
        fetch_files.base_bins.set(from_file['fetch_base_bins'])
         
        # load selected runs
        data = from_file['data']
        setyear = fetch_tab.year.get()
        setrun =  fetch_tab.run.get()
        for id, d in data.items():
            
            # set year and run and fetch
            fetch_tab.year.set(d['year'])
            fetch_tab.run.set(d['run'])
            fetch_tab.get_data()

            # set corresponding parameters for the run
            d_actual = self.data[id]
            d_actual.omit.set(d['omit'])
            d_actual.omit_scan.set(d['omit_scan'])
            d_actual.check_draw_data.set(d['check_draw_data'])
            d_actual.check_draw_fit.set(d['check_draw_fit'])
            d_actual.check_draw_res.set(d['check_draw_res'])
            d_actual.check_state.set(d['check_state'])
            d_actual.label.set(d['label'])
            d_actual.rebin.set(d['rebin'])
            d_actual.base_bins.set(d['base_bins'])

        # reset year and run input info
        fetch_tab.year.set(setyear)
        fetch_tab.run.set(setrun)
        
        # fit files
        fit_files = self.fit_files
        fit_files.annotation.set(from_file['fit_annotation'])
        fit_files.asym_type.set(from_file['fit_asym_type'])
        fit_files.fit_function_title.set(from_file['fit_fit_function_title'])
        fit_files.n_component.set(from_file['fit_n_component'])
        fit_files.par_label.set(from_file['fit_par_label'])
        fit_files.set_as_group.set(from_file['fit_set_as_group'])
        fit_files.set_prior_p0.set(from_file['fit_set_prior_p0'])
        fit_files.use_rebin.set(from_file['fit_use_rebin'])
        fit_files.xaxis.set(from_file['fit_xaxis'])
        fit_files.yaxis.set(from_file['fit_yaxis'])
        fit_files.xlo.set(from_file['fit_xlo'])
        fit_files.xhi.set(from_file['fit_xhi'])
        fit_files.gchi_label['text'] = from_file['gchi']
        
        # get parameters in fitting page
        fit_files.populate()
        fit_files.populate_param(force_modify=True)

        # constrain
        constr = fit_files.pop_fitconstr
        constr.constraints_are_set = from_file['constr_constraints_are_set']
        
        constr.show()
        constr.entry.insert('1.0', from_file['constr_input_fn_text'])
        constr.get_input()
        
        if constr.constraints_are_set:
            constr.set_constraints()
        else:
            constr.win.destroy()
            constr.win.update()
        
        # set parameter values
        data = self.data
        fitpar_all = from_file['fitpar']
        for id, fitpar in fitpar_all.items():
            
            # make sure dataline checkboxes are active
            fetch_tab.data_lines[id].draw_fit_checkbox['state'] = 'normal'
            fetch_tab.data_lines[id].draw_res_checkbox['state'] = 'normal'

            # get pulse length
            pulse_len = 0
            if '2' in data[id].mode:
                pulse_len = data[id].pulse_s

            # get probe lifetime
            lifetime = bd.life[from_file['probe_species']]

            # get fit function
            fitfn = fit_files.fitter.get_fn(from_file['fit_fit_function_title'],
                                            from_file['fit_n_component'],
                                            pulse_len,
                                            lifetime)

            if '2' in data[id].mode and from_file['probe_species'] == 'Mg31':
                fitfn1 = decay_corrected_fn(fa_31Mg, fitfn, pulse_len)
            else:
                fitfn1 = fitfn

            # set fit results
            fitpar = pd.DataFrame(fitpar)
            data[id].set_fitpar(fitpar)
            data[id].drop_unused_param(fitpar.index)
            data[id].fitfn = fitfn1
            
        fit_files.populate()
        
    # ======================================================================= #
    def on_closing(self):
        """Excecute this when window is closed: destroy and close all plots."""
        self.logger.info('Closing all windows.')
        plt.close('all')
        self.root.destroy()
        self.logger.info('Finished     ' + '-'*50)
    
    # ======================================================================= #
    def report_issue(self):
        """Display github issue page"""
        self.logger.info('Opening github issue page: '+\
                         'https://github.com/dfujim/bfit/issues')
        webbrowser.open('https://github.com/dfujim/bfit/issues')
    
    # ======================================================================= #
    def return_binder(self, *args):
        """Switch between various functions of the enter button. """
        
        idx = self.notebook.index('current')
        self.logger.debug('Calling return key command for notebook index %d', idx)
        if idx == 0:        # data viewer
            self.fileviewer.get_data()
        elif idx == 1:        # data fetch_files
            self.fetch_files.return_binder()
        elif idx == 2:        # fit viewer
            self.fit_files.return_binder()
        else:
            pass
    
    # ======================================================================= #
    def save_state(self, filename=None):
        """
            Save the state of the gui:

            dataline state info
            Fitting function
            Number of components
            Initial inputs
            Fit results
        """

        # final output
        to_file = {}

        # bfit menu options
        to_file['probe_species'] = self.probe_species.get()
        to_file['minimizer'] = self.minimizer.get()
        to_file['norm_with_param'] = self.norm_with_param.get()
        to_file['draw_standardized_res'] = self.draw_standardized_res.get()
        to_file['use_nbm'] = self.use_nbm.get()
        to_file['draw_ppm'] = self.draw_ppm.get()
        to_file['draw_rel_peak0'] = self.draw_rel_peak0.get()
        to_file['thermo_channel'] = self.thermo_channel.get()
        to_file['units'] = self.units
        to_file['label_default'] = self.label_default.get()
        to_file['ppm_reference'] = self.ppm_reference
        to_file['update_period'] = self.update_period
        to_file['deadtime'] = self.deadtime
        to_file['deadtime_switch'] = self.deadtime_switch.get()
        to_file['deadtime_global'] = self.deadtime_global.get()
        to_file['style'] = self.style
        to_file['hist_select'] = self.hist_select
        to_file['draw_style'] = self.draw_style.get()
        to_file['draw_fit'] = self.draw_fit.get()
        to_file['bnmr_data_dir'] = self.bnmr_data_dir
        to_file['bnqr_data_dir'] = self.bnqr_data_dir

        # fileviewer
        fileviewer_tab = self.fileviewer
        to_file['fileview_year'] = fileviewer_tab.year.get()
        to_file['fileview_run'] = fileviewer_tab.runn.get()
        to_file['fileview_asym_type'] = fileviewer_tab.asym_type.get()
        to_file['fileview_rebin'] = fileviewer_tab.rebin.get()
        to_file['fileview_is_updating'] = fileviewer_tab.is_updating.get()

        # fetch files
        fetch_files = self.fetch_files
        to_file['fetch_year'] = fetch_files.year.get()
        to_file['fetch_run'] = fetch_files.run.get()
        to_file['fetch_check_state'] = fetch_files.check_state.get()
        to_file['fetch_check_state_data'] = fetch_files.check_state_data.get()
        to_file['fetch_check_state_fit'] = fetch_files.check_state_fit.get()
        to_file['fetch_check_state_res'] = fetch_files.check_state_res.get()
        to_file['fetch_check_rebin'] = fetch_files.check_rebin.get()
        to_file['fetch_check_bin_remove'] = fetch_files.check_bin_remove.get()
        to_file['fetch_asym_type'] = fetch_files.asym_type.get()
        to_file['fetch_base_bins'] = fetch_files.base_bins.get()
        to_file['fetch_omit_state'] = fetch_files.omit_state.get()

        # get state from data
        datalines = fetch_files.data_lines
        data = {}
        for id, d in self.data.items():
            data[id] = {
                    'omit'              :d.omit.get(),
                    'check_draw_data'   :d.check_draw_data.get(),
                    'check_draw_fit'    :d.check_draw_fit.get(),
                    'check_draw_res'    :d.check_draw_res.get(),
                    'check_state'       :d.check_state.get(),
                    'omit_scan'         :d.omit_scan.get(),
                    'id'                :d.id,
                    'label'             :d.label.get(),
                    'rebin'             :d.rebin.get(),
                    'run'               :d.run,
                    'year'              :d.year,
                    'base_bins'         :d.base_bins.get(),
                    }
        to_file['data'] = data

        # fit files
        fit_files = self.fit_files
        to_file['gchi'] = fit_files.gchi_label['text']
        to_file['fit_annotation'] = fit_files.annotation.get()
        to_file['fit_asym_type'] = fit_files.asym_type.get()
        to_file['fit_fit_function_title'] = fit_files.fit_function_title.get()
        to_file['fit_n_component'] = fit_files.n_component.get()
        to_file['fit_par_label'] = fit_files.par_label.get()
        to_file['fit_set_as_group'] = fit_files.set_as_group.get()
        to_file['fit_set_prior_p0'] = fit_files.set_prior_p0.get()
        to_file['fit_use_rebin'] = fit_files.use_rebin.get()
        to_file['fit_xaxis'] = fit_files.xaxis.get()
        to_file['fit_yaxis'] = fit_files.yaxis.get()
        to_file['fit_xlo'] = fit_files.xlo.get()
        to_file['fit_xhi'] = fit_files.xhi.get()
        
        # save constraints
        constr = fit_files.pop_fitconstr
        to_file['constr_constraints_are_set'] = constr.constraints_are_set
        to_file['constr_input_fn_text'] = constr.input_fn_text
        
        # get parameter values from data
        data_values = {id: dat.fitpar.to_dict() for id, dat in self.data.items()}
        to_file['fitpar'] = data_values
            
        # get xlims
        to_file['xlo'] = fit_files.xlo.get()
        to_file['xhi'] = fit_files.xhi.get()

        # save file ----------------------------------------------------------
        if filename is None:
            fid = filedialog.asksaveasfile(mode='w', filetypes=[('yaml', '*.yaml'),
                                                           ('allfiles', '*')],
                                           defaultextension='.yaml')
        else:
            fid = open(filename, 'w')
            
        if fid:
            yaml.dump(to_file, fid)
            fid.close()

        self.logger.info('Saving program state to %s', fid)
    
    # ======================================================================= #
    def scroll_binder(self, event):
        """
            Switch between various functions of the mousewheel button. 
            Bound to <Button-4> and <Button-5>
        """
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            pass
        elif idx == 1:        # data fetch_files
            self.fetch_files.canvas_scroll(event)
        elif idx == 2:        # fit viewer
            self.fit_files.canvas_scroll(event)
        else:
            pass
               
    # ======================================================================= #
    def search_archive(self):  
        self.logger.info('Opening mud archive musr website')
        webbrowser.open('http://musr.ca/mud/runSel.html', new=1)
        
    # ======================================================================= #
    def set_bnmr_dir(self): 
        """Set directory location via environment variable BNMR_ARCHIVE."""
        self.logger.info('Setting BNMR environment directory')
        d = filedialog.askdirectory(parent=self.root, mustexist=True, 
                initialdir=self.bnmr_data_dir)
            
        if type(d) == str:
            self.bnmr_data_dir = d
            os.environ[self.bnmr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"', 
                              self.bnmr_archive_label, d)
        else:
            self.logger.error('Input was not of type string')
            
    # ======================================================================= #
    def set_bnqr_dir(self): 
        """Set directory location via environment variable BNQR_ARCHIVE."""
        self.logger.info('Setting BNQR environment directory')
        d = filedialog.askdirectory(parent=self.root, mustexist=True, 
                initialdir=self.bnqr_data_dir)
        
        if type(d) == str:
            self.bnqr_data_dir = d
            os.environ[self.bnqr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"', 
                              self.bnqr_archive_label, d)
        else:
            self.logger.error('Input was not of type string')
    
    # ======================================================================= #
    def set_fit_routine(self):
        """Set python module for fitting routines"""
        
        self.logger.info('Loading module...')
        self.routine_mod = importlib.import_module(self.minimizer.get())
        
        # repopuate fitter
        self.logger.info('Repopulating fitter...')
        self.fit_files.fitter = self.routine_mod.fitter(
                                    keyfn = self.get_run_key, 
                                    probe_species = self.probe_species.get())
        self.fit_files.fit_routine_label['text'] = self.fit_files.fitter.__name__
        self.fit_files.populate()
        self.logger.debug('Success.')
        
    # ======================================================================= #
    def set_fit_routine_with_popup(self):
        """Set python module for fitting routines"""
        self.logger.info('Setting fitting backend routine')
        d = filedialog.askopenfilename(initialdir = "./", 
                title = "Select fitting routine module", 
                filetypes = (("python modules", "*.py"), 
                             ("cython modules", "*.pyx"), 
                             ("all files", "*.*")))
        
        if type(d) == str:
            
            # empty condition
            if d == '':
                self.logger.error('Input was empty string.')
                return
            
            # get paths
            path = os.path.abspath(d)
            pwd = os.getcwd()
            
            # load the module
            os.chdir(os.path.dirname(path))
            self.minimizer.set(os.path.splitext(os.path.basename(d))[0])
            self.set_fit_routine()
            os.chdir(pwd)
            
        else:
            self.logger.error('Input was not of type string.')    
        
    # ======================================================================= #
    def set_icon(self, window):
        """Set the icon for new windows"""
        try:
            img = PhotoImage(file=icon_path)
            window.tk.call('wm', 'iconphoto', window._w, img)
        except Exception as err:
            print(err)
        
    # ======================================================================= #
    def set_matplotlib(self): 
        """Edit matplotlib settings file, or give info on how to do so."""
        
        self.logger.info('Attempting to edit matplotlibrc file')
        
        # settings
        location = os.path.join(os.environ['HOME'], '.config', 'matplotlib')
        filename = "matplotlibrc"
        weblink = 'http://matplotlib.org/users/customizing.html'+\
                  '#the-matplotlibrc-file'
        
        # check for file existance
        if not os.path.isfile(os.path.join(location, filename)):
            self.logger.debug('File not found.')
            value = messagebox.showinfo(parent=self.mainframe, 
                    title="Get matplotlibrc", \
                    message="No matplotlibrc file found.", 
                    detail="Press ok to see web resource.", 
                    type='okcancel')
            
            if value == 'ok':
                webbrowser.open(weblink)
            return
        
        # if file exists, edit
        self.logger.debug('File found. Opening in external program.')
        subprocess.call(['xdg-open', os.path.join(location, filename)])
            
    # ======================================================================= #
    def set_1f_shift_style(self, clicked_style):
        """
            Ensure that ppm and peak shift modes are not both selected at the
            same time. 
            
            clicked_style: string, one of 'ppm' or 'peak'
        """
        
        if clicked_style == 'ppm':
            self.draw_rel_peak0.set(False)
            
        elif clicked_style == 'peak':
            self.draw_ppm.set(False)
        
    # ======================================================================= #
    def set_all_labels(self, *a):    self.fetch_files.set_all_labels()
    def set_check_all(self, x):  
        self.logger.info('Checking all files')
        state = self.fetch_files.check_state.get()
        self.fetch_files.check_state.set(not state)
        self.fetch_files.check_all()
    def set_deadtime(self):          popup_deadtime(wref.proxy(self))
    def set_draw_style(self):        popup_drawstyle(wref.proxy(self))
    def set_histograms(self, *a):    popup_set_histograms(wref.proxy(self))
    def set_focus_tab(self, idn, *a): self.notebook.select(idn)
    def set_nbm(self, mode):
        """
            Set the nbm variable based on the run mode
        """
            
        # get new nbm BooleanVar
        new_nbm = self.nbm_dict.get(mode, self.nbm_dict[''])
        
        # switch the variable
        menu = self.menus['Draw Mode']
        try:
            idx = menu.index('Use NBM in asymmetry')
        except TclError:
            idx = menu.index('Use NBM in asymmetry (1n)')
        
        menu.entryconfig(idx, variable = new_nbm)
        self.use_nbm = new_nbm
        
        # change the menu label
        if mode == '1n':
            menu.entryconfig(idx, label = 'Use NBM in asymmetry (1n)')
        else:
            menu.entryconfig(idx, label = 'Use NBM in asymmetry')
    def set_ppm_reference(self, *a): popup_set_ppm_reference(wref.proxy(self))
    def set_probe_species(self, *a): 
        species = self.probe_species.get()
        self.fit_files.fitter.probe_species = species
        self.fit_files.probe_label['text'] = species
        self.logger.info('Probe species changed to %s', species)
    def set_redraw_period(self, *a): popup_redraw_period(wref.proxy(self))
    def set_units(self, *a):         popup_units(wref.proxy(self))
    def set_style_new(self, x):      
        self.logger.info('Setting draw style to "new"')
        self.draw_style.set('new')
    def set_style_stack(self, x):    
        self.logger.info('Setting draw style to "stack"')
        self.draw_style.set('stack')
    def set_style_redraw(self, x):   
        self.logger.info('Setting draw style to "redraw"')
        self.draw_style.set('redraw')
    def set_tab_change(self, event):
        
        new_tab = event.widget.index("current")
        
        self.logger.debug('Changing to tab %d', new_tab)
        
        # fileviewer
        if new_tab == 0:
            self.fileviewer.set_nbm()
            
        # fetch files
        elif new_tab == 1:
            self.fetch_files.set_nbm()
            
        # fit files
        elif new_tab == 2:
            self.fit_files.populate()
            
    def set_thermo_channel(self, ):  
        self.fetch_files.update_data()
        self.fileviewer.get_data()
     
    # ======================================================================= #
    def set_asym_calc_mode_box(self, mode, parent, area, *args):
        """Set asym combobox values. Asymmetry calculation and draw modes."""
        
        self.logger.debug('Setting asym combobox values for mode '+\
                         '"%s" and area "%s"', mode, area)
    
        # get list of possible run modes
        try:
            modes = list(self.asym_dict_keys[mode])
        except KeyError as err:
            messagebox.showerror('Error', 'Unknown mode %s' % mode)
            self.logger.exception(str(err))
            raise err from None
        
        # prune the list to match only ok files
        if parent == self.fit_files:
            modes = [m for m in modes if self.asym_dict[m] in \
                                        self.fit_files.fitter.valid_asym_modes]
    
        # add single counter asymetries based on mode and type
        if mode != '2e':
            if 'BNMR' in area:
                modes.extend(['Forward Counter', 'Backward Counter'])
            if 'BNQR' in area:
                modes.extend(['Left Counter', 'Right Counter'])
            
        # selection: switch if run mode not possible
        if parent.asym_type.get() not in modes:
            parent.asym_type.set(modes[0])
        
        # set list
        parent.entry_asym_type['values'] = modes
        
    # ======================================================================= #
    def update_bfit(self):
        """Check pip for updated version"""
        
        self.logger.info('Using pip to update')
        
        # set up queue to get signal
        que = Queue()
        
        # run update function
        def do_update():
            try:
                subprocess.call([sys.executable, "-m", "pip", "install", 
                                 "--user", "--upgrade", 'bfit'])
            except subprocess.CalledProcessError:
                que.put('Error')
            else:
                que.put('Success')
        
        popup = popup_ongoing_process(self, 
                            target = do_update,
                            message="Updating bfit...", 
                            queue = que)
        output = popup.run()
        
        # end update
        if output == 'Error':
            messagebox.showerror("Error", 'Update error. Use command line to update.')
        elif output == 'Success':
            messagebox.showinfo("Success", 'Close window and restart bfit to implement updates.')
        else:
            return
     
    # ======================================================================= #
    def whatsnew(self):
        """Display releases page"""
        self.logger.info('Opening https://github.com/dfujim/bfit/releases')
        webbrowser.open('https://github.com/dfujim/bfit/releases')
        
# =========================================================================== #
if __name__ == "__main__":
    bfit()

