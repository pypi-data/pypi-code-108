# Drawing style window
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
import numpy as np
from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.gui.tab_fileviewer import num_prefix
import bfit.backend.colors as colors
import matplotlib as mpl
import bdata as bd
import pandas as pd
import webbrowser
import logging
from functools import partial
import matplotlib.pyplot as plt


# ========================================================================== #
class popup_prepare_data(object):
    """
        Popup window for preparing data for fitting. 
        
        Data fields:
        
        bfit:               bfit object
        checkbutton_state:  Checkbutton, linked to bdfit.check_state

        data:               fitdata object
        entry_label:        ttk.Entry, set run label
        label_flatten_base: ttk.Label for flattening the baseline
        omit_scan:          BooleanVar, if true, omit last scan from asym calc
        flatten_base:       IntVar, if >0, flatten the baseline using this many bins
        flatten_over:       BooleanVar, if true, apply baseline overcorrection in flatten
    """

    # ====================================================================== #
    def __init__(self, bfit, data):
        """
            bfit: bfit object
            checkbutton_state: checkbutton for state activated/deactivated
            data: fitdata object
            
            entry_label: Entry obj input run label
            
            win: Toplevel
        """
        
        # set variables
        self.bfit = bfit    # fit_files pointer
        self.data = data
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Prepare %s for fitting' % data.get_values('Unique Id')[0])
        topframe = ttk.Frame(self.win, relief='sunken', pad=5)

        # icon
        self.bfit.set_icon(self.win)

        # show file details ---------------------------------------------------
        frame_details = ttk.Labelframe(topframe, pad=5, text='File Details')
        
        r = 0
        keys = (('Unique Id', '', ''), 
                ('Title', '', ''), 
                ('Temperature (K)',    'T    = ', ' K'), 
                ('B0 Field (T)',       'B0   = ', ' T'), 
                ('Platform Bias (kV)', 'Bias = ', ' kV'), 
                ('Run Duration (s)', 'Duration: ', ''),
                ('Sample Counts', 'Sample Counts: ', ''))
        for key, label, unit in keys:
            
            if key not in ('Sample Counts',):
                val, err = data.get_values(key)
            
            # prep output string
            if key == 'Run Duration (s)':
                
                text = '%s%d:%d' % (label, int(val/60), val%60)

            elif key == 'Sample Counts':
                
                hist = ('F+', 'F-', 'B-', 'B+') if data.area.upper() == 'BNMR' \
                                     else ('L+', 'L-', 'R-', 'R+')

                val = int(np.sum([data.hist[h].data for h in hist]))
                val, unit = num_prefix(val)
                text = '%s%.3g%s' % (label, val, unit)    
                
            else:
                if type(val) not in (str, np.str_) :
                    val = '%.3f' % val
                
                text = '%s%s%s' % (label, val, unit)
            
            # set label in window
            label = ttk.Label(frame_details, text=text, justify=LEFT)
            label.grid(column=0, row=r, sticky='nw')
            r += 1
                
        # run label
        frame_label = ttk.Frame(frame_details)
        label_label = ttk.Label(frame_label, text='Label:', justify=LEFT)
        self.entry_label = Entry(frame_label, textvariable=self.data.label, width=18)
        self.entry_label.bind('<KeyRelease>', self.ungray_label)
        button_label = ttk.Button(frame_label, text='Reset to default', 
                                    command=self.reset_label, pad=1)
        
        # inspect button
        button_inspect = ttk.Button(frame_details, text='Inspect', 
                                    command=self.inspect, pad=1)
        
        # grid 
        label_label.grid(column=0, row=0, sticky='w')
        self.entry_label.grid(column=1, row=0, sticky='w')
        button_label.grid(column=2, row=0, sticky='w', padx=5)
        frame_label.grid(column=0, row=r, sticky='new'); r+=1
        button_inspect.grid(column=0, row=r, sticky='sew', padx=5, pady=5)
        frame_details.grid_rowconfigure(r, weight=1)
        
        # mode ----------------------------------------------------------------
        mode_text = self.bfit.fetch_files.runmode_relabel[self.data.mode]
        mode_text = mode_text.split('(')[0] + '(%s)' % self.data.mode
        frame_mode = ttk.Labelframe(topframe, text='Run Mode', pad=5)
        label_mode = ttk.Label(frame_mode, text=mode_text, justify=LEFT)
        label_mode.grid(column=0, row=0, sticky='nw')
        
        # include in fit ------------------------------------------------------
        frame_state = ttk.Labelframe(topframe, text='State', pad=5)
        self.checkbutton_state = ttk.Checkbutton(frame_state, text='Active', 
                variable=self.data.check_state, onvalue=True, offvalue=False, pad=5,
                command=self.config_checkbutton_state)
        self.config_checkbutton_state()
        self.checkbutton_state.grid(column=0, row=0)
        
        # rebin ---------------------------------------------------------------
        frame_rebin = ttk.Labelframe(topframe, text='Misc Options', pad=5)
        label_rebin = ttk.Label(frame_rebin, text='Rebin:')
        spin_rebin = Spinbox(frame_rebin, from_=0, to=100,
                             width=3,
                             textvariable=self.data.rebin)
        checkbutton_flip = ttk.Checkbutton(frame_rebin, text='Flip asymmetry (a -> -a)', 
                variable=self.data.flip_asym, onvalue=True, offvalue=False, pad=5)
        
        label_rebin.grid(column=0, row=0, padx=5, pady=5)
        spin_rebin.grid(column=1, row=0, padx=5, pady=5)
        checkbutton_flip.grid(column=2, row=0, padx=5, pady=5)
        
        # scan repair ---------------------------------------------------------
        frame_scan = ttk.Labelframe(topframe, text='Scan Repair', pad=5)
        
        # omit bins
        label_omit = ttk.Label(frame_scan, text='Remove bins:')
        entry_omit = Entry(frame_scan, textvariable=self.data.omit, width=25)
        button_omit = ttk.Button(frame_scan, text='Draw raw uncorrected', command=self.draw_raw)
        
        # omit last scan
        checkbutton_omit_scan = ttk.Checkbutton(frame_scan, text='Omit final scan if incomplete', 
                variable=self.data.omit_scan, onvalue=True, offvalue=False, pad=5,
                command=self.set_bin_repair)
        
        # flatten baseline
        self.label_flatten_base = ttk.Label(frame_scan, 
                                      text='Flatten baseline using N end bins. N = ')
        spin_flatten_base = Spinbox(frame_scan, from_=0, to=1000,
                                        width=4,
                                        textvariable=self.data.base_bins)
        spin_flatten_base.bind("<KeyRelease>", self.set_bin_repair)
        spin_flatten_base.bind("<Leave>", self.set_bin_repair)
 
        frame_draw_corrected = ttk.Labelframe(frame_scan, text='Draw Correction', pad=5)
        button_draw_raw_flat = ttk.Button(frame_draw_corrected, text='Raw', 
                                    command=lambda: self.draw_compare(draw_style='r'))
        button_draw_raw_comb = ttk.Button(frame_draw_corrected, text='Combined', 
                                    command=lambda: self.draw_compare(draw_style='c'))
        
        # add grey text to bin removal
        bin_remove_starter_line = self.bfit.fetch_files.bin_remove_starter_line
        input_line = data.omit.get()
        
        if not input_line:
            input_line = bin_remove_starter_line
            entry_omit.config(foreground=colors.entry_grey)
        
        entry_omit.delete(0, 'end')
        entry_omit.insert(0, input_line)
        entry_fn = partial(on_entry_click, \
                text=bin_remove_starter_line, entry=entry_omit)
        on_focusout_fn = partial(on_focusout, \
                text=bin_remove_starter_line, entry=entry_omit)
        entry_omit.bind('<FocusIn>', entry_fn)
        entry_omit.bind('<FocusOut>', on_focusout_fn)
        
        # grid
        r = 0
        label_omit.grid(column=0, row=r, sticky='w')
        entry_omit.grid(column=1, row=r, sticky='w')
        button_omit.grid(column=3, row=r, sticky='e', padx=10); r+=1
        checkbutton_omit_scan.grid(column=0, row=r, sticky='w', columnspan=2); r+=1
        self.label_flatten_base.grid(column=0, row=r, sticky='w', columnspan=2)
        spin_flatten_base.grid(column=2, row=r, sticky='w')
        
        button_draw_raw_flat.grid(column=0, row=0, sticky='')
        button_draw_raw_comb.grid(column=1, row=0, sticky='')
        frame_draw_corrected.grid(column=3, row=r-1, sticky='ens', pady=5, padx=5, 
                                  rowspan=2)
    
    
        # change run details --------------------------------------------------
        frame_modify = ttk.Labelframe(topframe, text='Modify Details', pad=5)
        
        self.var_type = StringVar()
        self.var_type.set('')
        self.combo_var_type = ttk.Combobox(frame_modify, \
                textvariable=self.var_type, state='readonly', width=25)
        self.combo_var_type['values'] = ('', 'ppg', 'camp', 'epics')
        self.combo_var_type.bind('<<ComboboxSelected>>', self.populate_var_selection)
        
        self.var = StringVar()
        self.var.set('')
        self.combo_var = ttk.Combobox(frame_modify, \
                textvariable=self.var, state='readonly', width=25)
        self.combo_var['values'] = ()
        self.combo_var.bind('<<ComboboxSelected>>', self.populate_prop_selection)
        
        self.prop = StringVar()
        self.prop.set('')
        self.combo_prop = ttk.Combobox(frame_modify, \
                textvariable=self.prop, state='readonly', width=25)
        self.combo_prop['values'] = ('mean', 'std', 'title', 'description', 
                                     'units', 'low', 'high', 'skew', 
                                     'id_number',)
        self.combo_prop.bind('<<ComboboxSelected>>', self.populate_value_entry)
        
        self.value = StringVar()
        self.value.set('')
        self.entry_value = Entry(frame_modify, textvariable=self.value, width=27)
        self.entry_value.bind('<KeyRelease>', self.set_value)
        
        # labels
        label_val_type = ttk.Label(frame_modify, text='System', justify=RIGHT)
        label_val = ttk.Label(frame_modify, text='Variable', justify=RIGHT)
        label_prop = ttk.Label(frame_modify, text='Property', justify=RIGHT)
        label_value = ttk.Label(frame_modify, text='Value', justify=RIGHT)
        
        # reset button
        button_reset = ttk.Button(frame_modify, text='Reset All', 
                                    command=self.reset_all_modified, pad=1)
        
        # grid
        r = 0
        label_val_type.grid(column=0, row=r, padx=5, pady=5, sticky='e'); r+=1
        label_val.grid(column=0, row=r, padx=5, pady=5, sticky='e'); r+=1
        label_prop.grid(column=0, row=r, padx=5, pady=5, sticky='e'); r+=1
        label_value.grid(column=0, row=r, padx=5, pady=5, sticky='e'); r+=1
        
        r = 0
        self.combo_var_type.grid(column=1, row=r, padx=5, sticky='e'); r+=1
        self.combo_var.grid(column=1, row=r, padx=5, sticky='e'); r+=1
        self.combo_prop.grid(column=1, row=r, padx=5, sticky='e'); r+=1
        self.entry_value.grid(column=1, row=r, padx=5, sticky='e'); r+=1
        
        button_reset.grid(column=0, row=r, padx=5, sticky='we', columnspan=2); r+=1
    
        # grid frames ---------------------------------------------------------
        topframe.grid(column=0, row=0)
        frame_details.grid(column=0, row=0, sticky='nws', padx=5, pady=5, rowspan=3)
        frame_modify.grid(column=0, row=3, sticky='nwse', padx=5, pady=5)
        
        r = 0
        frame_mode.grid(column=1, row=r, sticky='new', padx=5, pady=5); r+=1
        frame_state.grid(column=1, row=r, sticky='new', padx=5, pady=5); r+=1
        frame_rebin.grid(column=1, row=r, sticky='new', padx=5, pady=5); r+=1
        
        frame_mode.grid_columnconfigure(2, weight=1)
        frame_modify.grid_columnconfigure(1, weight=1)
        
        if '1' in self.data.mode:
            frame_scan.grid(column=1, row=r, sticky='ne', padx=5, pady=5); r+=1
        
        self.set_bin_repair()
        
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def config_checkbutton_state(self):
        """
            Change text in state checkbox
        """
        
        if self.data.check_state.get():
            self.checkbutton_state.config(text='Active')
        else:
            self.checkbutton_state.config(text='Disabled')
        
    # ====================================================================== #
    def draw_compare(self, draw_style='c'):
        """
            Draw effect of baseline flattening on combined asym
        """
        bfit = self.bfit
        
     
        plt.figure()
        a_orig = self.data.asym(draw_style, scan_repair_options='')
        a_corr = self.data.asym(draw_style)
        
        # raw
        if draw_style == 'r':
            x = np.arange(len(a_orig.p[0]))
            
            p = a_orig.p[0]
            dp = a_orig.p[1]
            p[p==0] = np.nan
            dp[dp==0] = np.nan
            
            n = a_orig.n[0]
            dn = a_orig.n[1]
            n[n==0] = np.nan
            dn[dn==0] = np.nan
            
            plt.errorbar(x, p, dp, fmt='.k', label='Uncorrected ($+$)')
            plt.errorbar(x, n, dn, fmt='.', color='grey', 
                         ecolor='grey', label='Uncorrected ($-$)')
        
            x = np.arange(len(a_corr.p[0]))
            
            p = a_corr.p[0]
            dp = a_corr.p[1]
            p[p==0] = np.nan
            dp[dp==0] = np.nan
            
            n = a_corr.n[0]
            dn = a_corr.n[1]
            n[n==0] = np.nan
            dn[dn==0] = np.nan
            
            plt.errorbar(x, p, dp, fmt='xr', label='Corrected ($+$)')
            plt.errorbar(x, n, dn, fmt='x', color='orange', 
                         ecolor='orange', label='Corrected ($-$)')
            
            plt.xlabel('Bin')
        
        # combined
        elif draw_style == 'c':
            unit = self.bfit.units[self.data.mode]
            x, a, da = a_orig
            
            plt.errorbar(x*unit[0], a, da, fmt='.k', label='Uncorrected')
            
            n = self.data.base_bins.get()
            x, a, da = a_corr
            plt.errorbar(x*unit[0], a, da, fmt='xr', label='Corrected')
            if n > 0:
                plt.errorbar(np.concatenate((x[:n], x[-n:]))*unit[0], 
                             np.concatenate((a[:n], a[-n:])), 
                             np.concatenate((da[:n], da[-n:])), 
                             fmt='ob', fillstyle='none', label='Baseline')
            
            plt.xlabel(self.bfit.xlabel_dict[self.data.mode] % unit[1])
            
        plt.ylabel('Asymmetry')
        plt.legend(fontsize='x-small')
        plt.tight_layout()
    
    # ====================================================================== #
    def draw_raw(self):
        """
            Draw raw scans in an inspect window
        """
        
        bfit = self.bfit
        
        # save draw style
        style = bfit.draw_style.get()
        
        # draw new
        bfit.draw_style.set('new')
        self.data.draw('r', figstyle='inspect', asym_args={'scan_repair_options':''})
        
        # reset draw style
        bfit.draw_style.set(style)
        
    # ====================================================================== #
    def inspect(self):
        """
            Load data in inspect window
        """
        ins = self.bfit.fileviewer
        
        ins.runn.set(self.data.run)
        ins.year.set(self.data.year)
        ins.get_data()
        self.bfit.notebook.select(0)
        
    # ====================================================================== #
    def populate_prop_selection(self, *_):
        """
            Set combo_prop based on selection combo_var
        """
        self.populate_value_entry()
    
    # ====================================================================== #
    def populate_value_entry(self, *_):
        """
            Set entry_value based on selection combo_prop
        """
        
        # get dictionary
        hist = getattr(self.data, self.var_type.get())
        
        # set default
        self.value.set('')
        
        # check if variable exists
        if self.var.get() in hist.keys():
            var = hist[self.var.get()]
            
            # set property based on varaible info
            prop = self.prop.get()
            if prop:
                self.value.set(str(getattr(var, prop)))
        
    # ====================================================================== #
    def populate_var_selection(self, *_):
        """
            Set combo_var based on selection combo_var_type
        """
        
        if self.var_type.get() == 'ppg':
            val = bd.bdata.dkeys_ppg.values()
            
        elif self.var_type.get() == 'camp':
            val = bd.bdata.dkeys_camp.values()

        elif self.var_type.get() == 'epics':
            val = bd.bdata.dkeys_epics.values()
        
        else:
            val = []
            
        val = pd.Series(val).unique()
        self.combo_var['values'] = sorted(val)
        self.var.set('')
        
    # ====================================================================== #
    def reset_all_modified(self):
        """
            Reset all modified values back to read values
        """
        
        # clear the manually updated values
        self.data.manually_updated_var = {'epics':{}, 'camp':{}, 'ppg':{}}
        
        # read data again
        self.data.read()
        
        # update fetch tab
        line = self.bfit.fetch_files.data_lines[self.data.id]
        line.set_check_text()
        line.update_label()
        
        # reset value
        self.populate_value_entry()
        
    # ====================================================================== #
    def reset_label(self):
        """
            Reset the label back to default
        """
        
        # get default label
        try:
            label = self.bfit.get_label(self.data)
        except KeyError:
            return
            
        # clear old text
        self.entry_label.delete(0, 'end')
        
        # set
        self.entry_label.insert(0, label)
        
        # reset color in fetch tab
        line = self.bfit.fetch_files.data_lines[self.data.id]
        entry = line.label_entry
        entry.config(foreground=colors.entry_grey)
        
    # ====================================================================== #
    def set_bin_repair(self, *event):
        """
            Make and set bin repair string
        """
        
        # get n bins in baseline
        try:
            n_base = self.data.base_bins.get()
        except:
            return
            
        # set colors
        if n_base > 0:
            self.label_flatten_base.config(foreground=colors.selected)
        else:
            self.label_flatten_base.config(foreground=colors.foreground)
        
    # ====================================================================== #
    def set_value(self, *_):
        """
            Set value of parameter
        """
        
        # get strings
        var_type = self.var_type.get()
        var = self.var.get()
        prop = self.prop.get()
        value = self.value.get()
        
        # get list we're modifying
        var_list = getattr(self.data, var_type)
        
        # cast the input 
        if prop in ('high', 'id_number', 'low', 'mean', 'std', 'skew'):
            
            if not value:
                value = np.nan
            else:
                try:
                    value = float(value)
                except ValueError:
                    return
                
        # set the input
        var_list.set(var, **{prop:value})
        
        # update variables
        self.data.set_new_var()
        
        # add property to perminantly updated list
        self.data.manually_updated_var[var_type][var] = getattr(self.data, var_type)[var]
        
        # update fetch tab
        line = self.bfit.fetch_files.data_lines[self.data.id]
        line.set_check_text()
        line.update_label()
        
    # ====================================================================== #
    def ungray_label(self, _):
        """
            Remove the gray in the fetch tab label entry
        """
        line = self.bfit.fetch_files.data_lines[self.data.id]
        entry = line.label_entry
        entry.config(foreground=colors.entry_white)
