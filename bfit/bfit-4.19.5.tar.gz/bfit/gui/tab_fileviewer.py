# File viewer tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk
from multiprocessing import Process, Pipe
from bdata.calc import nqr_B0_hh6, nqr_B0_hh3
from bfit.backend.fitdata import fitdata
from bdata import bdata, bmerged
from bfit import logger_name
import bdata as bd

import numpy as np
import matplotlib.pyplot as plt
import sys, os, time, glob, datetime
import logging


__doc__ = """
    View file contents tab.
    
    To-do:
        cumulative count viewing
    """

# =========================================================================== #
class fileviewer(object):
    """
        Data fields:
            asym_type: StringVar, drawing style
            bfit: bfit object
            button_run_from_file: ttk.Button for load from run
            data: bdata object for drawing
            entry_asym_type: combobox for asym calculations
            entry_rebin: Spinbox
            entry_runn: Spinbox
            entry_year: Spinbox
            filename: string, path to file to load, disabled if == ''
            is_updating: BooleanVar, True if update draw
            rebin: IntVar() rebin value
            runn: IntVar() run number
            text: Text widget for displaying run information
            update_id: string, run id for the currently updating run
            year: IntVar() year of exp 
    """
    
    default_export_filename = "%d_%d.csv" # year_run.csv
    update_id = ''
    mode_dict = {"1c":"Camp Scan", 
                 "1d":"Laser Scan", 
                 "1e":"Field Scan", 
                 "1w":"Frequency Comb", 
                 "1f":"Frequency Scan", 
                 "1x":"Frequency Scan", 
                 "1n":"Rb Cell Scan", 
                 "20":"SLR", 
                 '2e':'Randomized Frequency Scan',
                 '2h':'SLR with Alpha Tracking', 
                 '2s':'Spin Echo', 
                }
    
    mode_epics_var = {'1n':'ILE2:BIAS15:VOL',
                      '1d':'ILE2:RING:FREQ:VOL',
                      '1e':'ILE2A1:HH:CUR',
                     }
    
    # ======================================================================= #
    def __init__(self, file_tab, bfit):
        """ Position tab tkinter elements"""
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')
        
        # year and filenumber entry ------------------------------------------
        entry_frame = ttk.Frame(file_tab, borderwidth=1)
        self.year = IntVar()
        self.runn = IntVar()
        self.rebin = IntVar()
        self.filename = ''
        self.bfit = bfit
        
        self.year.set(self.bfit.get_latest_year())
        self.rebin.set(1)
        
        self.entry_year = Spinbox(entry_frame, \
                from_=2000, to=np.inf, 
                textvariable=self.year, width=5)
        self.entry_runn = Spinbox(entry_frame, \
                from_=0, to=np.inf, 
                textvariable=self.runn, width=7)
        self.runn.set(40000)
        
        # fetch button
        fetch = ttk.Button(entry_frame, text='Fetch', command=self.get_data)
            
        # draw button
        draw = ttk.Button(entry_frame, text='Draw', 
                          command=lambda:self.draw(figstyle='inspect'))
        
        # get run from file
        self.button_run_from_file = ttk.Button(file_tab, text='Load run from file', 
                                                command=self.load_file)
        
        # grid and labels
        entry_frame.grid(column=0, row=0, sticky=N, columnspan=2)
        ttk.Label(entry_frame, text="Year:").grid(column=0, row=0, sticky=E)
        self.entry_year.grid(column=1, row=0, sticky=E)
        ttk.Label(entry_frame, text="Run Number:").grid(column=2, row=0, sticky=E)
        self.entry_runn.grid(column=3, row=0, sticky=E)
        fetch.grid(column=4, row=0, sticky=E)
        draw.grid(column=5, row=0, sticky=E)
        self.button_run_from_file.grid(column=1, row=0, sticky=E, padx=5)
        
        # padding 
        for child in entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        # viewer frame -------------------------------------------------------
        view_frame = ttk.Frame(file_tab, borderwidth=2)
        
        self.text_nw = Text(view_frame, width=88, height=20, state='normal', wrap='none')
        self.text_ne = Text(view_frame, width=88, height=20, state='normal', wrap='none')
        self.text_sw = Text(view_frame, width=88, height=20, state='normal', wrap='none')
        self.text_se = Text(view_frame, width=88, height=20, state='normal', wrap='none')
        
        ttk.Label(view_frame, text="Run Info").grid(column=0, row=0, sticky=N, pady=5)
        ttk.Label(view_frame, text="PPG Parameters").grid(column=1, row=0, sticky=N, pady=5)
        ttk.Label(view_frame, text="Camp and Stats").grid(column=0, row=2, sticky=N, pady=5)
        ttk.Label(view_frame, text="EPICS").grid(column=1, row=2, sticky=N, pady=5)
        
        self.text_nw.grid(column=0, row=1, sticky=(N, W, E, S), padx=5)
        self.text_ne.grid(column=1, row=1, sticky=(N, W, E, S), padx=5)
        self.text_sw.grid(column=0, row=3, sticky=(N, W, E, S), padx=5)
        self.text_se.grid(column=1, row=3, sticky=(N, W, E, S), padx=5)
        
        view_frame.grid(column=0, row=1, sticky=(N, E, W), columnspan=2)
        
        # details frame: stuff at the bottom ----------------------------------
        details_frame = ttk.Frame(file_tab)
        self.entry_rebin = Spinbox(details_frame, from_=1, to=100, width=3, \
                textvariable=self.rebin)
        
        # update check box
        self.is_updating = BooleanVar()
        self.is_updating.set(False)
        update_box = ttk.Checkbutton(details_frame, text='Periodic Redraw', 
                command=self.do_update, variable=self.is_updating, onvalue=True, 
                offvalue=False)

        # asymmetry type combobox
        self.asym_type = StringVar()
        self.asym_type.set('')
        self.entry_asym_type = ttk.Combobox(details_frame, \
                textvariable=self.asym_type, state='readonly', width=25)
        self.entry_asym_type['values'] = ()
                
        # gridding
        ttk.Label(details_frame, text="Rebin:").grid(column=0, row=0, sticky=E)
        self.entry_rebin.grid(column=1, row=0, sticky=E)
        self.entry_asym_type.grid(column=2, row=0, sticky=E)
        update_box.grid(column=3, row=0, sticky=E)
        details_frame.grid(column=0, row=2, sticky=S, columnspan=2)
        
        # padding 
        for child in details_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
            
        # resizing
        file_tab.grid_rowconfigure(1, weight=1)
        file_tab.grid_columnconfigure(0, weight=1)
        
        entry_frame.grid_columnconfigure(0, weight=2)
        entry_frame.grid_columnconfigure(2, weight=1)
        entry_frame.grid_rowconfigure(0, weight=1)
        
        for i in range(2):
            view_frame.grid_columnconfigure(i, weight=1)
        view_frame.grid_rowconfigure(1, weight=1)
        view_frame.grid_rowconfigure(3, weight=1)
        
        for t in [self.text_nw, self.text_ne, self.text_sw, self.text_se]:
            for i in range(5):
                t.grid_columnconfigure(i, weight=1)
                t.grid_rowconfigure(i, weight=1)
            
        self.logger.debug('Initialization success.')
            
    # ======================================================================= #
    def __del__(self):
        pass
        
    # ======================================================================= #
    def _get_data(self, bdata_obj, quiet=False):
        """
            Display data and send bdata object to bfit draw list. 
            Return True on success, false on Failure
        """
        
        # get data
        try: 
            data = fitdata(self.bfit, bdata_obj)
        except ValueError as err:
            self.logger.exception('File read failed.')
            self.logger.debug(err)
            raise err from None
            for t in [self.text_nw, self.text_sw, self.text_se, self.text_ne]:
                self.set_textbox_text(t, 'File read failed.')
            return False
        except RuntimeError as err:
            self.logger.exception('File does not exist.')
            self.logger.debug(err)
            for t in [self.text_nw, self.text_sw, self.text_se, self.text_ne]:
                self.set_textbox_text(t, 'File does not exist.')
            return False
        
        # set data field
        self.data = data
        
        # set draw parameters
        self.bfit.set_asym_calc_mode_box(data.mode, self, data.area)
        
        # set nbm variable
        self.set_nbm()
        
        # set rebin
        self.set_rebin(self.data)
        
        # quiet mode: don't update text
        if quiet: return True
        
        # NW -----------------------------------------------------------------
        
        # get data: headers
        mode = self.mode_dict[data.mode]
        try:
            if data.ppg.rf_enable.mean and data.mode == '20' and \
                                                        data.ppg.rf_on.mean > 0:
                mode = "Hole Burning"
        except AttributeError:
            pass
        
        mins, sec = divmod(data.duration, 60)
        duration = "%dm %ds" % (mins, sec)
        
        # set dictionary
        data_nw =  {"Run":'%d (%d)' % (data.run, data.year), 
                    "Area": data.area, 
                    "Run Mode": "%s (%s)" % (mode, data.mode), 
                    "Title": data.title, 
                    "Experimenters": data.experimenter, 
                    "Sample": data.sample, 
                    "Orientation":data.orientation, 
                    "Experiment":str(data.exp), 
                    "Run Duration": duration, 
                    "Start": data.start_date, 
                    "End": data.end_date, 
                    "":"", 
                    }
        
        # set key order 
        key_order_nw = ['Run', 'Run Mode', 'Title', '', 
                        'Start', 'End', 'Run Duration', '', 
                        'Sample', 'Orientation', '', 
                        'Experiment', 'Area', 'Experimenters','',
                        ]
        
        # get probe species
        try:
            probe = data.ppg.probe_species.units
            data_nw["Probe"] = str(probe)
            key_order_nw.append('Probe')
            key_order_nw.append('')
        except AttributeError:
            pass
        
        # comments
        if hasattr(data, 'comments'):
            data_nw["Comment"] = data.comments['Comments during run'].body
            key_order_nw.append('Comment')
        
        # SW -----------------------------------------------------------------
        data_sw = {'':''}
        key_order_sw = []
                        
        # get data: temperature and fields
        try:
            temp = data.temperature.mean
            temp_stdv = data.temperature.std
            data_sw["Temperature"] = "%.2f +/- %.2f K" % (temp, temp_stdv)
            key_order_sw.append('Temperature')
        except AttributeError:
            pass
        
        try:
            curr = data.camp.smpl_current
            data_sw["Heater Current"] = "%.2f +/- %.2f A" % (curr.mean, curr.std)
            key_order_sw.append('Heater Current')
        except AttributeError:
            pass
        
        try:
            temp = data.camp.oven_readC.mean
            temp_stdv = data.camp.oven_readC.std
            data_sw['Oven Temperature'] = "%.2f +/- %.2f K" % (temp, temp_stdv)
            key_order_sw.append('Oven Temperature')
        except AttributeError:
            pass
        
        try:
            curr = data.camp.oven_current
            data_sw['Oven Current'] = "%.2f +/- %.2f A" % (curr.mean, curr.std)
            key_order_sw.append('Oven Current')
        except AttributeError:
            pass
        
        try: 
            field = np.around(data.camp.b_field.mean, 3)
            field_stdv = np.around(data.camp.b_field.std, 3)
            data_sw['Magnetic Field'] = "%.3f +/- %.3f T" % (field, field_stdv)
            key_order_sw.append('Magnetic Field')
        except AttributeError:
            pass
            
        try: 
            val, _ = nqr_B0_hh3(amps=data.epics.hh_current.mean)
            data_sw['Magnetic Field'] = "%.3f Gauss" % val
            key_order_sw.append('Magnetic Field')
        except AttributeError:
            pass
            
        if key_order_sw[-1] != '':
            key_order_sw.append('')
                
        # cryo options
        try: 
            mass = data.camp.mass_read
            data_sw['Mass Flow'] = "%.3f +/- %.3f" % (mass.mean, mass.std)
            key_order_sw.append('Mass Flow')
        except AttributeError:
            pass
    
        try: 
            mass = data.camp.he_read
            data_sw['Mass Flow'] = "%.3f +/- %.3f" % (mass.mean, mass.std)
            key_order_sw.append('Mass Flow')
        except AttributeError:
            pass
    
        try: 
            cryo = data.camp.cryo_read
            data_sw['CryoEx Mass Flow'] = "%.3f +/- %.3f" % (cryo.mean, cryo.std)
            key_order_sw.append('CryoEx Mass Flow')
        except AttributeError:
            pass    
            
        try: 
            data_sw['Needle Setpoint'] = "%.3f turns" % data.camp.needle_set.mean
            key_order_sw.append('Needle Setpoint')
        except AttributeError:
            pass    
            
        try: 
            data_sw['Needle Readback'] = "%.3f turns" % data.camp.needle_pos.mean
            key_order_sw.append('Needle Readback')
        except AttributeError:
            pass    
            
        try:
            lift_set = np.around(data.camp.clift_set.mean, 3)
            data_sw['Cryo Lift Setpoint'] = "%.3f mm" % lift_set
            key_order_sw.append('Cryo Lift Setpoint')
        except AttributeError:
            pass
        
        try:
            lift_read = np.around(data.camp.clift_read.mean, 3)
            data_sw['Cryo Lift Readback'] = "%.3f mm" % lift_read
            key_order_sw.append('Cryo Lift Readback')
        except AttributeError:
            pass
    
        # rf dac
        if mode != 'SLR':
            if key_order_sw[-1] != '':
                key_order_sw.append('')
            
            try: 
                data_sw['rf_dac'] = "%d" % int(data.camp.rf_dac.mean)
                key_order_sw.append('rf_dac')
            except AttributeError:
                pass
            
            try: 
                data_sw['RF Amplifier Gain'] = "%.2f" % data.camp.rfamp_rfgain.mean
                key_order_sw.append('RF Amplifier Gain')
            except AttributeError:
                pass    
        
        if key_order_sw[-1] != '':
            key_order_sw.append('')
        
        # rates and counts
        hist = ('F+', 'F-', 'B-', 'B+') if data.area.upper() == 'BNMR' \
                                     else ('L+', 'L-', 'R-', 'R+')

        try:     
            val = int(np.sum([data.hist[h].data for h in hist]))
            val, unit_val = num_prefix(val)
            data_sw['Total Counts Sample'] = "%.3g%s" % (val, unit_val)
            key_order_sw.append('Total Counts Sample')
        except (AttributeError, KeyError):
            pass
        
        try: 
            val = int(np.sum([data.hist[h].data for h in hist])/data.duration)
            val, unit_val = num_prefix(val)
            data_sw['Total Rate Sample'] =  "%.3g%s (cps)" % (val, unit_val)
            key_order_sw.append('Total Rate Sample')
        except (AttributeError, KeyError):
            pass
        
        try: 
            tag_F = 'F' if data.area == 'BNMR' else 'L'
            tag_B = 'B' if data.area == 'BNMR' else 'R'
    
            F = np.sum([data.hist[h].data for h in hist if tag_F in h])/data.duration
            B = np.sum([data.hist[h].data for h in hist if tag_B in h])/data.duration
            
            F, unit_F = num_prefix(F)
            B, unit_B = num_prefix(B)
            
            try:
                ratio = F/B
            except ZeroDivisionError:
                ratio = np.nan
            
            data_sw['Rate %s/%s' % (tag_F, tag_B)] = \
                    '%.3g%s / %.3g%s (cps) [ratio: %.2f]' % (F, unit_F, B, unit_B, ratio)
            key_order_sw.append('Rate %s/%s' % (tag_F, tag_B))
        except (AttributeError, KeyError):
            pass
        
        if key_order_sw[-1] != '':
            key_order_sw.append('')
        
        hist = ('F+', 'F-', 'B-', 'B+')    
        try: 
            val = int(np.sum([data.hist['NBM'+h].data for h in hist]))
            val, unit_val = num_prefix(val)
            data_sw['Total Counts NBM'] = "%.3g%s" % (val, unit_val)
            key_order_sw.append('Total Counts NBM')
        except (AttributeError, KeyError):
            pass
        
        try: 
            val = int(np.sum([data.hist['NBM'+h].data for h in hist])/data.duration)
            val, unit_val = num_prefix(val)
            data_sw['Total Rate NBM'] = "%.3g%s (cps)" % (val, unit_val)
            key_order_sw.append('Total Rate NBM')
        except (AttributeError, KeyError):
            pass
            
        # SE -----------------------------------------------------------------
        data_se = {'':''}
        key_order_se = []
            
        # get data: biases 
        try:
            if 'nqr_bias' in data.epics.keys():
                bias =      data.epics.nqr_bias.mean/1000.
                bias_std =  data.epics.nqr_bias.std/1000.
            elif 'nmr_bias' in data.epics.keys():
                bias =      data.epics.nmr_bias.mean
                bias_std =  data.epics.nmr_bias.std
            
            data_se["Platform Bias"] = "%.3f +/- %.3f kV" % \
                    (np.around(bias, 3), np.around(bias_std, 3))
            key_order_se.append("Platform Bias")
            
        except UnboundLocalError:
            pass
        
        try:
            data_se["BIAS15"] = "%.3f +/- %.3f V" % \
                    (np.around(data.epics.bias15.mean, 3), 
                     np.around(data.epics.bias15.std, 3))
            key_order_se.append('BIAS15')
        except AttributeError:
            pass
        
        # get data: beam energy
        try: 
            init_bias = data.epics.target_bias.mean
            init_bias_std = data.epics.target_bias.std
        except AttributeError:
            try:
                init_bias = data.epics.target_bias.mean
                init_bias_std = data.epics.target_bias.std
            except AttributeError:
                pass
            
        try:
            val = np.around(init_bias/1000., 3)
            std = np.around(init_bias_std/1000., 3)
            data_se["Initial Beam Energy"] = "%.3f +/- %.3f keV" % (val, std)
            key_order_se.append('Initial Beam Energy')
        except UnboundLocalError:
            pass
        
        # Get final beam energy
        try: 
            val = np.around(data.beam_kev, 3)
            std = np.around(data.beam_kev_err, 3)
            data_se['Implantation Energy'] = "%.3f +/- %.3f keV" % (val, std)
            key_order_se.append('Implantation Energy')
        except AttributeError:
            pass
        
        if key_order_se[-1] != '':
            key_order_se.append('')
        
        # doppler tubes
        try:
            data_se["Doppler Tube CH0"] = "%.3f +/- %.3f V" % \
                    (np.around(data.epics.dopplertube_ch0.mean, 3), 
                     np.around(data.epics.dopplertube_ch0.std, 3))
            key_order_se.append('Doppler Tube CH0')
        except AttributeError:
            pass
        
        try:
            data_se["Doppler Tube CH1"] = "%.3f +/- %.3f V" % \
                    (np.around(data.epics.dopplertube_ch1.mean, 3), 
                     np.around(data.epics.dopplertube_ch1.std, 3))
            key_order_se.append('Doppler Tube CH1')
        except AttributeError:
            pass
        
        try:
            data_se["Doppler Tube CH2"] = "%.3f +/- %.3f V" % \
                    (np.around(data.epics.dopplertube_ch2.mean, 3), 
                     np.around(data.epics.dopplertube_ch2.std, 3))
            key_order_se.append('Doppler Tube CH2')
        except AttributeError:
            pass
        
        if key_order_se[-1] != '':
            key_order_se.append('')
        
        # laser stuff
        try: 
            val = data.epics.las_pwr
            data_se['Laser Power'] = "%.3f +/- %.3f V" % (val.mean, val.std)
            key_order_se.append('Laser Power')
        except AttributeError:
            pass
        
        try: 
            val = data.epics.las_lambda
            data_se['Laser Wavelength'] = "%.3f +/- %.3f nm" % (val.mean, val.std)
            key_order_se.append('Laser Wavelength')
        except AttributeError:
            pass
        
        try: 
            val = data.epics.las_wavenum
            data_se['Laser Wavenumber'] = "%.5f +/- %.5f 1/cm" % (val.mean, val.std)
            key_order_se.append('Laser Wavenumber')
        except AttributeError:
            pass
        
        # magnet stuff
        try: 
            val = data.epics.hh_current.mean
            std = data.epics.hh_current.std
            field, _ = nqr_B0_hh3(amps=val)
            data_se['HH3 Magnet Current'] = "%.3f +/- %.3f A (%.2f G)" % (val, std, field)
            key_order_se.append('HH3 Magnet Current')            
        except AttributeError:
            pass
        
        try: 
            val = data.epics.hh6_current.mean
            std = data.epics.hh6_current.std
            field, _ = nqr_B0_hh6(amps=val)
            data_se['HH6 Magnet Current'] = "%.3f +/- %.3f A (%.2f G)" % \
                                                    (val, std, field)
            key_order_se.append('HH6 Magnet Current')            
        except AttributeError:
            pass
        
        if key_order_se[-1] != '':
            key_order_se.append('')
        
        # EL3
        try: 
            val = data.epics.el3.mean
            std = data.epics.el3.std
            data_se['Einzel Lens 3'] = "%.3f +/- %.3f V" % (val, std)
            key_order_se.append('Einzel Lens 3')
        except AttributeError:
            pass
        
        # NE -----------------------------------------------------------------
        data_ne = {'':''}
        key_order_ne = []
        
        # get data: SLR data
        if data.mode in ['20', '2h']:
            
            # PPG timing 
            try:
                dwell = int(data.ppg.dwelltime.mean)
                data_ne['Dwell time'] = "%d ms" % dwell
                key_order_ne.append('Dwell time')
            except AttributeError:
                pass
            
            try:    
                beam = int(data.ppg.prebeam.mean)            
                data_ne['Number of prebeam dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of prebeam dwelltimes')
            except AttributeError:
                pass
            
            try:    
                beam = int(data.ppg.beam_on.mean)            
                data_ne['Number of beam-on dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of beam-on dwelltimes')
            except AttributeError:
                pass
            
            try: 
                beam = int(data.ppg.beam_off.mean)
                data_ne['Number of beam-off dwelltimes'] = "%d dwelltimes" % beam
                key_order_ne.append('Number of beam-off dwelltimes')
            except AttributeError:
                pass
            
            try:    
                rf = int(data.ppg.rf_on_delay.mean)
                data_ne['RF on delay'] = "%d dwelltimes" % rf
                key_order_ne.append('RF on delay')
            except AttributeError:
                pass
            
            try:    
                rf = int(data.ppg.rf_on.mean)
                data_ne['RF on duration'] = "%d dwelltimes" % rf
                key_order_ne.append('RF on delay')
            except AttributeError:
                pass
            
            key_order_ne.append('')
            
            # Miscellaneous
            try:    
                hel = bool(data.ppg.hel_enable.mean)
                data_ne['Flip helicity'] = str(hel)
                key_order_ne.append('Flip helicity')
            except AttributeError:
                pass
            
            try:    
                hel = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity sleep'] = "%d ms" % hel
                key_order_ne.append('Helicity sleep')
            except AttributeError:
                pass
        
            key_order_ne.append('')
            
            try:
                rf = bool(data.ppg.rf_enable.mean)
                data_ne['RF enable'] = str(rf)
                key_order_ne.append('RF enable')
                
                if rf:
                    freq = int(data.ppg.freq.mean)    
                    data_ne['Frequency'] = "%d Hz" % freq
                    key_order_ne.append('Frequency')
            except AttributeError:
                pass
            
        # get 1F specific data
        elif data.mode in ('1f', '1x'):
            
            # ppg timing box
            try:
                val = int(data.ppg.dwelltime.mean)
                data_ne['Bin Width'] = "%d ms" % val
                key_order_ne.append('Bin Width')
            except AttributeError:
                pass
            
            try:    
                val = int(data.ppg.nbins.mean)
                data_ne['Number of Bins'] = "%d" % val
                key_order_ne.append('Number of Bins')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.service_t.mean)
                data_ne['DAQ service time'] = "%d ms" % val
                key_order_ne.append('DAQ service time')
            except AttributeError:
                pass    
            
            key_order_ne.append('')
            
            # titles for frequencies
            if data.mode == '1x':
                nregions = len([k for k in data.ppg.keys() if 'fine_freq_start' in k])
                
                titles = ['Main scan']
                for i in range(nregions):
                    titles.append('Fine region %d' % (i+1))
                titles = [titles[i].ljust(14) for i in range(len(titles))]
                
                data_ne['Scan region'] = ''.join(titles)
                key_order_ne.append('Scan region')
            
            # PSM RF - Frequency
            try:
                start = int(data.ppg.freq_start.mean)
                data_ne['Start frequency'] = '%d Hz' % start
                key_order_ne.append('Start frequency')
            except AttributeError:
                pass
            
            try:
                stop = int(data.ppg.freq_stop.mean)
                data_ne['End frequency'] = '%d Hz' % stop
                key_order_ne.append('End frequency')
            except AttributeError:
                pass
            
            try:
                incr = int(data.ppg.freq_incr.mean)
                data_ne['Frequency scan gap'] = '%d Hz' % incr
                key_order_ne.append('Frequency scan gap')
            except AttributeError:
                pass
            
            try:
                nsteps = int((stop-start)/incr)
                data_ne['Num frequency steps'] = '%d (%d freqs in total)' % (nsteps, nsteps+1)
                key_order_ne.append('Num frequency steps')
            except NameError:
                pass
            
            try:
                center = (stop+start)/2
                data_ne['Center frequency'] = '%d Hz' % center
                key_order_ne.append('Center frequency')
            except NameError:
                pass
            
            try:
                width = stop-start
                data_ne['Full scan width'] = '%d Hz' % width
                key_order_ne.append('Full scan width')
            except NameError:
                pass
                
            try:
                val = bool(data.ppg.rand_freq_val.mean)
                data_ne['Randomize frequency order'] = str(val)
                key_order_ne.append('Randomize frequency order')
            except AttributeError:
                pass
                
            key_order_ne.append('')
            
            # Miscellaneous
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip helicity'] = str(val)
                key_order_ne.append('Flip helicity')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity sleep'] = "%d ms" % val
                key_order_ne.append('Helicity sleep')
            except AttributeError:
                pass
            
            try:
                val = bool(data.ppg.const_t_btwn_cycl.mean)
                data_ne['Ensure constant time between cycles'] = str(val)
                key_order_ne.append('Ensure constant time between cycles')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.ncycles.mean)
                data_ne['Repeat N cycles per supercycle'] = '%d' % val
                key_order_ne.append('Repeat N cycles per supercycle')
            except AttributeError:
                pass
                
            i = 1
            while True: 
                
                string_len = 14 * i
                
                try:
                    
                    start = int(data.ppg['fine_freq_start_%d' % i].mean)
                    string = data_ne['Start frequency'].ljust(string_len)
                    data_ne['Start frequency'] = string + '%d Hz' % start
                    
                    stop = int(data.ppg['fine_freq_end_%d' % i].mean)
                    string = data_ne['End frequency'].ljust(string_len)
                    data_ne['End frequency'] = string + '%d Hz' % stop
                    
                    gap = int(data.ppg['fine_freq_increment_%d' % i].mean)
                    string = data_ne['Frequency scan gap'].ljust(string_len) 
                    data_ne['Frequency scan gap'] = string + '%d Hz' % gap
                    
                    center = (start+stop)/2
                    string = data_ne['Center frequency'].ljust(string_len)
                    data_ne['Center frequency'] = string + '%d Hz' % center
                    
                    width = (stop-start)
                    string = data_ne['Full scan width'].ljust(string_len)
                    data_ne['Full scan width'] = string + '%d Hz' % width
                    
                    nsteps = int((stop-start)/gap)
                    string = data_ne['Num frequency steps'].split('(')[0]
                    string = string.ljust(string_len)
                    data_ne['Num frequency steps'] = string + '%d' % nsteps
                    
                except KeyError:
                    break
                except NameError:
                    pass
                
                i += 1
                
        # get 1W specific data
        elif data.mode == '1w':
            
            # ppg timing
            try:
                val = int(data.ppg.dwelltime.mean)
                data_ne['Bin width'] = "%d ms" % val
                key_order_ne.append('Bin width')
            except AttributeError:
                pass
            
            try:    
                val = int(data.ppg.nbins.mean)
                data_ne['Number of bins'] = "%d" % val
                key_order_ne.append('Number of bins')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.service_t.mean)
                data_ne['DAQ service time'] = "%d ms" % val
                key_order_ne.append('DAQ service time')
            except AttributeError:
                pass    
            
            
            key_order_ne.append('')
            
            # psm rf freq
            try:
                val = str(data.ppg.freqfn_f1.units)
                data_ne['Parametric function for f0ch1'] = val
                key_order_ne.append('Parametric function for f0ch1')
            except AttributeError:
                pass
            
            try:
                val = str(data.ppg.freqfn_f2.units)
                data_ne['Parametric function for f0ch2'] = val
                key_order_ne.append('Parametric function for f0ch2')
            except AttributeError:
                pass
            
            try:
                val = str(data.ppg.freqfn_f3.units)
                data_ne['Parametric function for f0ch3'] = val
                key_order_ne.append('Parametric function for f0ch3')
            except AttributeError:
                pass
            
            try:
                val = str(data.ppg.freqfn_f4.units)
                data_ne['Parametric function for f0ch4'] = val
                key_order_ne.append('Parametric function for f0ch4')
            except AttributeError:
                pass
             
            try:
                val = int(data.ppg.yconst.mean)
                data_ne['Parametric Y constant'] = '%d Hz' % val
                key_order_ne.append('Parametric Y constant')
            except AttributeError:
                pass
                
            try:
                start = int(data.ppg.xstart.mean)
                data_ne['Parametric X start'] = '%d Hz' % start
                key_order_ne.append('Parametric X start')
            except AttributeError:
                pass
                
            try:
                stop = int(data.ppg.xstop.mean)
                data_ne['Parametric X end'] = '%d Hz' % stop
                key_order_ne.append('Parametric X end')
            except AttributeError:
                pass
                
            try:
                incr = int(data.ppg.xincr.mean)
                data_ne['X scan gap'] = '%d Hz' % incr
                key_order_ne.append('X scan gap')
            except AttributeError:
                pass
                
            try:
                nsteps = int((stop-start)/incr)
                data_ne['Num X steps'] = '%d (%d freqs total)' % (nsteps, nsteps+1)
                key_order_ne.append('Num X steps')
            except NameError:
                pass

            try:
                val = bool(data.ppg.rand_freq_val.mean)
                data_ne['Randomize frequency order'] = str(val)
                key_order_ne.append('Randomize frequency order')
            except AttributeError:
                pass
                
            key_order_ne.append('')
                
            # Miscellaneous
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip helicity'] = str(val)
                key_order_ne.append('Flip helicity')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity sleep'] = "%d ms" % val
                key_order_ne.append('Helicity sleep')
            except AttributeError:
                pass        
            
            try:
                val = bool(data.ppg.const_t_btwn_cycl.mean)
                data_ne['Ensure constant time between cycles'] = str(val)
                key_order_ne.append('Ensure constant time between cycles')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.ncycles.mean)
                data_ne['Repeat N cycles per supercycle'] = '%d' % val
                key_order_ne.append('Repeat N cycles per supercycle')
            except AttributeError:
                pass
            
        # get Rb Cell specific data
        elif data.mode in ['1n', '1d', '1e', '1c']:
            
            try:
                dwell = int(data.ppg.dwelltime.mean)
                data_ne['Bin Width'] = "%d ms" % dwell
                key_order_ne.append('Bin Width')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.nbins.mean)
                data_ne['Number of Bins'] = '%d' % val
                key_order_ne.append('Number of Bins')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.service_t.mean)
                data_ne['DAQ service time'] = "%d ms" % val
                key_order_ne.append('DAQ service time')
            except AttributeError:
                pass    
            
            data_ne[''] = ''
            key_order_ne.append('')
            
             # common items
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip helicity'] = str(val)
                key_order_ne.append('Flip helicity')
            except AttributeError:
                pass
            
            try:
                val = int(data.ppg.hel_sleep.mean)
                data_ne['Helicity sleep'] = "%d ms" % val
                key_order_ne.append('Helicity sleep')
            except AttributeError:
                pass
            
            # custom varible scan check
            try: 
                custom_enable = bool(data.ppg.customv_enable.mean)
            except AttributeError:
                custom_enable = False
            
            # set scan variable name, ppg key
            if data.mode == '1c':
                prefix = ''
                try:
                    val = str(data.ppg.scan_device.units)
                    data_ne['CAMP device'] = '%s' % val
                    key_order_ne.append('CAMP device')
                except AttributeError:
                    pass                
                
            else:
                if custom_enable:
                    prefix = 'customv_'
                    
                    try:
                        val = str(data.ppg.customv_name_write.units)
                        data_ne['EPICS device'] = '%s' % val
                        key_order_ne.append('EPICS device')
                    except AttributeError:
                        pass                
                else:
                    prefix = ''
                    data_ne['EPICS device'] = '%s' % self.mode_epics_var[self.data.mode]
                    key_order_ne.append('EPICS device')                
                    
            # scan ranges
            try:
                ppg = data.ppg[prefix+'scan_start']
                start = int(ppg.mean)
                unit = str(ppg.units).title()
                data_ne['Scan start'] = '%d %s' % (start, unit)
                key_order_ne.append('Scan start')
            except (AttributeError, KeyError):
                pass
            
            try:    
                ppg = data.ppg[prefix+'scan_stop']
                stop = int(ppg.mean)
                unit = str(ppg.units).title()
                data_ne['Scan stop'] = '%d %s' % (stop, unit)
                key_order_ne.append('Scan stop')
            except (AttributeError, KeyError):
                pass
            
            try:
                ppg = data.ppg[prefix+'scan_incr']
                incr = int(np.round(ppg.mean))
                unit = str(ppg.units).title()
                data_ne['Scan gap'] = '%d %s' % (incr, unit)
                key_order_ne.append('Scan gap')
            except (AttributeError, KeyError):
                pass
            
            try:
                nsteps = int((stop-start)/incr)
                data_ne['Number of scan steps'] = '%d (%d data points)' % (nsteps, nsteps+1)
                key_order_ne.append('Number of scan steps')
            except NameError:
                pass
                
            try:
                val = int(data.ppg.ncycles.mean)
                data_ne['Repeat N cycles per supercycle'] = '%d' % val
                key_order_ne.append('Repeat N cycles per supercycle')
            except AttributeError:
                pass
            
        # get 2e mode specific data
        elif data.mode in ['2e']:
            
            # ppg timing
            try:
                val = int(data.ppg.rf_on_ms.mean)
                data_ne['RF on time (aka dwelltime)'] = "%d ms" % val
                key_order_ne.append('RF on time (aka dwelltime)')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.rf_on_delay.mean)
                data_ne['RF on delay'] = "%d dwelltimes" % val
                key_order_ne.append('RF on delay')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.beam_off_ms.mean)
                data_ne['Beam off time'] = "%d ms" % val
                key_order_ne.append('Beam off time')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.ndwell_post_on.mean)
                data_ne['Post-RF beam-on'] = "%d dwelltimes" % val
                key_order_ne.append('Post-RF beam-on')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.ndwell_per_f.mean)
                data_ne['Number dwelltimes per freq'] = "%d" % val
                key_order_ne.append('Number dwelltimes per freq')
            except AttributeError:
                pass
                
            key_order_ne.append('')
            
            # PSM RF Frequency   
            try:
                start = int(data.ppg.freq_start.mean)
                data_ne['Start frequency'] = '%d Hz' % start
                key_order_ne.append('Start frequency')
            except AttributeError:
                pass
            
            try:
                stop = int(data.ppg.freq_stop.mean)
                data_ne['End frequency'] = '%d Hz' % stop
                key_order_ne.append('End frequency')
            except AttributeError:
                pass
            
            try:
                incr = int(data.ppg.freq_incr.mean)
                data_ne['Frequency scan gap'] = '%d Hz' % incr
                key_order_ne.append('Frequency scan gap')
            except AttributeError:
                pass
            
            try:
                nsteps = int((stop-start)/incr)
                data_ne['Num frequency steps'] = '%d (%d freqs in total)' % (nsteps, nsteps+1)
                key_order_ne.append('Num frequency steps')
            except NameError:
                pass
            
            try:
                center = (stop-start)/2
                data_ne['Center frequency'] = '%d Hz' % center
                key_order_ne.append('Center frequency')
            except NameError:
                pass
            
            try:
                width = stop-start
                data_ne['Full scan width'] = '%d Hz' % width
                key_order_ne.append('Full scan width')
            except NameError:
                pass
                
            try:
                val = bool(data.ppg.rand_freq_val.mean)
                data_ne['Randomize frequency order'] = str(val)
                key_order_ne.append('Randomize frequency order')
            except AttributeError:
                pass
                
            key_order_ne.append('')
            
            # misc
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Flip helicity'] = str(val)
                key_order_ne.append('Flip helicity')
            except AttributeError:
                pass
                
            try:
                val = bool(data.ppg.hel_enable.mean)
                data_ne['Helicity sleep'] = "%d ms" % val
                key_order_ne.append('Helicity sleep')
            except AttributeError:
                pass
                
            try:
                val = int(data.ppg.ncycles.mean)
                data_ne['Repeat N cycles per supercycle'] = '%d' % val
                key_order_ne.append('Repeat N cycles per supercycle')
            except AttributeError:
                pass
            
        # set viewer string
        def set_str(data_dict, key_order, txtbox):
        
            m = max(max(map(len, list(data_dict.keys()))) + 1, 5)
            lines = [k.rjust(m)+':   ' + data_dict[k] for k in key_order]
            lines = [l if l.strip() != ':' else '' for l in lines]
            
            self.set_textbox_text(txtbox, '\n'.join(lines))
        
        set_str(data_nw, key_order_nw, self.text_nw)
        set_str(data_ne, key_order_ne, self.text_ne)
        set_str(data_sw, key_order_sw, self.text_sw)
        set_str(data_se, key_order_se, self.text_se)
        
        return True
        
    # ======================================================================= #
    def _get_latest_run(self, year, run):
        """
            Get run number of latest run in local file system, given an initial 
            part of the run number
        """
        
        runlist = []
            
        # look for latest run by run number
        for d in [self.bfit.bnmr_archive_label, self.bfit.bnqr_archive_label]:
            if d not in os.environ.keys():
                if 'BNMR' in d.upper():
                    dirloc = os.path.join(bd._mud_data, 'bnmr')
                else:
                    dirloc = os.path.join(bd._mud_data, 'bnqr')
            else:
                dirloc = os.environ[d]
            runlist.extend(glob.glob(os.path.join(dirloc, str(year), '0%d*.msr'%run)))
        runlist = [int(os.path.splitext(os.path.basename(r))[0]) for r in runlist]
        
        # get latest run by max run number
        try:
            run = max(runlist)
        except ValueError:
            self.logger.exception('Run fetch failed')
            for t in [self.text_nw, self.text_ne, self.text_sw, self.text_se]:
                self.set_textbox_text(t, 'Run not found.')  
            return False
        else:
            return run
        
    # ======================================================================= #
    def draw(self, figstyle, quiet=False):
        """Get data then draw."""
        self.bfit.logger.info('Draw button pressed')
        
        if self.get_data(quiet=quiet):
            self.data.draw(self.asym_type.get(), 
                           label=self.bfit.get_label(self.data), 
                           figstyle=figstyle)
            
    # ======================================================================= #
    def draw_diagnostics(self): #incomplete
        """
            Get data then draw in debug mode.
        """
        
        # isssue with data fetch
        if not self.get_data(quiet=quiet):
            return
        
        # get data
        dat = self.data
    
        # make figure
        fix, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=2, ncols=2)
    
        # get asym
        a = data.asym(hist_select=self.bit.hist_select)
        x = a[self.x_tag[data.mode]]
        xlabel = self.xlabel_dict[data.mode]
            
        # draw 2e mode 
        if '2e' == dat.mode:
            pass 
            
        # draw TD mode
        elif '2' in dat.mode:
            
            # draw combined asym -------------------------
            tag = a.c[0]!=0 # remove zero asym
            ax1.errorbar(x[tag], a.c[0][tag], a.c[1][tag])
            ax1.set_xlabel(xlabel)
            ax1.set_ylabel(self.bfit.ylabel_dict['c'])
            
            # draw split asym ----------------------------
            
            # remove zero asym
            ap = a.p[0]
            an = a.n[0]
            tag_p = ap!=0
            tag_n = an!=0
            tag_cmb = tag_p*tag_n
            
            # get average
            avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
            
            # draw
            ax2.errorbar(x[tag_p], ap[tag_p], a.p[1][tag_p], label='+')
            ax2.errorbar(x[tag_n], an[tag_n], a.n[1][tag_n], label="-")
            ax2.axhline(avg, color='k', linestyle='--')
            ax2.set_xlabel(xlabel)
            ax2.set_ylabel(self.bfit.ylabel_dict['h'])
        
            # draw histograms  --------------------------
            hist = data.hist
            
            # draw
            keylist = ('F+', 'F-', 'B+', 'B-', 'L+', 'R+', 'L-', 'R-', 
                         'NBMF+', 'NBMF-', 'NBMB+', 'NBMB-', 'AL0+', 'AL0-')
            for i, h in enumerate(keylist):
                
                # get bins
                try:
                    x = np.arange(len(hist[h].data))
                except KeyError:
                    continue
                
                # check for non-empty histograms, then draw
                if np.mean(hist[h].data) > 0:                        
                    ax3.plot(x, hist[h].data, label=h)
                    
            ax3.ylabel(self.bfit.ylabel_dict['rhist'])
            ax3.xlabel('Bin')
        
        # draw TI mode
        elif '1' in dat.mode:
            pass
        
        # unknown mode
        else:
            raise RuntimeError('Unknown mode type')
    
    # ======================================================================= #
    def export(self, filename=None):
        """Export data as csv"""
        
        self.logger.info('Export button pressed')
        
        # get data
        if not self.get_data():
            return
        data = self.data
        
        # get filename 
        if filename is None:
            filename = filedialog.asksaveasfilename(
                initialfile=self.default_export_filename%(data.year, data.run), 
                filetypes=[('csv', '*.csv'), 
                           ('allfiles', '*')], 
                defaultextension='.csv')
        
        # write to file
        if filename:
            self.bfit.export(data, filename, rebin=self.rebin.get())
    
    # ======================================================================= #
    def get_data(self, quiet=False):
        """
            Display data and send bdata object to bfit draw list. 
            Return True on success, false on Failure
        """
        
        if self.filename != '':
            return self._get_data(bdata(0, filename=self.filename))
        
        # fetch year
        try:
            year = self.year.get()
        except ValueError:
            for t in [self.text_nw, self.text_ne, self.text_sw, self.text_se]:
                self.set_textbox_text(t, 'Year input must be integer valued')  
                self.logger.exception('Year input must be integer valued')
            return False
        
        # fetch run number
        run = self.runn.get()
        
        self.logger.debug('Parsing run input %s', run)
        
        if run < 40000:
            run = self._get_latest_run(year, run)
            if run is False:
                return False
        
        # check for merged runs
        if run > 50000:
            
            # split run number
            run = str(run)
            run = [int(run[i:i+5]) for i in range(0, len(run), 5)]
            
            # split year number - note to self: update in 1000 years
            if year > 3000:
                year = str(year)
                year = [int(year[i:i+4]) for i in range(0, len(year), 4)]
            else:
                year = [year]*len(run)
            
            # get data
            data = bmerged([bdata(r, year=y) for r, y in zip(run, year)])
            
        else:
            data = bdata(run, year=year)
        
        self.logger.info('Fetching run %s from %s', run, year)
        
        return self._get_data(data, quiet=quiet)
        
    # ======================================================================= #
    def load_file(self, filename=None):
        """
            Read data based on filename rather than run number
            
            return True on success and False on failure
        """
        
        # get filename
        if filename is None:
            
            if self.filename == '':
                filename = filedialog.askopenfilename(filetypes=[('msr', '*.msr'),
                                                             ('allfiles', '*')])
                if not filename:
                    return False    
            else:
                filename = ''
        
        # set filename
        self.logger.debug('self.filename = %s', filename)
        self.filename = filename
        
        # get data
        if filename != '':
            self.logger.info('Fetching run %s', filename)
            self.button_run_from_file['text'] = 'Stop loading run from file'
            self.entry_year['state'] = 'disabled'
            self.entry_runn['state'] = 'disabled'
            return self._get_data(bdata(0, filename=filename))
        else:
            self.button_run_from_file['text'] = 'Load run from file'
            self.entry_year['state'] = 'normal'
            self.entry_runn['state'] = 'normal'
            return True
                    
    # ======================================================================= #
    def set_rebin(self, data):
        """
            Link rebin intvar to that of data object
            data: fitdata obj
        """
        value = self.rebin.get()
        self.rebin = data.rebin
        self.rebin.set(value)
        self.entry_rebin.configure(textvariable = data.rebin)
        
    # ======================================================================= #
    def set_nbm(self):
        """
            Set the nbm variable based on the run mode
        """
        
        # check if data
        if not hasattr(self, 'data'):
            return
        
        # check run mode
        mode = self.data.mode
        
        self.bfit.set_nbm(mode)

    # ======================================================================= #
    def set_textbox_text(self, textbox, text):
        """Set the text in a tkinter Text widget"""
        textbox.delete('1.0', END)
        textbox.insert('1.0', text)
        
    # ======================================================================= #
    def do_update(self, first=True, runid=''):
        self.logger.debug('Draw via periodic update')
        
        # update stop condition
        if runid and runid != self.update_id:
            return
        
        # select period drawing figure
        if first:
            
            first = False
            
            # check that there is a canvas, if not, draw
            if self.bfit.plt.active['inspect'] == 0:
                self.draw('inspect', quiet=False)
                first = True
            
            # set up updating canvas
            fig = self.bfit.plt.gcf('inspect')
            fig.canvas.manager.set_window_title('Figure %d (Inspect - Updating)'%fig.number)
            self.bfit.plt.plots['periodic'] = [fig.number]
            self.bfit.plt.active['periodic'] = self.bfit.plt.active['inspect']
            
            runid = self.data.id
            self.update_id = runid
            
            # repeat
            if not first:
                self.bfit.root.after(self.bfit.update_period*1000, 
                                     lambda:self.do_update(first=False, 
                                                           runid=runid))
                return
        
        # update 
        if self.is_updating.get():
            
            # check that figure exists or is not updating (was closed)
            if self.bfit.plt.active['periodic'] not in self.bfit.plt.plots['inspect']: 
                self.is_updating.set(False)
                del self.bfit.plt.plots['periodic'][0]
                self.bfit.plt.active['periodic'] = 0
                return
            
            # Get the updating figure
            fig = self.bfit.plt.gcf('periodic')
            title = fig.canvas.manager.get_window_title()

            # Check that the figure is still updating
            if 'Updating' not in title:
                self.is_updating.set(False)
                del self.bfit.plt.plots['periodic'][0]
                self.bfit.plt.active['periodic'] = 0
                return
            
            # update run
            year, run = tuple(map(int, runid.split('.')[:2]))
            current_year = self.year.get()
            current_run = self.runn.get()
            
            self.year.set(year)
            self.runn.set(run)
            
            # check current run 
            if current_run < 40000:
                current_run2 = self._get_latest_run(current_year, current_run)
                if current_run2 is False:
                    return 
            else:
                current_run2 = current_run
                
            # update only in stack mode
            draw_style = self.bfit.draw_style.get()
            self.bfit.draw_style.set('stack')
            
            # don't update figure limits
            if self.data.mode in ('20', '2h'):
                self.bfit.plt.autoscale('periodic', False)
                
            # draw
            self.draw(figstyle='periodic', quiet=True)
            draw_style = self.bfit.draw_style.set(draw_style)
            
            # reset year and run 
            do_quiet = (current_run2 != run) or (current_year != year)
            
            self.year.set(current_year)
            self.runn.set(current_run)
            self.get_data(quiet=do_quiet)
            
            # Print update message
            print('Updated figure at:', str(datetime.datetime.now()).split('.')[0], 
                  flush=True)
            
            # repeat
            self.bfit.root.after(self.bfit.update_period*1000, 
                                 lambda:self.do_update(first=False, runid=runid))
            
        # remove window from updating list
        else:
            # check if window already removed 
            if self.bfit.plt.active['periodic'] != 0:
                
                # remove window
                fig = self.bfit.plt.gcf('periodic')
                fig.canvas.manager.set_window_title('Figure %d (Inspect)'%fig.number)
                
                self.bfit.plt.autoscale('periodic', True)
                del self.bfit.plt.plots['periodic'][0]
                self.bfit.plt.active['periodic'] = 0
            
# =========================================================================== #
def num_prefix(val):
    if val > 1e9: return (val/1e9, 'G')
    if val > 1e6: return (val/1e6, 'M')
    if val > 1e3: return (val/1e3, 'k')
    
    return (val, '')
