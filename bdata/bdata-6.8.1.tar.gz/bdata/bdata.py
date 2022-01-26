# Python object for reading bnmr and bnqr msr data files. 
# Requires use of the mudpy package.
# Derek Fujimoto
# July 2017

import bdata as bd
import numpy as np
import pandas as pd
import os, glob, re
import datetime, warnings, requests
from .exceptions import MinimizationError, InputError, DkeyWarning, IOWarning
from .containers import hdict, vdict

from mudpy import mdata
from mudpy.containers import mdict, mvar, mhist
from iminuit import Minuit
from scipy.optimize import curve_fit

__doc__="""
    Beta-data module. The bdata object is largely a data container, designed to 
    read out the MUD data files and to provide user-friendly access to 
    BNMR/BNQR data. Data files are read either from a directory specified by 
    environment variable (see below), or from a passed filename for easy 
    external user access. In this case, data files can be downloaded from 
    musr.ca. The MUD data file is read and closed on object construction. 
    
    Signature: bdata(run_number, year=None, filename='')
    
    Example usage ------------------------------------------------------------
    
        import bdata as bd
        b = bd.bdata(40001)                  # read run 40001 from current year. 
        b = bd.bdata(40001, year=2009)       # read run 40001 from year 2009.
        b = bd.bdata(filename='file.msr')    # read file from local memory, run 
                                               number unused.
    Methods ------------------------------------------------------------------
    
        b.asym()            # calculate asymmetry. See bdata.asym docstring.     
        b.beam_kev()        # returns beam energy in keV
        b.pulse_off_s()     # pulse-off time for SLR measurements: 

    Setup --------------------------------------------------------------------
    
        bdata will download the mssr data files from musr.ca automatically and 
        save them under the install location by default. 
        
        To specify the data directory, set environment variables BNMR_ARCHIVE 
        and BNQR_ARCHIVE such that one can access the msr files according to 
        the following scheme:
        
        ${BNMR_ARCHIVE}/year/filename
        ${BNQR_ARCHIVE}/year/filename

        This may be preferred if access to data prior to archival is desired. 

    Features -----------------------------------------------------------------
    
        Representation 
    
            Representation has been nicely formatted so that typing the object 
            name into the interpreter produces nice output. 
        
        Operators
            
            mvar, mscaler, and mhist objects allow for arithmatic or logic 
            operators to be used, where the value used in the operation is the 
            mean, count, or data array respectively. 
            
            Example:    b.ppg.bias15 + 1       
            is equivalent to 
                        b.ppg.bias15.mean + 1
        
        Special Rules For Attributes
        
            If an attribute is not found in bdata, it will look for the 
            attribute in the mdict objects in the order: camp, epics, ppg, hist.
            This second-level attribute search is much slower than regular 
            access.
            
            mdict objects all allow assignment and fetching of dictionary keys 
            as if they were attributes. Note that one can replace "+" with "p", 
            and "-" with "m" to allow fetching of histograms. 
        
            Example: b.ppg.beam_on, bd.ppg['beam_on'], bd.beam_on all have the 
                     exact same output, with the last being much slower than 
                     the others.
    
    Derek Fujimoto
    Nov 2019
"""

# =========================================================================== #
class bdata(mdata):
    """
        Class fields 
            dkeys
            evar_bnmr
            evar_bnqr
            
        Data fields
            ppg
            epics
            camp
            + inherited fields from mdata
                        
        Public functions
            asym
            beam_kev
            pulse_off_s
            
        Private worker functions
            __init__
            __getattr__
            __repr__
            __setattr__
            _get_area_data
            _get_asym_hel
            _get_asym_comb
            _get_asym_alpha
            _get_asym_alpha_tag
            _get_1f_sum_scans
            _get_2e_asym
            _get_ppg
            _get_xhist
            _rebin
    """
    
    # set nice dictionary keys 
    
    # PPG (just the stuff after the last "/")
    dkeys_ppg = {
        "e20 beam on dwelltimes"            :"beam_on", 
        "e00 beam on dwelltimes"            :"beam_on", 
        "e20  beam off dwelltimes"          :"beam_off", 
        "e20 beam off dwelltimes"           :"beam_off",   
        "e00 beam off dwelltimes"           :"beam_off",   
        "beam off time (ms)"                :"beam_off_ms", 
                                                    
        "constant time between cycles"      :"const_t_btwn_cycl", 
        "e1f const time between cycles"     :"const_t_btwn_cycl", 
        
        "Custom var enabled"                :"customv_enable", 
        "Custom var read name"              :"customv_name_read",    
        "Custom var write name"             :"customv_name_write",   
         
        "Start custom scan"                 :"customv_scan_start",    
        "Stop custom scan"                  :"customv_scan_stop",    
        "Custom Increment"                  :"customv_scan_incr", 
        
        "scan device"                       :"scan_device",
        
        "scan start"                        :"scan_start",
        "scan stop"                         :"scan_stop",
        "scan incr"                         :"scan_incr",
        "scan increment"                    :"scan_incr",
        
        "NaVolt start (volts)"              :"scan_start", 
        "NaVolt stop (volts)"               :"scan_stop", 
        "NaVolt inc (volts)"                :"scan_incr", 
        
        "laser start (volts)"               :"scan_start", 
        "laser stop (volts)"                :"scan_stop", 
        "laser inc (volts)"                 :"scan_incr", 
       
        "field start (gauss)"               :"scan_start", 
        "field stop (gauss)"                :"scan_stop", 
        "field inc (gauss)"                 :"scan_incr", 
                                                    
        "DAQ drives sampleref"              :"smpl_ref_daq_drive", 
        "DAQ service time (ms)"             :"service_t", 
        "Dwell time (ms)"                   :"dwelltime", 
        "Bin width (ms)"                    :"dwelltime", 
                                                    
        "Enable helicity flipping"          :"hel_enable", 
        "Enable RF"                         :"rf_enable", 
        "enable sampleref mode"             :"smpl_ref_enable", 
        
        "Field start (Gauss)"               :"field_start", 
        "Field stop (Gauss)"                :"field_stop",    
        "Field inc (Gauss)"                 :"field_incr", 
        
        "frequency increment (Hz)"          :"freq_incr", 
        "frequency start (Hz)"              :"freq_start", 
        "frequency stop (Hz)"               :"freq_stop", 
        
        "scan var histo factor"             :"scan_var_histo_factor",
        
        "init mode file"                    :"init_mode", 
        "init mode"                         :"init_mode", 
                                                    
        "helicity flip sleep (ms)"          :"hel_sleep", 
        "Helicity flip sleep(ms)"           :"hel_sleep", 
                                                                                                
        "num bins"                          :"nbins", 
        "num cycles per supercycle"         :"ncycles", 
        "Number dwelltimes per freq"        :"ndwell_per_f", 
        "number of midbnmr regions"         :"nregion", 
        "num post RF beamOn dwelltimes"     :"ndwell_post_on", 
                               
        "Param X Start"                     :'xstart', 
        "Param X Stop"                      :'xstop', 
        "Param X Incr"                      :'xincr', 
        "Constant param Y"                  :'yconst', 
        
        "f1 frequency function"             :"freqfn_f1", 
        "f2 frequency function"             :"freqfn_f2", 
        "f3 frequency function"             :"freqfn_f3", 
        "f4 frequency function"             :"freqfn_f4", 
                                                    
        "PPG mode"                          :"mode",     
        "e20 prebeam dwelltimes"            :"prebeam", 
        "e00 prebeam dwelltimes"            :"prebeam", 
        "psm onef enabled"                  :"onef_enable", 
        "psm onef scale factor"             :"onef_scale", 
        "psm fREF enabled"                  :"fref_enable", 
        "psm fREF scale factor"             :"fref_scale", 
        "psm scale factor"                  :"psm_scale", 
        "psm scaler factor"                 :"psm_scale", 
                                                    
        "randomize freq increments"         :"rand_freq_incr", 
        "Randomize freq values"             :"rand_freq_val", 
        "Ref tuning freq (Hz)"              :"ref_tune_freq", 
        "Ref tuning frequency (Hz)"         :"ref_tune_freq", 
        "e20 rf frequency (Hz)"             :"freq", 
        "e00 rf frequency (Hz)"             :"freq", 
        "RFon delay (dwelltimes)"           :"rf_on_delay", 
        "num RF on delays (dwell times)"    :"rf_on_delay", 
        "RFon duration (dwelltimes)"        :"rf_on", 
        "RF on time (ms)"                   :"rf_on_ms", 
        "RF enabled"                        :"rf_enable", 
        
        'num finer freq regions'            :'fine_freq_nregions',
        'fine freq start  (hz)'             :'fine_freq_start',
        'fine freq end  (hz)'               :'fine_freq_end',
        'fine freq increment  (hz)'         :'fine_freq_increment',
        
        "Single tone simulated"             :"sgle_tone_sim", 
                                                    
        "use defaults for midbnmr"          :"defaults", 
        
        "probe species"                     :"probe_species",
    }
    
    # CAMP
    dkeys_camp = {
        
        "/biasV/input1"                             :"rb_cell_bias_set", 
        "/biasV/output1"                            :"rb_cell_bias_read", 
    
        "/CryoEx_MassFlow/read_flow"                :"cryo_read", 
        "/CryoEx_MassFlow/set_flow"                 :"cryo_set", 
        "/Cryo_level/He_level"                      :"cryo_he", 
        "/Cryo_level/N2_level"                      :"cryo_n2", 
        "/cryo_lift/set_position"                   :"clift_set",  
        "/cryo_lift/read_position"                  :"clift_read", 
        
        "/Cryo_oven/current_read_1"                 :"oven_current", 
        "/Cryo_oven/output_1/D"                     :"oven_out_d", 
        "/Cryo_oven/output_1/I"                     :"oven_out_i", 
        "/Cryo_oven/output_1/P"                     :"oven_out_p", 
        "/Cryo_oven/read_A"                         :"oven_readA", 
        "/Cryo_oven/read_B"                         :"oven_readB", 
        "/Cryo_oven/read_C"                         :"oven_readC", 
        "/Cryo_oven/read_D"                         :"oven_readD", 
        "/Cryo_oven/setpoint_1"                     :"oven_set1", 
                    
        "/Dac0/dac_set"                             :"dac_set", 
        "/dac/dac_set"                              :"dac_set", 
        "/Dewar/He_level"                           :"he_level", 
         
        "/flow_set/output"                          :"flow_set_out", 
                                                
        "/He_flow/read_flow"                        :"he_read", 
        "/He_flow/set_flow"                         :"he_set", 
                                                
        "/lock-in/R"                                :"lockin_r", 
        "/lock-in/theta"                            :"lockin_theta", 
        "/lock-in/X"                                :"lockin_x", 
        "/lock-in/Y"                                :"lockin_y", 
                                                
        "/Magnet/mag_field"                         :"b_field",     
        "/Magnet/mag_set"                           :"b_field_setpt",     
        "/Magnet/mag_read"                          :"mag_current", 
        "/Magnet/controls/sys_status"               :"mag_ctrl_status", 
        "/Magnet/ramp_status"                       :"mag_ramp_status", 
        "/Magnet/volts"                             :"mag_voltage", 
        "/mass_flow/read_flow"                      :"mass_read", 
        "/mass_flow/set_flow"                       :"mass_set",   
                                                
        "/needle-valve/read_position"               :"needle_read", 
        "/Needle/read_position"                     :"needle_pos", 
        "/Needle/motor_position"                    :"needle_pos", 
        "/needle-valve/set_position"                :"needle_set", 
        "/Needle_Valve/set_position"                :"needle_set", 
        "/Needle/set_position"                      :"needle_set", 
        
        "/PVac/adc_read"                            :"vac", 
                                                
        "/rfamp/fwd_max"                            :"rfamp_fwd", 
        "/rfamp/fwd_power"                          :"rfamp_fpwr", 
        "/rfamp/refl_max"                           :"rfamp_rfl", 
        "/rfamp/RF_gain"                            :"rfamp_rfgain", 
        "/rf_level_cont/dac_set"                    :"rf_dac", 
                                                
        "/Sample/current_read_1"                    :"smpl_current", 
        "/Sample/current_read"                      :"smpl_current", 
        "/Sample1/current_read"                     :"smpl_current", 
        "/Sample/sample_read"                       :"smpl_read_A", 
        "/Sample/read_A"                            :"smpl_read_A", 
        "/Sample1/read_A"                           :"smpl_read_A", 
        "/Sample/read_B"                            :"smpl_read_B", 
        "/Sample1/read_B"                           :"smpl_read_B", 
        "/adc0/adc_read"                            :"smpl_read_B", 
        "/Sample/read_C"                            :"smpl_read_C", 
        "/Sample/read_D"                            :"smpl_read_D", 
        "/Sample/set_current"                       :"smpl_set_current", 
        "/Sample/setpoint"                          :"smpl_set", 
        "/Sample1/setpoint"                         :"smpl_set", 
        "/Sample/setpoint_1"                        :"smpl_set", 
        "/sample2/heat_range"                       :"smpl2_heat", 
        "/sample2/sample_read"                      :"smpl2_read", 
        "/sample_volts/reading"                     :"smpl_volts", 
        "/Shield/read_1"                            :"shield_read1", 
        "/signal_gen/amplitude"                     :"sig_gen_amp", 
        "/signal_gen/frequency"                     :"sig_gen_freq", 
        "/signal_gen/power_level"                   :"sig_gen_pwr", 
        "/signal_gen/rf_on"                         :"sig_gen_rfon", 
        "/stealth/fwd_max"                          :"stealth_fwd_max", 
        "/stealth/fwd_power"                        :"stealth_fwd_pwr", 
        "/stealth/rev_max"                          :"stealth_rev_max", 
        "/stealth/rev_power"                        :"stealth_rev_pwr", 
    }
    
    # EPICS
    dkeys_epics = {
        "BNMR:HVBIAS:P"                             :"nmr_bias", 
        "BNMR:HVBIAS:PO"                            :"nmr_bias", 
        "BNMR:HVBIAS:POS"                           :"nmr_bias", 
        "BNMR:HVBIAS:POS:"                          :"nmr_bias", 
        "BNMR:HVBIAS:POS:R"                         :"nmr_bias", 
        "BNMR:HVBIAS:POS:RDVO"                      :"nmr_bias", 
        "BNMR:HVBIAS:POS:RDVOL"                     :"nmr_bias", 
        "BNMR:HVBIAS:POS:RDVOL1"                    :"nmr_bias", 
                                              
        "BNMR:HVBIAS:N"                             :"nmr_bias_n", 
        "BNMR:HVBIAS:NE"                            :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG"                           :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG:"                          :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG:R"                         :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG:RDVO"                      :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG:RDVOL"                     :"nmr_bias_n", 
        "BNMR:HVBIAS:NEG:RDVOL1"                    :"nmr_bias_n", 
                                              
        "BNQR:HVBIAS:RD"                            :"nqr_bias", 
        "BNQR:HVBIAS:RDVOL"                         :"nqr_bias", 
                                              
        "ITE:BIAS:RDVO"                             :"target_bias",  
        "ITE:BIAS:RDVOL"                            :"target_bias",  
        "ITE:BIAS:RDVOLER"                          :"target_bias",  
        "ITE:BIAS:RDVOLVOL"                         :"target_bias", 
        "ITW:BIAS:R"                                :"target_bias", 
        "ITW:BIAS:RD"                               :"target_bias", 
        "ITW:BIAS:RDV"                              :"target_bias", 
        "ITW:BIAS:RDVO"                             :"target_bias", 
        "ITW:BIAS:RDVOL"                            :"target_bias", 
        "ITW:BIAS:RDVOL1"                           :"target_bias", 
        "ITW:BIAS:RDVOLVOL"                         :"target_bias", 
                                              
        "ILE2:BIAS15:R"                             :"bias15", 
        "ILE2:BIAS15:RD"                            :"bias15", 
        "ILE2:BIAS15:RDV"                           :"bias15", 
        "ILE2:BIAS15:RDVO"                          :"bias15",    
        "ILE2:BIAS15:RDVOL"                         :"bias15", 
                                              
        "ILE2:LAS:RDPO"                             :"las_pwr", 
        "ILE2:LAS:RDPOW"                            :"las_pwr", 
        "ILE2:LAS:RDPOWE"                           :"las_pwr", 
        "ILE2:LAS:RDPOWER"                          :"las_pwr", 
        "ILE2:LAS:RDPOWERL"                         :"las_pwr", 
         
        "ILE2:BIASTUBE:"                            :"biastube", 
        "ILE2:BIASTUBE:V"                           :"biastube", 
        "ILE2:BIASTUBE:VOL"                         :"biastube", 
        "ILE2:BIASTUBE:RDVOL"                       :"biastube", 
         
        "ILE2:DPPLR:CH0:HW:RDVOL"                   :"dopplertube_ch0", 
        "ILE2:DPPLR:CH1:HW:RDVOL"                   :"dopplertube_ch1", 
        "ILE2:DPPLR:CH2:HW:RDVOL"                   :"dopplertube_ch2", 
        
        "BNMR:EL3:RDVOL"                            :"el3", 
         
        "ILE2A1:HH:CUR"                             :"hh_current", 
        "ILE2A1:HH:RDCU"                            :"hh_current", 
        "ILE2A1:HH:RDCUR"                           :"hh_current", 
        "ILE2A1:HH3:RDCUR"                          :"hh_current", 
        
        "ILE2A1:HH6:RDCUR"                          :"hh6_current", 
        
        "TRILIS177:METER:LAMBDA1"                   :"las_lambda",
        "TRILIS177:METER:WAVENUM1"                  :"las_wavenum",
    }
    
    dkeys = {"":"", **dkeys_camp, **dkeys_epics, **dkeys_ppg}
    
    # mapping from old run attributes to new run attributes
    old_attr = {  
        # histogram names
            'FREQ'          :'Frequency', 
            'Bp'            :'B+', 
            'back+'         :'B+',
            'Fp'            :'F+', 
            'front+'        :'F+',
            'Bm'            :'B-', 
            'back-'         :'B-',
            'Fm'            :'F-', 
            'front-'        :'F-',
            'FluM'          :'FluM2', 
            'FluorMon2'     :'FluM2',
            'PolLp'         :'L+', 
            'PolLeft+'      :'L+',
            'PolRp'         :'R+', 
            'PolRight+'     :'R+', 
            'PolLm'         :'L-',
            'PolLeft-'      :'L-',
            'PolRm'         :'R-', 
            'PolRight-'     :'R-',
            'NBMBp'         :'NBMB+', 
            'NeutBmB+'      :'NBMB+',
            'NBMFp'         :'NBMF+', 
            'NeutBmF+'      :'NBMF+',
            'NBMBm'         :'NBMB-', 
            'NeutBmB-'      :'NBMB-',
            'NBMFm'         :'NBMF-', 
            'NeutBmF-'      :'NBMF-',
        
        # method to mode conversion
            'TI-Bnmr'       :'1f',
            'TI-bNMR'       :'1f',
            
            'TD-Bnmr'       :'20',
            'TD-bNMR'       :'20',

        # apparatus
            'bnmr2'         :'BNMR',
            'bnmr'          :'BNMR',
        }
    
    # options for asymmetry calculation
    option = {  ''                      :'',
                
                'adif'                  :'alpha_diffusion',
                'ad'                    :'alpha_diffusion',
                'adiff'                 :'alpha_diffusion',
                
                'atag'                  :'alpha_tagged',
                'at'                    :'alpha_tagged',
                
                'b'                     :'backward_counter',
                'bck'                   :'backward_counter',
                'left'                  :'backward_counter',
                'left_counter'          :'backward_counter',
                
                'c'                     :'combined',
                'com'                   :'combined',
                
                'cntr'                  :'counter',
                
                'dif_c'                 :'difference_combined', 
                'dc'                    :'difference_combined', 
                
                'dif_h'                 :'difference_helicity',
                'dh'                    :'difference_helicity',
                
                'f'                     :'forward_counter',
                'fwd'                   :'forward_counter',
                'right'                 :'forward_counter',
                'right_counter'         :'forward_counter',
                
                '+'                     :'positive', 
                'up'                    :'positive', 
                'u'                     :'positive', 
                'p'                     :'positive',
                'pos'                   :'positive', 
                
                '-'                     :'negative',
                'down'                  :'negative', 
                'd'                     :'negative',
                'n'                     :'negative',
                'neg'                   :'negative',
                
                'h'                     :'helicity',
                'hel'                   :'helicity',
                
                'r'                     :'raw',
                
                'rs'                    :'raw_split_scan',
                'raw_split'             :'raw_split_scan',
                
                'raw_c'                 :'raw_combined',
                'rc'                    :'raw_combined',
                
                'raw_h'                 :'raw_helicity',
                'rh'                    :'raw_helicity',
                
                'sl_c'                  :'slope_combined',
                'slc'                   :'slope_combined', 
                'sc'                    :'slope_combined',
                
                'sl_h'                  :'slope_helicity',
                'slh'                   :'slope_helicity',
                'sh'                    :'slope_helicity',
    }
    
    # output keys for mode TI runs
    mode1_dict = {  '1f': 'freq',
                    '1x': 'freq',
                    '1w': 'xpar',
                    '1n': 'mV',
                    '1e': 'mA',
                    '1c': 'camp',
                    '1d': 'las',
                    }
    
    # set environment variable same to get data archive location
    # should point to something like
    # "/data1/bnmr/dlog/" on linbnmr2
    # "/data/bnmr/" on muesli or lincmms
    evar_bnmr = "BNMR_ARCHIVE"
    evar_bnqr = "BNQR_ARCHIVE"
    
    # ======================================================================= #
    def __init__(self, run_number=None, year=None, filename=""):
        """Constructor. Reads file, stores and sorts data."""
            
        # check input
        if run_number is None and filename == '':
            raise InputError("Bad input, specify either run_number or filename")
            
        # convert dkeys keys to lower case
        bdata.dkeys = {k.lower():i for k, i in self.dkeys.items()}
            
        # Get the current year
        if year is None:   year = datetime.datetime.now().year
        
        # read file if not provided
        if filename == "":
            
            # Get spectrometer directory. Based on rmlm's bnmr_20a.cpp.
            if run_number >= 40000 and run_number <= 44999:
                spect_dir = "bnmr"
            elif run_number >= 45000 and run_number <= 49999:
                spect_dir = "bnqr"
            else:
                raise ValueError("Run number out of range") 
                
            # look for data location
            if spect_dir == "bnmr":
                
                use_default_dir = not self.evar_bnmr in os.environ
                if use_default_dir:
                    directory = os.path.join(bd._mud_data, spect_dir)
                else:
                    directory = os.environ[self.evar_bnmr]
                    
            elif spect_dir == "bnqr":
                
                use_default_dir = not self.evar_bnqr in os.environ
                if use_default_dir:
                    directory = os.path.join(bd._mud_data, spect_dir)
                else:
                    directory = os.environ[self.evar_bnqr]
                    
            # finalize file name
            run = '%06d.msr' % run_number
            filename = os.path.join(directory, str(year), run)

            # check if file is link - follow the link
            if os.path.islink(filename):
                path = os.path.split(filename)[0]
                filename = os.path.split(os.readlink(filename))[-1]
                filename = os.path.join(path, filename)
            
            # if file does not exist, try to fetch from web
            if not os.path.isfile(filename):
                
                # make directory 
                os.makedirs(os.path.join(directory, str(year)), exist_ok=True)
                
                # make url
                url = '/'.join(('http://musr.ca/mud/data', 
                                spect_dir.upper(), 
                                str(year), 
                                run))
            
                # get data
                webfile = requests.get(url)
                if not webfile.ok:
                    raise RuntimeError('File %s not found. '%filename+\
                                'Attempted download from musr.ca failed.')
                
                # write to file
                with open(filename, 'wb') as fid:
                    fid.write(webfile.content)
                
                # let users know what happened
                warnings.warn('Run %d (%d) not found '% (run_number, year)+\
                              'locally. Fetched and saved to %s '%directory+\
                              'from musr.ca.', 
                              category=IOWarning)
                        
        # Open and read file
        super().__init__(filename)
        
        # cast histogram data to floats
        if hasattr(self, 'hist'):
            for key, hist in self.hist.items():
                self.hist[key].data = hist.data.astype(np.float64)
            
        # Sort independent variables into dictionaries by title
        self.ppg = vdict()
        self.camp = vdict()
        self.epics = vdict()
        
        if hasattr(self, 'ivar'):
            
            for v in self.ivar.values(): 
                if 'PPG' in v.title:
                    title = v.title.split("/")[-1].lower()
                    title_default = re.sub('\W', '', title.replace(' ', '_'))            
                    
                    # check for 1x mode keys
                    if title not in bdata.dkeys.keys():
                        
                        title_1x = re.sub('[0-9]', '', title)
                        if title_1x in bdata.dkeys.keys():
                            new_title = bdata.dkeys[title_1x]
                            
                            try:
                                num = re.search(r'\d+', title).group()
                            except AttributeError:
                                self.ppg[bdata.dkeys.get(title, title_default)] = v
                                continue
                                
                            new_title += '_%s' % num
                            self.ppg[new_title] = v
                            continue
                            
                    self.ppg[bdata.dkeys.get(title, title_default)] = v
                elif v.title == "":
                    pass
                elif v.title[0] == "/":
                    title = v.title.lower()
                    title_default = re.sub('\W', '', title.replace(' ', '_'))
                    self.camp[bdata.dkeys.get(title, title_default)] = v
                else:
                    title = v.title.lower()
                    title_default = re.sub('\W', '', title.replace(' ', '_'))
                    self.epics[bdata.dkeys.get(title, title_default)] = v
                    
                if title not in bdata.dkeys.keys() and 'fine freq' not in title:
                    message = '%d.%d: "%s" not found in dkeys ("%s").'
                    message = message % (self.year, self.run, v.title, v.description)
                    warnings.warn(message, DkeyWarning, stacklevel=2)
            
        # Fix attributes for old runs
        if year < 2005:
            if not self.mode: 
                self.mode = self.old_attr.get(self.method, self.method)
            self.apparatus = self.old_attr.get(self.apparatus, self.apparatus)
            
            # histogram titles
            hist = hdict()
            
            for k in self.hist.keys():
                newk = self.old_attr.get(k, k)
                hist[newk] = self.hist[k]
                hist[newk].title = newk
            self.hist = hist
        
        # Fix inconsistent area for old runs
        if self.area == 'ISAC':
            if self.run >= 45000:   self.area = 'BNQR'
            else:                   self.area = 'BNMR'
    
    # ======================================================================= #
    def __getattr__(self, name):
        
        if name in ('hist', 'camp', 'ppg', 'epics'):
            return getattr(object, name)
        
        else:

            # fetch from top level
            try:
                return getattr(object, name)
                
            # fetching of second level
            except AttributeError as err:
                if hasattr(self, 'camp') and hasattr(self.camp, name):
                    return getattr(self.camp, name)
                if hasattr(self, 'epics') and hasattr(self.epics, name): 
                    return getattr(self.epics, name)
                if hasattr(self, 'ppg') and hasattr(self.ppg, name): 
                    return getattr(self.ppg, name)
                if hasattr(self, 'hist') and hasattr(self.hist, name): 
                    return getattr(self.hist, name)
                        
                raise AttributeError(err) from None
                                
    # ======================================================================= #
    def __repr__(self):
        """
            Nice printing of parameters.
        """
        
        # get all attributes
        d = self.__dict__
        
        # add beam properties
        try: 
            d['beam_keV'] = self.beam_keV
            d['beam_keV_err'] = self.beam_keV_err
            d['pulse_s'] = self.pulse_s
        except AttributeError: 
            pass
        
        dkeys = list(d.keys())
        if dkeys:
            items = []
            dkeys.sort()
            for key in dkeys:
                if key[0] == '_': continue
                
                # exceptions
                if key in ('ivar', 'sclr'):
                    items.append([key, d[key].__class__])                
                    
                # non iterables and mdict objects
                elif not hasattr(d[key], '__iter__') or d[key].__class__ in (mdict, vdict, hdict):
                    items.append([key, d[key]])                
                
                # strings
                elif d[key].__class__ in (str, np.str_):
                    items.append([key, d[key]])                
                
                # misc objects
                else:
                    items.append([key, d[key].__class__])
                
                            
            m = max(map(len, dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"
        
    # ======================================================================= #
    def _beam_kev(self, get_error=False):
        """
            Get the beam energy in kev, based on typical biases: 
                itw (or ite bias) - bias15 - platform bias
                
            if get_error: fetch error in value, rather than value
        """
        
        # get epics pointer
        epics = self.epics
        
        # fetch stds
        if get_error:   attr = 'std'
        else:           attr = 'mean'
        
        # get inital beam energy in keV
        beam = getattr(epics.target_bias, attr)/1000.
            
        # get Rb cell voltage
        bias15 = getattr(epics.bias15, attr)/1000.
        
        # get platform bias 
        if self.area.upper() == 'BNMR':
            platform = getattr(epics.nmr_bias, attr)
        elif self.area.upper() == 'BNQR':
            platform = getattr(epics.nqr_bias, attr)/1000.
        else:
            raise RuntimeError('Area not recognized')
        
        if get_error:
            return np.sqrt(np.sum(np.square((beam, bias15, platform)))) # keV
        else:
            return beam-bias15-platform # keV
    
    # ======================================================================= #
    def _correct_baseline_combined(self, freq, F1, F2, B1, B2, options):
        """
            Correct sloped scan baseline in the case of combined asym calculation 
            1 = pos helicity
            2 = neg helicity
        """

        # parse input
        scan_comb_fn, \
        baseline_bins, \
        omit_incomplete_scan, \
        split_scan, \
        flatten_final_asym = self._parse_1f_baseline_options(options)
        
        # split into scans
        if baseline_bins or omit_incomplete_scan or split_scan:
                        
            # split into scans
            _, freq1_spl, F1_spl = self._split_scan(freq, F1, omit_incomplete_scan)
            _, freq2_spl, F2_spl = self._split_scan(freq, F2, omit_incomplete_scan)
            _, freq1_spl, B1_spl = self._split_scan(freq, B1, omit_incomplete_scan)
            _, freq2_spl, B2_spl = self._split_scan(freq, B2, omit_incomplete_scan)
            
            # correct baseline 
            if baseline_bins: 
                
                # get slopes of each helicity ratio
                def get_slopes(num, den, fre):
                    """
                        numerator, denominator, frequency
                    """
                    slopes = []
                    ratio = []
                    
                    for top, bot, fq in zip(num, den, fre):
                        
                        # get ratio
                        bot[bot==0] = np.nan
                        top[top==0] = np.nan
                        r = top/bot
                        dr = r * np.sqrt(1/top + 1/bot)
                        
                        # get slope
                        sl = self._get_baseline_slope(fq, r, dr, baseline_bins)
                        slopes.append(sl)
                        ratio.append(r)
                        
                    return (slopes, ratio)
                    
                slope1, ratio1 = get_slopes(B1_spl, F1_spl, freq1_spl)
                slope2, ratio2 = get_slopes(F2_spl, B2_spl, freq2_spl)
                    
                # do correction
                def do_correction(factor=1):
                    
                    # fix the numerator counter to get the correct resulting ratio
                    B1_fix = []
                    for r, sl, f, fq in zip(ratio1, slope1, F1_spl, freq1_spl):
                        g = r + factor*sl*(np.mean(fq) - fq)
                        B1_fix.append(g * f)
                    
                    F2_fix = []
                    for r, sl, b, fq in zip(ratio2, slope2, B2_spl, freq2_spl):
                        g = r + factor*sl*(np.mean(fq) - fq)
                        F2_fix.append(g * b)
                                        
                    # concat
                    F1 = np.concatenate(F1_spl)
                    B1 = np.concatenate(B1_fix)
                    freq1 = np.concatenate(freq1_spl)
                    
                    F2 = np.concatenate(F2_fix)
                    B2 = np.concatenate(B2_spl)
                    freq2 = np.concatenate(freq2_spl)
                    
                    # combine
                    freq1, (F1, B1) = scan_comb_fn([F1, B1], freq1)
                    freq2, (F2, B2) = scan_comb_fn([F2, B2], freq2)
                    
                    # check freq
                    assert all(freq1 == freq2), 'Frequency arrays not equal'
                    
                    # get asym
                    a, da = self._get_asym_4counter(F1, F2, B1, B2)
                    
                    return (freq1, a ,da)
                
                # get the overcorrection factor to flatten the final asym
                def get_factor(factor=1):
                    
                    freq, a, da = do_correction(factor)
                    
                    # get slope
                    sl = self._get_baseline_slope(freq, a, da, baseline_bins)
                    
                    return abs(sl*np.mean(freq))
                
                # get overcorrection
                factor = 1
                if flatten_final_asym:    
                    m = Minuit(get_factor, factor=1)
                    m.errordef = 1
                    m.migrad()
                    
                    if m.valid:
                        factor = m.values[0]
                        print('%d.%d: found combined overcorrection factor of %f' % \
                                (self.year, self.run, factor))
                    else:
                        print('%d.%d: overcorrection estimation failed' % \
                                (self.year, self.run))
                                
                # do correction again with factor
                freq, a, da = do_correction(factor)                
                
                return (freq, (a, da))

            # concat scans
            F1 = np.concatenate(F1_spl)
            B1 = np.concatenate(B1_spl)
            freq1 = np.concatenate(freq1_spl)
            
            F2 = np.concatenate(F2_spl)
            B2 = np.concatenate(B2_spl)
            freq2 = np.concatenate(freq2_spl)
            
            # sort scans
            idx = np.argsort(freq1)
            F1, B1, freq1 = F1[idx], B1[idx], freq1[idx]
            
            idx = np.argsort(freq2)
            F2, B2, freq2 = F2[idx], B2[idx], freq2[idx]
            
            # check freq
            assert all(freq1 == freq2), 'Frequency arrays not equal'
            freq = freq1
            
        # combine
        freq, (F1, F2, B1, B2) = scan_comb_fn([F1, F2, B1, B2], freq)
                
        # get asym
        a, da = self._get_asym_4counter(F1, F2, B1, B2)
        
        return (freq, (a, da))
    
    # ======================================================================= #
    def _correct_baseline_simple(self, freq, F, B, options):
        """
            Correct sloped scan baseline in the case of simple asym calculation 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # parse input
        scan_comb_fn, \
        baseline_bins, \
        omit_incomplete_scan, \
        split_scan, \
        flatten_final_asym = self._parse_1f_baseline_options(options)
        
        # split into scans
        if baseline_bins or omit_incomplete_scan or split_scan:
            
            # split into scans
            _, freq_spl, F_spl = self._split_scan(freq, F, omit_incomplete_scan)
            _, freq_spl, B_spl = self._split_scan(freq, B, omit_incomplete_scan)
            
            # correct baseline 
            if baseline_bins: 
                slopes = []
                asym = []
                
                # iterate on scans, fix each in turn
                for f, b, fq in zip(F_spl, B_spl, freq_spl):
                    
                    # get pre-modified asym
                    a, da = self._get_asym_simple(f, b)    
                                    
                    # get slopes
                    sl = self._get_baseline_slope(fq, a, da, baseline_bins)
                    slopes.append(sl)
                    asym.append(a)
                    
                # do correction
                def do_correction(factor=1):
                    # fix the forward counter to get the correct resulting ratio
                    F_spl2 = []
                    for a, sl, f, b, fq in zip(asym, slopes, F_spl, B_spl, freq_spl):                    
                        g = a + factor*sl*(np.mean(fq) - fq)
                        g[g == 1] = np.nan
                        F_spl2.append((1+g)/(1-g) * b)
                    
                    # combine
                    freq, (F, B) = scan_comb_fn([F_spl2, B_spl], freq_spl)
                    
                    # get asym
                    if type(F) is list: 
                        a = []
                        da = []
                        for f, b in zip(F, B):
                            a2 = self._get_asym_simple(f, b)
                            a.append(a2[0]) 
                            da.append(a2[1]) 
                    else:
                        a, da = self._get_asym_simple(F, B) 
                    
                    return (freq, a, da)
                
                # get the overcorrection factor to flatten the final asym
                def get_factor(factor=1):
                    
                    freq, a, da = do_correction(factor)
                    
                    # get slope
                    sl = self._get_baseline_slope(freq, a, da, baseline_bins)
                    
                    return abs(sl*np.mean(freq))
                
                # get overcorrection
                factor = 1
                if flatten_final_asym:    
                    m = Minuit(get_factor, factor=1)
                    m.errordef = 1
                    m.migrad()
                    
                    if m.valid:
                        factor = m.values[0]
                        print('%d.%d: found simple baseline over correction factor of %f' % \
                                (self.year, self.run, factor))
                    else:
                        print('%d.%d: baseline over-correction estimation failed' % \
                                (self.year, self.run))
                                
                # do correction again with factor
                freq, a, da = do_correction(factor)                
                
                return (freq, (a, da))

            F = F_spl
            B = B_spl
            freq = freq_spl
                
        # combine scans
        freq, (F, B) = scan_comb_fn([F, B], freq)
        
        # get asym: raw scans
        if type(F) is list:
            a = [] 
            da = []
            for f, b in zip(F, B):
                asym = self._get_asym_simple(f, b)
                a.append(asym[0])
                da.append(asym[1])
        
        # get asym: combined scans
        else:
            a, da = self._get_asym_simple(F, B)
        
        return (freq, (a, da))
        
    # ======================================================================= #
    def _correct_deadtime(self, d, deadtime):
        """
            Apply deadtime correction based on bnmrfit physical script named
            bnmr_fdt.pcm written by Jay and Zaher in June 2005
            
            d:          list of arrays for each counter as a function of time
            deadtime:   float 
        """
        
        try:
        
            # dwell time
            tdwell = self.ppg['dwelltime'].mean * 0.001
             
            # time to do one scan
            if self.mode in ('20', '2h', '00'):
                tscan = tdwell * (self.ppg['beam_on'].mean + \
                                  self.ppg['beam_off'].mean + \
                                  self.ppg['prebeam'].mean) \
                        + self.ppg['hel_sleep'].mean * 0.001

                # number of scans
                nscans = self.duration / tscan

            elif '1' in self.mode:
                nscans = self.ppg['nbins'].mean

        # missing PPG parameters
        except KeyError:    
            if deadtime > 0:
                warnings.warn(
                    "%d.%d: Missing PPG parameter(s), no deadtime correction applied" \
                        % (self.year, self.run),
                    Warning, stacklevel=2)
            return d
            
        # time per bin
        tbin = tdwell * nscans
        
        # apply correction 
        dnew = [di / (1 - di/tbin*deadtime) for di in d]
        
        return dnew
        
    # ======================================================================= #
    def _fix_prebeam_offbyone(self, d):
        """
            Fix the prebeam off by one error in NQR 20 and 2e runs, starting in 
            2018 (all runs) and ending with 45262 in 2020 (inclusive). 
            
            Issue: extra prebeam bin assigned. 
            
            Inputs: d - list of histograms
        """
        
        # check if fix is needed
        if self.area.lower() == 'bnqr' and 2018 <= self.year <= 2020:
            if self.year == 2020 and self.run > 45262:
                pass
            else: 
                
                # double check if fix is needed
                if np.sum(np.array(d)[:, 0]) > 100:
                    return d
                
                # do the fix: remove extra bin
                for i in range(len(d)):                    
                    d[i] = np.delete(d[i], [0])
        return d
                        
    # ======================================================================= #
    def _get_area_data(self, nbm=False, hist_select=''):
        """Get histogram list based on area type.
        
        nbm: if True, get neutral beam monitor data
        hist_select: string of [,], [ ], [;], or [.] deliminated histogram titles
              expected order:   'F+, F-, B+, B-'
              or                'R+, R-, L+, L-'

        such that the output list pattern is: [1+, 1-, 2+, 2-]
        where   1 = F or R and
                2 = B or L
        
        Setting hist_select overrides any setting of nbm
                
        """
        
        # get histogram titles
        if hist_select != '':
            
            # replace deliminators with spaces
            for delim in ', ;.':
                hist_select = hist_select.replace(delim, ' ')
            
            # split into parts
            hist_select = [h.stip() for h in hist_select.split(' ') if h]
            
            # check for user error
            if len(hist_select) < 4:
                raise InputError('hist_select must be a string of at least '+\
                        'four histogram names deliminated by ",", "." ,";" '+\
                        'or a space.')
        
        elif nbm:
            hist_select = ('NBMF+', 'NBMF-', 'NBMB+', 'NBMB-')
        
        elif self.area.upper() == 'BNMR':
            hist_select = ('F+', 'F-', 'B+', 'B-')
            
        elif self.area.upper() == 'BNQR':
            hist_select = ['R+', 'R-', 'L+', 'L-']
            
            if self.mode == '2h':
                hist_select.extend(['AL1+', 'AL1-', 
                                    'AL0+', 'AL0-', 
                                    'AL3+', 'AL3-', 
                                    'AL2+', 'AL2-'])
        
        else:
            raise RuntimeError('Unable to fetch area data for %d.%d' % \
                                                        (self.year, self.run))
            
        # get data
        return [np.copy(self.hist[h].data) for h in hist_select]

    # ======================================================================= #
    def _get_asym_alpha(self, a, b):
        """
            Find alpha diffusion ratios from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)
            b: list of beta  detector histograms (each helicity)
            
            a/b = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # just  use AL0
        try:
            a = a[2:4]
        except IndexError:
            a = a[:2]
            
        # sum counts in alpha detectors
        asum = np.sum(a, axis=0)
        
        # sum counts in beta detectors
        bsum = np.sum(b, axis=0)
        
        # check for dividing by zero 
        asum[asum == 0] = np.nan
        bsum[bsum == 0] = np.nan
        
        # asym calcs
        asym = asum/bsum
        
        # errors
        dasym = asym*np.sqrt(1/asum + 1/bsum)
        
        return [asym, dasym]

    # ======================================================================= #
    def _get_asym_alpha_tag(self, a, b):
        """
            Find asymmetry from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)  
            b: list of beta  detector histograms (each helicity)  1+ 1- 2+ 2-
        """

        # beta in coincidence with alpha
        coin = a[:4]
        
        # beta coincidence with no alpha
        no_coin = a[4:8]

        # get split helicity asym from 
        hel_coin =      self._get_asym_hel(coin)
        hel_no_coin =   self._get_asym_hel(no_coin)
        hel_reg =       self._get_asym_hel(b)
        
        # get combined helicities
        com_coin =      self._get_asym_comb(coin)
        com_no_coin =   self._get_asym_comb(no_coin)
        com_reg =       self._get_asym_comb(b)

        # make output
        return (hel_coin, hel_no_coin, hel_reg, com_coin, com_no_coin, com_reg)
    
    # ======================================================================= #
    def _get_asym_bck(self, d, freq=None, options=''):
        """
            Find the asymmetry of backward counter using the asymmetries. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # get the relevant counters
        F = np.copy(d[2])
        B = np.copy(d[3])
        
        if '1' in self.mode: 
            return self._correct_baseline_simple(freq, F, B, options)
        elif '2' in self.mode:
            return self._get_asym_simple(F, B)    
        
    # ======================================================================= #
    def _get_asym_counter(self, d):
        """
            Find the asymmetry of each counter using the asymmetries. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # forward counter
        fwd = self._get_asym_fwd(d) # input: 1+ 1-
        
        # backward counter 
        bck = self._get_asym_bck(d) # input: 2+ 2-

        # exit
        return [fwd, bck]  
        
    # ======================================================================= #
    def _get_asym_fwd(self, d, freq=None, options=''):
        """
            Find the asymmetry of forward counter using the asymmetries. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # get the relevant counters
        F = np.copy(d[0])
        B = np.copy(d[1])
        
        if '1' in self.mode: 
            return self._correct_baseline_simple(freq, F, B, options)
        elif '2' in self.mode:
            return self._get_asym_simple(F, B)    
        
    # ======================================================================= #
    def _get_asym_hel(self, d):
        """
            Find the asymmetry of each helicity. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # positive helicity calc
        pos = self._get_asym_pos(d)
        
        # negative helicity calc
        neg = self._get_asym_neg(d)

        # exit
        return [pos, neg]
                
    # ======================================================================= #
    def _get_asym_comb(self, d, freq=None, options=''):
        """
        Find the combined asymmetry for slr runs. Elegant 4-counter method.
        d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """

        # get counter identifies
        Fp, Fn, Bp, Bn = d
        
        # choose calculation method
        if '1' in self.mode: 
            return self._correct_baseline_combined(freq, Fp, Fn, Bp, Bn, options)
        elif '2' in self.mode:
            return self._get_asym_4counter(Fp, Fn, Bp, Bn)
        
    # ======================================================================= #
    def _get_asym_4counter(self, Fp, Fn, Bp, Bn):
        """
        Find the combined asymmetry for slr runs. Elegant 4-counter method.
        """

        # pre-calcs
        r_denom = Fp*Bn
        r_denom[r_denom==0] = np.nan
        r = np.sqrt((Bp*Fn/r_denom))
        r[r==-1] = np.nan
    
        # combined asymmetry
        asym_comb = (r-1)/(r+1)
        
        # check for div by zero
        Fp[Fp==0] = np.nan                  
        Bp[Bp==0] = np.nan
        Fn[Fn==0] = np.nan
        Bn[Bn==0] = np.nan
        
        # error in combined asymmetry
        asym_comb_err = r*np.sqrt(1/Bp + 1/Fp + 1/Bn + 1/Fn)/np.square(r+1)
        
        # replace nan with zero 
        asym_comb[np.isnan(asym_comb)] = 0.
        asym_comb_err[np.isnan(asym_comb_err)] = 0.
        
        return [asym_comb, asym_comb_err]

    # ======================================================================= #
    def _get_asym_neg(self, d, freq=None, options=''):
        """
            Find the negative helicity asymmetry. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # get the relevant counters
        F = np.copy(d[1])
        B = np.copy(d[3])
        
        if '1' in self.mode: 
            return self._correct_baseline_simple(freq, F, B, options)
        elif '2' in self.mode:
            return self._get_asym_simple(F, B)    
        
    # ======================================================================= #
    def _get_asym_pos(self, d, freq=None, options=''):
        """
            Find the positive helicity asymmetry. 
            d = list: [1+ 1- 2+ 2-], where 1 = F/R and 2 = B/L
        """
        
        # get the relevant counters
        F = np.copy(d[0])
        B = np.copy(d[2])
        
        if '1' in self.mode: 
            return self._correct_baseline_simple(freq, F, B, options)
        elif '2' in self.mode:
            return self._get_asym_simple(F, B)    
            
    # ======================================================================= #
    def _get_asym_simple(self, F, B):
        """
            Do the simple asymmetry calculation: F-B / F+B
        """
        
        # pre-calcs
        denom = F+B
        
        # check for div by zero
        denom[denom==0] = np.nan          
        
        # asymmetries
        asym = (F-B)/denom
                    
        # errors 
        # https://www.wolframalpha.com/input/?i=%E2%88%9A(F*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+F)%5E2+%2B+B*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+B)%5E2)
        asym_err = 2*np.sqrt(F*B/np.power(denom, 3))
        
        # remove nan            
        asym[np.isnan(asym)] = 0.
        asym_err[np.isnan(asym_err)] = 0.
         
        return [asym, asym_err]
    
    # ======================================================================= #
    def _get_baseline_slope(self, freq, scan, dscan, baseline_bins):
        """
            Flatten the baseline of a single scan by fitting it to a linear line 
            and subtracting the slope (then adding back the line mean). 
            
            freq: array of frequencies
            scan: array of values to fix
            dscan: array of errors
            baseline_bins: int, number of bins on either end to use in the 
                           baseline fitting. Should exclude any resonance peaks. 
        """
        
        # simple return
        if baseline_bins <= 0:
            return scan
        
        # get indices to crop 
        bins = np.arange(len(freq))
        
        # sort freq and scan by freq
        idx = np.argsort(freq)
        freq = np.array(freq)[idx]
        scan = np.array(scan)[idx]
        dscan = np.array(dscan)[idx]
        
        # crop out center
        low = baseline_bins
        high = len(freq) - baseline_bins
        
        freq2 = np.concatenate((freq[:low], freq[high:]))
        scan2 = np.concatenate((scan[:low], scan[high:]))
        dscan2 = np.concatenate((dscan[:low], dscan[high:]))
        
        # remove nan and 0
        idx = (~np.isnan(scan2)) & (scan2 != 0) & (dscan2 != 0)
        freq2 = freq2[idx]
        scan2 = scan2[idx]
        dscan2 = dscan2[idx]
        
        if not scan2.size:
            return 0
        
        # estimate starting baseline parameters
        s_start = np.mean(scan[:low])
        s_end = np.mean(scan[high:])
        f_start = np.mean(freq[:low])
        f_end = np.mean(freq[high:])

        slope = (s_end - s_start)/(f_end - f_start)
        offset = s_start - slope * f_start

        # fit
        fitfn = lambda x, a, b: a*x + b
        par, cov = curve_fit(fitfn, freq2, scan2, sigma=dscan2, 
                             absolute_sigma=True,
                             p0=[slope, offset])
        std = np.diag(cov)**0.5
        
        # baseline slope
        return par[0]
        
    # ======================================================================= #
    def _get_1f_mean_scans(self, d, freq):
        """
            Average counts in each frequency bin over 1f scans. 
        """
        
        # concat scans
        try:
            for i in range(len(d)):
                d[i] = np.concatenate(d[i])
            freq = np.concatenate(freq)
        except ValueError:
            pass        
        
        # make data frame
        df = pd.DataFrame({i:d[i] for i in range(len(d))})
        df['x'] = freq
        
        # combine scans: values with same frequency 
        df = df.groupby('x').apply(lambda i: i[i>0].mean())
        df.drop('x', axis='columns', inplace=True)
        x = df.index.values
        d = df.values.T
        
        return (x, d)
    
    # ======================================================================= #
    def _get_1f_sum_scans(self, d, freq):
        """
            Sum counts in each frequency bin over 1f scans, excluding zero. 
        """
        
        # concat scans
        try:
            for i in range(len(d)):
                d[i] = np.concatenate(d[i])
            freq = np.concatenate(freq)
        except ValueError:
            pass
        
        # make data frame
        df = pd.DataFrame({i:d[i] for i in range(len(d))})
        df['x'] = freq
        
        # combine scans: values with same frequency 
        df = df.groupby('x').sum()
        x = df.index.values
        d = df.values.T
        
        return (x, d)
            
    # ======================================================================= #
    def _get_2e_asym(self):
        """
            Get asymmetries for 2e random-frequency scan. 
            Based on bnmr_2e.cpp by rmlm (Oct 4, 2017).
        """
        
        # get needed PPG parameters for splitting 1D histos into 2D histos
        try:        
            # get frequency vector
            freq = np.arange(self._get_ppg('freq_start'), \
                        self._get_ppg('freq_stop')+self._get_ppg('freq_incr'), \
                        self._get_ppg('freq_incr'))
                             
            # number of dwelltimes per frequency bin 
            ndwell = 2*int(self._get_ppg('ndwell_per_f'))-1
            
            # number of RF on delays for the start bin. 
            start_bin = int(self._get_ppg('rf_on_delay'))
            
            # get bin centers in ms
            time = self._get_ppg('rf_on_ms')*(np.arange(ndwell)+0.5-ndwell/2.)
            
            # get the time and index of the middle time 
            mid_time_i = int(np.floor(ndwell/2.))
            mid_time = time[mid_time_i]
        
            # beam off time after pulse in ms
            beam_off = int(self._get_ppg('beam_off_ms'))
        
        except KeyError:
            raise RuntimeError("Not all dictionary variables read out to "+\
                               "proper locations")
            
        # setup output
        out = mdict()
        out['freq'] = freq
        out['time'] = time
            
        # get data
        data = np.array(self._get_area_data()) # [[fp], [fm], [bp], [bm]]
        
        # discared initial bad bins, and beam-off trailing bins
        data = data[:, start_bin:len(freq)*ndwell+start_bin]
        
        # split data by frequency
        nsplit = len(data[0])/ndwell
        
        fp = np.array(np.split(data[0], nsplit))
        fm = np.array(np.split(data[1], nsplit))
        bp = np.array(np.split(data[2], nsplit))
        bm = np.array(np.split(data[3], nsplit))
        
        # get raw asymmetries 
        asym_p_2cntr = (bp-fp)/(bp+fp)      # two counter
        asym_m_2cntr = (bm-fm)/(bm+fm)      # two counter
        r = np.sqrt(bp*fm/(bm*fp))
        asym_4cntr = (r-1)/(r+1)            # four counter
        
        # get raw asymmetry errors
        asym_p_2cntr_err = 2*np.sqrt(bp*fp)/((bp+fp)**1.5)
        asym_m_2cntr_err = 2*np.sqrt(bm*fm)/((bm+fm)**1.5)
        asym_4cntr_err = r*np.sqrt(1./bp+1./bm+1./fp+1./fm)/((r+1)**2)

        # save to output
        out['raw_p'] = np.array([asym_p_2cntr, asym_p_2cntr_err])
        out['raw_n'] = np.array([asym_m_2cntr, asym_m_2cntr_err])
        out['raw_c'] = np.array([asym_4cntr, asym_4cntr_err])

        # wrap asymmetry arrays into one for calculations [p, m, 4]
        # indexing is now [pm4][freq][time bin]
        asym     = np.array([asym_p_2cntr,    asym_m_2cntr,    asym_4cntr])
        asym_err = np.array([asym_p_2cntr_err, asym_m_2cntr_err, asym_4cntr_err])

        # compute differenced asymmetries via slopes from weighted least squares 
        # minimization.
        if ndwell >= 5:
            
            # calculate needed components element-wise
            w = asym_err**-2
            x = time
            y = asym
            
            wx = w*x
            wy = w*y
            wxy = w*x*y
            wxx = w*x*x
        
            # sum over values i < mid_time_i within each asymmetry and frequency 
            # Indexing: [pm4][freq]
            w_pre   = np.sum(w  [:, :, :mid_time_i], 2)    
            wx_pre  = np.sum(wx [:, :, :mid_time_i], 2)
            wy_pre  = np.sum(wy [:, :, :mid_time_i], 2)
            wxy_pre = np.sum(wxy[:, :, :mid_time_i], 2)
            wxx_pre = np.sum(wxx[:, :, :mid_time_i], 2)
            
            # sum over values i > mid_time_i
            w_pst   = np.sum(w  [:, :, -mid_time_i:], 2)
            wx_pst  = np.sum(wx [:, :, -mid_time_i:], 2)
            wy_pst  = np.sum(wy [:, :, -mid_time_i:], 2)
            wxy_pst = np.sum(wxy[:, :, -mid_time_i:], 2)
            wxx_pst = np.sum(wxx[:, :, -mid_time_i:], 2)
            
            # calculate slopes and intercepts
            delta_pre = w_pre*wxx_pre - wx_pre**2
            delta_pst = w_pst*wxx_pst - wx_pst**2
            
            sl_pre = (w_pre*wxy_pre - wx_pre*wy_pre)/delta_pre
            sl_pst = (w_pst*wxy_pst - wx_pst*wy_pst)/delta_pst
            dsl_pre = np.sqrt(w_pre/delta_pre)
            dsl_pst = np.sqrt(w_pst/delta_pst)
            
            intr_pre = (wy_pre*wxx_pre - wx_pre*wxy_pre)/delta_pre
            intr_pst = (wy_pst*wxx_pst - wx_pst*wxy_pst)/delta_pst
            dintr_pre = np.sqrt(wxx_pre/delta_pre)
            dintr_pst = np.sqrt(wxx_pst/delta_pst)
            
            # extrapolate to middle time bin
            asym_slopes = intr_pst-intr_pre+(sl_pst-sl_pre)*mid_time
            asym_slopes_err = np.sqrt(dintr_pre**2 + dintr_pst**2 + \
                                      (dsl_pre**2 + dsl_pst**2) * mid_time**2)
            
            # save to output        
            out['sl_p'] = np.array([asym_slopes[0], asym_slopes_err[0]])
            out['sl_n'] = np.array([asym_slopes[1], asym_slopes_err[1]])
            out['sl_c'] = np.array([asym_slopes[2], asym_slopes_err[2]])
        
        # calculate asymmetry using differences
        asym_diff = asym[:, :, mid_time_i+1] - asym[:, :, mid_time_i-1]
        asym_diff_err = np.sqrt(asym_err[:, :, mid_time_i+1]**2+\
                                asym_err[:, :, mid_time_i-1]**2)
        
        # save to output
        out['dif_p'] = np.array([asym_diff[0], asym_diff_err[0]])
        out['dif_n'] = np.array([asym_diff[1], asym_diff_err[1]])
        out['dif_c'] = np.array([asym_diff[2], asym_diff_err[2]])   
            
        return out

    # ======================================================================= #
    def _get_ppg(self, name):
        """Get ppg parameter mean value"""
        return self.ppg[name].mean
    
    # ======================================================================= #
    def _get_xhist(self):
        """Get histogram data for x axis."""
        
        # histogram name
        if self.mode == '1f':
            xlabel = 'Frequency'
        elif self.mode == '1x':
            xlabel = 'Frequency'
        elif self.mode == '1w':
            xlabel = 'x parameter'
        elif self.mode == '1n':
            for xlabel in self.hist.keys():
                if 'cell' in xlabel.lower():    
                    break
        elif self.mode == '1e':
            xlabel = 'Magnet mA'
        elif self.mode == '1c':
            xlabel = 'Camp'
        elif self.mode == '1d':
            xlabel = 'Laser'
        
        if 'Custom EPICS scan' in self.hist.keys():
            xlabel = 'Custom EPICS scan'
        
        # get data
        return self.hist[xlabel].data
            
    # ======================================================================= #
    def _kill_bins(self, d, ranges):
        """
            Set counter values to zero based on user-input ranges
            
            d: list of histogram counters
            ranges: string of indices or ranges of indices (ex: 1-10, which is 
                    inclusive) which are used to zero bins and remove them from
                    the final asymmetry calculation
        """

        bin_ranges = []
        for b in ranges:
            if not '-' in b:
                bin_ranges.append(int(b))
            else:
                one = int(b.split('-')[0])
                two = int(b.split('-')[1])
                bin_ranges.extend(np.arange(one, two+1))
        
        # trivial exit
        if len(bin_ranges) == 0:
            return d
        
        # kill bins
        bin_ranges = np.array(bin_ranges)
        for i in range(len(d)):

            # get good bin range                
            idx = (bin_ranges>=0)*(bin_ranges<len(d[i]))

            # kill
            d[i][bin_ranges[idx]] = 0.
            
        return d
        
    # ======================================================================= #
    def _parse_1f_baseline_options(self, options):
        """
            Parse the options to get the proper flags and functions
        """
        
        # defaults
        scan_comb_fn = self._get_1f_sum_scans
        baseline_bins = 0
        omit_incomplete_scan = False
        flatten_final_asym = False
        split_scan = False
        
        # parse input options
        if options:
            
            # split and strip         
            options = options.split(':')
            options = list(map(str.strip, options))
            options = [opt for opt in options if opt]
            
            # check baseline correction bins
            for opt in options:
                try:
                    baseline_bins = int(opt)
                except ValueError:
                    pass
                else:
                    del options[options.index(opt)]
                    break
                
            # check flags
            omit_incomplete_scan = 'omit' in options
            flatten_final_asym = 'overcorrect' in options
            
            # get scan combination function
            if 'scan_raw' in options:
                scan_comb_fn = lambda d, freq : (freq, d)
                split_scan = True 
            elif 'scan_mean' in options:
                scan_comb_fn = self._get_1f_mean_scans 
            elif 'scan_sum' in options: 
                scan_comb_fn = self._get_1f_sum_scans 
                
            # check input
            if flatten_final_asym and not baseline_bins:
                raise RuntimeError("If overcorrection specified, must "+\
                                   "include number of bins to estimate "+\
                                   "baseline corrction")
            
            # check for unused options
            for opt in ('omit', 'overcorrect', 'scan_mean', 'scan_sum', 'scan_raw'):
                if opt in options:
                    del options[options.index(opt)]
            if options:
                print('%d.%d: Bad scan_repair_options: %s' % \
                        (self.year, self.run, ', '.join(options)))
        
        return (scan_comb_fn, 
                baseline_bins, 
                omit_incomplete_scan, 
                split_scan,
                flatten_final_asym)
    
    # ======================================================================= #
    def _rebin(self, xdx, rebin):
        """
            Rebin array x with weights 1/dx**2 by factor rebin.
            
            Inputs: 
                xdx = [x, dx]
                rebin = int
            Returns [x, dx] after rebinning. 
        """

        x = xdx[0]
        dx = xdx[1]
        rebin = int(rebin)
        
        # easy end condition
        if rebin <= 1:
            return (x, dx)
        
        # Rebin Discard unused bins
        lenx = len(x)
        x_rebin = []
        dx_rebin = []
        
        # avoid dividing by zero
        dx[dx==0] = np.inf
        
        # weighted mean
        for i in np.arange(0, lenx, rebin):
            w = 1./dx[i:i+rebin]**2
            wsum = np.sum(w)
            
            if wsum == 0:
                x_rebin.append(np.mean(x[i:i+rebin]))
                dx_rebin.append(np.std(x[i:i+rebin]))
            else:
                x_rebin.append(np.sum(x[i:i+rebin]*w)/wsum)
                dx_rebin.append(1./wsum**0.5)
                
        return np.array([x_rebin, dx_rebin])
                 
    # ======================================================================= #
    def _split_scan(self, freq, scan, omit_incomplete_scan=False):
        """
            Split an array into multiple scans by counting the number of unique 
            frequencies scanned. 
            
            freq: array of frequencies
            scan: array of asymmetry, counters, or other. 
            omit_incomplete: if true, exclude last incomplete scan
            
            return (bsplit, fsplit, ssplit) where
            
            fsplit and ssplit are lists of arrays with each entry corresponding 
            to a scan
            bsplit is the bin indices for plotting consecutive scans
        """

        # check type
        freq = np.asarray(freq)
        scan = np.asarray(scan)
        
        # make bins 
        bins = np.arange(len(freq))

        # chop off the last incomplete scan
        n_pts_per_scan = len(np.unique(freq))
        n_total = len(scan)
        n_full = n_total - n_total % n_pts_per_scan
        
        bins_complete = bins[:n_full]
        bins_incomplete = bins[n_full:]
        
        freq_complete = freq[:n_full]
        freq_incomplete = freq[n_full:]
        
        scan_complete = scan[:n_full]
        scan_incomplete = scan[n_full:]
        
        # split scan
        bins_split = list(bins_complete.reshape(-1, n_pts_per_scan))
        freq_split = list(freq_complete.reshape(-1, n_pts_per_scan))
        scan_split = list(scan_complete.reshape(-1, n_pts_per_scan))
        
        # add the incomplete scan
        if not omit_incomplete_scan:
            bins_split.append(bins_incomplete)
            freq_split.append(freq_incomplete)
            scan_split.append(scan_incomplete)

        return (bins_split, freq_split, scan_split)
    
    # ======================================================================= #
    def asym(self, option="", omit="", rebin=1, hist_select='', nbm=False, 
             deadtime=0, scan_repair_options=''):
        """Calculate and return the asymmetry for various run types. 
           
        usage: asym(option="", omit="", rebin=1, hist_select='', nbm=False, 
                    deadtime=0, scan_repair_options='')
            
        Inputs:
            option:             see below for details
            omit:               mode 1 bins to omit if space seperated string in 
                                    options is not feasible. See options 
                                    description below.
            rebin:              Weighted average over 'rebin' bins to 
                                    reduce array length by a factor of rebin. 
            hist_select:        string to specify which histograms get combined 
                                    into making the asymmetry calculation. 
                                    Deliminate with [, ] or [;]. Histogram names 
                                    cannot therefore contain either of these 
                                    characters.
            nbm:                if True, use neutral beams in calculations
            deadtime:           detector deadtime used to correct counter values 
                                (s)
            scan_repair_options:string with format "%d:%s:%s"
            
                                dictates treatment options for scans. All values
                                are optional and the order is irrelevant. 
            
                                possible ":"-deliminated values: 
                                    
                                    int:    use this many bins on either end of 
                                            each scan to estimate the baseline 
                                            slope on a scan-by-scan basis. Apply
                                            baseline slope correction. 
                                            default: don't correct the baseline
                                    
                                    'omit': add this optional keyword to exclude 
                                            the last scan in the series, if 
                                            incomplete
                                            default: include all scans
                                            
                                    'overcorrect':add this optional keyword to 
                                            include an overcorrection to the 
                                            baseline slopes in order to ensure 
                                            that the final scan-combined 
                                            asymmetry has a flat baseline
                                            default: flatten on a scan-by-scan 
                                                     basis
                                            
                                    'scan_sum' or 'scan_mean': dictate how 
                                            scans are combined. Functions are 
                                            applied to raw counts, not asym. 
                                            Default: scan_sum
                                            
        Asymmetry calculation outline (with default detectors) ---------------
        
            Split helicity      (NMR): (F-B)/(F+B) for each
            Combined helicity   (NMR): (r-1)/(r+1)
                where r = sqrt([(B+)(F-)]/[(F+)(B-)])
            Split counter       (NMR): (+ - -)/(+ + -) for each F, B
            
            
            
            Split helicity      (NQR): (R-L)/(R+L) for each
            Combined helicity   (NQR): (r-1)/(r+1)
                where r = sqrt([(L+)(R-)]/[(R+)(L-)])
            Split counter       (NMR): (+ - -)/(+ + -) for each R, L
            
            Alpha diffusion     (NQR) sum(AL0)/sum(L+R)
            Alpha tagged        (NQR) same as NQR, but using the tagged counters
            
        Histogram Selection ---------------------------------------------------
        
            If we wished to do a simple asymmetry calculation in the form of 
                                    
                                    (F-B)/(F+B)
            
            for each helicity, then 
                                       |--|  |--|   paired counter location
                        hist_select = 'F+, F-, B+, B-'
                                        |-----|       paired helicities
                                           |-----|
            
            for alpha diffusion calculations append the two alpha counters
            
                hist_select = 'R+, R-, L+, L-, A+, A-
            
            for alpha tagged calculations do the following
            
                hist_select = 'R+, R-, L+, L-, TR+, TR-, TL+, TL-, nTR+, nTR-, nTL+, nTL-'
                    
                where TR is the right counter tagged (coincident) with alphas, 
                      TL is the left  counter tagged with alphas, 
                     nTR is the right counter tagged with !alphas (absence of), 
                     nLR is the right counter tagged with !alphas, 
                                          
        Status of Data Corrections --------------------------------------------
            MODE 2 (TD): 
                Removes prebeam bins. 
                Provides the option of deadtime correction. Set to zero to disable.
                Rebinning: 
                    returned time is average time over rebin range
                    returned asym is weighted mean
                
            MODE 1 (TI): 
                Allows manual removal of unwanted bins. 
                Provides the option of deadtime correction. Set to zero to disable.
                Baseline correction:
                    Fit the baseline on a scan-by-scan basis with a linear line 
                    and subtract from the data to flatten. Add back the 
                    baseline average pre-flatten to keep baseline value 
                    approximately the same. Requires removal of incomplete scans
                Remove incomplete scans. 
                Scan Combination:
                    Multiscans are considered as a single scan with long 
                    integration time. Histogram bins are summed according to 
                    their frequency bin, errors are Poissonian.
                    
                    In the case of split counter asymmetries, we take the mean
                    of the non-zero counts in each bin, with errors treated still
                    as Possionian.
             
            2E: 
                Prebeam bin removal. 
                Postbeam bin removal. Assumes beamoff time is 0. 
                Splits saved 1D histograms into 2D.
                Deadtime corrections are not yet available for this mode. 
                
                Asymmetry calculations: 
                    raw: calculated through differences method (as described in 
                        the asymmetry calculation outline)
                    dif: let 0 be the index of the centermost scan in time. dif 
                        asymmetries are then calculated via raw[i+1]-raw[i-1], 
                        where "raw" is as calculated in the above line, for each 
                        of the three types: +, -, combined 
                    sl: take a weighted least squares fit to the two bins prior 
                        and the two bins after the center bin (in time). For 
                        each find the value of the asymmetry at the center time 
                        position. Take the difference: post-prior
                    
        Option List
        
            MODE 2 DESCRIPTIONS -----------------------------------------------
            
            "":     dictionary of 2D numpy arrays keyed by 
                        {"p", "n", "c", "time_s"} for each helicity and combination 
                        (val, err). Default return state for unrecognized options
            "h":    dictionary 2D numpy arrays keyed by {"p", "n", "time_s"} for 
                        each helicity (val, err).
            "p":    2D np array of up helicity state [time_s, val, err].
            "n":    2D np array of down helicity state [time_s, val, err].
            "f":    2D np array of forward counter [time_s, val, err].
            "b":    2D np array of backward counter [time_s, val, err].
            "l":    2D np array of left counter [time_s, val, err].
            "r":    2D np array of right counter [time_s, val, err].
            "c":    2D np array of combined asymmetry [time_s, val, err].
            "ad":   2D np array of alpha diffusion ratio [time_s, val, err].
            "at":   dictionary of alpha tagged asymmetries key:[val, err]. 
                    Keys:
                        
                        'time_s'               : 1D array of times in seconds   
                        'p_wiA', 'n_wiA', 'c_wiA': coincident with alpha
                        'p_noA', 'n_noA', 'c_noA': coincident with no alpha
                        'p_noT', 'n_noT', 'c_noT': untagged
                        
                where p, n, c refer to pos helicity, neg helicity, combined 
                helicity respectively. Only in 2h mode. 
                        
            
            MODE 1 DESCRIPTIONS -----------------------------------------------
            
                all options can include a space deliminated list of bins or 
                ranges of bins which will be omitted. ex: "raw 1 2 5-20 3"
            
            "":     dictionary of 2D numpy arrays keyed by {p, n, c, freq} for each 
                        helicity and combination [val, err]. Default return state 
                        for unrecognized options.
            "r":    Dictionary of 2D numpy arrays keyed by {p, n} for each 
                        helicity (val, err), but listed by bin, not combined by 
                        frequency. 
            "rs":   Dictionary of 2D numpy arrays keyed by {p, n} for each 
                        helicity (val, err), but listed by bin, not combined by 
                        frequency. Split into scans.
            "h":    get unshifted +/- helicity scan-combined asymmetries as a 
                        dictionary {'p':(val, err), 'n':(val, err), 'freq'}
            "p":    get pos helicity states as tuple, combined by frequency 
                        (freq, val, err)
            "n":    similar to p but for negative helicity states
            "f":    similar to p but for forward counter
            "b":    similar to p but for backward counter
            "l":    similar to p but for left counter
            "r":    similar to p but for right counter
            "c":    get combined helicity states as tuple (freq, val, err)
            
                        
            2E DESCRIPTIONS ---------------------------------------------------
            
            "sc":   get slope combined helicity states as tuple (freq, val, err)
            "dc":   get difference combined helicity states as tuple (freq, val, err)
            "rc":   get raw combined helicity states as tuple (freq, time, val, err)
            
                If no options, returns a dictionary with the keys: 
             
            'dif_p':    [val, err][frequency] of pos. helicity asymmetry 
            'dif_n':    [ve][f] of negative helicity asymmetry
            'dif_c':    [ve][f] of combined helicity asymmetry
            
            'raw_p':    [ve][f][time] raw asymmetries of each time bin. Pos hel. 
            'raw_n':    [ve][f][t] negative helicity.
            'raw_c':    [ve][f][t] combined helicity
            
            'freq':     [f] frequency values
            'time':     [t] time bin values
                
            'sl_p':     [ve][f] pos. hel. of asymmetry calcuated through slopes 
                            of pre and post middle time bin. Slope method only 
                            for >= 5 time bins, corresponds to >= 3 RF on delays
            'sl_n':     [ve][f] negative helicity.
            'sl_c':     [ve][f] combined helicity.
        """
                                
        # check for additonal options (1F)
        if omit != '':
            further_options = list(map(str.strip, omit.split(' ')))
        else:
            further_options = list(map(str.strip, option.split(' ')[1:]))
        option = option.split(' ')[0].strip()
        
        # Option reduction
        option = option.lower()
        option = self.option.get(option, option)
        
        # get data
        d = self._get_area_data(nbm=nbm, hist_select=hist_select) # 1+ 2+ 1- 2-
                
        # get alpha diffusion data
        if self.mode == '2h':
            d_alpha = d[4:]
            d = d[:4]
            
        # SLR -----------------------------------------------------------------
        if self.mode in ("20", '2h', "00"):
            
            # get the number of prebeam bins
            try:
                n_prebeam = int(self._get_ppg('prebeam'))
            
            # some old runs don't log prebeam values
            except KeyError:
                pass
            
            # remove negative count values, delete prebeam entries
            else:
                for i in range(len(d)):
                    d[i][d[i]<0] = 0.
                    d[i] = np.delete(d[i], np.arange(n_prebeam))
                    
                # check and fix 2018-2020 NQR prebeam error
                d = self._fix_prebeam_offbyone(d)
                
                if self.mode == '2h':
                    d_alpha = self._fix_prebeam_offbyone(d_alpha)
                                                    
            # deadtime correction
            d = self._correct_deadtime(d, deadtime)
            
            # delete alpha prebeam bins
            if self.mode == '2h':    
                for i in range(len(d_alpha)):
                    d_alpha[i][d_alpha[i]<0] = 0.
                    d_alpha[i] = np.delete(d_alpha[i], np.arange(n_prebeam))
                
            # get helicity data
            if option not in ('combined', 'forward_counter', 'backward_counter'):
                h = np.array(self._get_asym_hel(d))
            elif option in ('forward_counter', 'backward_counter'):
                h = np.array(self._get_asym_counter(d))
                
            # time
            time = self.get_time(n = len(d[0]), rebin=rebin)
            
            # mode switching
            if option in ('positive', 'forward_counter'): # ---------------------------------------
                return np.vstack([time, self._rebin(h[0], rebin)])
                
            elif option in ('negative', 'backward_counter'): # -------------------------------------
                return np.vstack([time, self._rebin(h[1], rebin)])
            
            elif option == 'helicity': # -------------------------------------
                out = mdict()
                out['p'] = self._rebin(h[0], rebin)
                out['n'] = self._rebin(h[1], rebin)
                out['time_s'] = time
                return out
                
            elif option == 'counter': # -------------------------------------
                out = mdict()
                
                if self.area.upper() == 'BNMR':
                    out['f'] = self._rebin(h[0], rebin)
                    out['b'] = self._rebin(h[1], rebin)
                elif self.area.upper() == 'BNQR':
                    out['r'] = self._rebin(h[0], rebin)
                    out['l'] = self._rebin(h[1], rebin)
                    
                out['time_s'] = time
                return out
                
            elif option == 'combined': # -------------------------------------
                c = np.array(self._get_asym_comb(d))
                return np.vstack([time, self._rebin(c, rebin)])
                
            elif option == 'alpha_diffusion': # ------------------------------
                try:
                    asym = self._get_asym_alpha(d_alpha, d)
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise InputError('Run is not in 2h mode.')
                return np.vstack([time, self._rebin(asym, rebin)])
            
            elif option == 'alpha_tagged': # ---------------------------------
                try:
                    asym = self._get_asym_alpha_tag(d_alpha, d)  
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise InputError('Run is not in 2h mode.')
                    else:
                        raise err
                
                out = mdict()
                out['p_wiA'] = self._rebin(asym[0][0], rebin)
                out['n_wiA'] = self._rebin(asym[0][1], rebin)
                out['p_noA'] = self._rebin(asym[1][0], rebin)
                out['n_noA'] = self._rebin(asym[1][1], rebin)
                out['p_noT'] = self._rebin(asym[2][0], rebin)
                out['n_noT'] = self._rebin(asym[2][1], rebin)
                out['c_wiA'] = self._rebin(asym[3], rebin)
                out['c_noA'] = self._rebin(asym[4], rebin)
                out['c_noT'] = self._rebin(asym[5], rebin)
                out['time_s'] = time
                
                return out
            
            else:
                h = np.array(self._get_asym_hel(d))
                c = np.array(self._get_asym_comb(d))
                ctr = np.array(self._get_asym_counter(d))
                
                out = mdict()
                out['p'] = self._rebin(h[0], rebin)
                out['n'] = self._rebin(h[1], rebin)
                
                if self.area.upper() == 'BNMR':
                    out['f'] = self._rebin(h[0], rebin)
                    out['b'] = self._rebin(h[1], rebin)
                elif self.area.upper() == 'BNQR':
                    out['r'] = self._rebin(h[0], rebin)
                    out['l'] = self._rebin(h[1], rebin)
                
                out['c'] = self._rebin(c, rebin)  
                out['time_s'] = time
                return out
        
        # 1F ------------------------------------------------------------------
        elif self.mode in self.mode1_dict.keys(): # ('1f', '1n', '1w', '1e', '1c', '1d', '1x')
            
            # get xaxis label and data key
            xlab = self.mode1_dict[self.mode]
            if 'Custom EPICS scan' in self.hist.keys():
                xlab = 'custom'
            
            # deadtime correction
            d = self._correct_deadtime(d, deadtime)
            
            # set bins to zero based on user input (exclude from final calculation)
            d = self._kill_bins(d, ranges=further_options)
            
            # get frequency
            freq = self._get_xhist()
            
            # get raw scans
            if 'raw' in option:
                
                out = mdict()
                scan_repair_options += ':scan_raw' # force no scan combination
                freq_p, p = self._get_asym_pos(d, freq=freq, options=scan_repair_options)
                freq_n, n = self._get_asym_neg(d, freq=freq, options=scan_repair_options)
                
                # feather the output to insert zeros in the place of opposite hel scans
                if option == 'raw':
                    assert len(freq_p) == len(freq_n)
                    out['p'] = np.array([np.concatenate(p[0]), np.concatenate(p[1])])
                    out['n'] = np.array([np.concatenate(n[0]), np.concatenate(n[1])])
                    out[xlab] = np.array(np.concatenate(freq_p))
                
                # simply report the scans
                elif option == 'raw_split_scan':
                    
                    # remove empty scans
                    p_out = []
                    n_out = []
                    fp_out = []
                    fn_out = []
                    
                    for pi, fi in zip(p, freq_p):
                        if sum(pi[0]) > 0:
                            p_out.append(pi)
                            fp_out.append(fi)
                    
                    for ni, fi in zip(n, freq_n):
                        if sum(ni[0]) > 0:
                            n_out.append(ni)
                            fn_out.append(fi)
                    
                    out['p'] = np.array(p_out, dtype=object)
                    out['n'] = np.array(n_out, dtype=object)
                    out[xlab + '_p'] = np.array(fp_out, dtype=object)
                    out[xlab + '_n'] = np.array(fn_out, dtype=object)
                
                # bad input
                else:
                    raise InputError('%d.%d: bad input for asym calculation (%s)' % \
                                    (self.year, self.run, option))
            
                return out 
                
                              
            # calculate asymmetry
            asym = mdict()
            if option in ('helicity', 'positive', ''):
                asym[xlab], asym['p'] = self._get_asym_pos(d, 
                                               options=scan_repair_options, 
                                               freq=freq)
            if option in ('helicity', 'negative', ''):
                asym[xlab], asym['n'] = self._get_asym_neg(d, 
                                               options=scan_repair_options, 
                                               freq=freq)
            if option in ('counter', 'backward_counter', ''): 
                asym[xlab], asym['b'] = self._get_asym_bck(d, 
                                               options=scan_repair_options, 
                                               freq=freq)
            if option in ('counter', 'forward_counter', ''): 
                asym[xlab], asym['f'] = self._get_asym_fwd(d, 
                                               options=scan_repair_options, 
                                               freq=freq)
            if option in ('combined', ''): 
                asym[xlab], asym['c'] = self._get_asym_comb(d, 
                                               options=scan_repair_options, 
                                               freq=freq)
            
            # rebin 
            if rebin > 1:
                for key in asym.keys():
                    
                    # rebin frequencies
                    if key == xlab: 
                        len_f = len(asym[key])
                        newf = (np.average(asym[key][i:i+rebin-1]) for i in range(0, len_f, rebin))
                        asym[key] = np.fromiter(newf, dtype=float, count=int(np.ceil(len_f/rebin)))
                    
                    # rebin asymmetries
                    else:
                        asym[key] = self._rebin(asym[key], rebin)
                                   
            # format output: NQR counters
            if self.area.upper() == 'BNQR' and 'f' in asym.keys():
                asym['r'] = asym['f']
                del asym['f']
        
            if self.area.upper() == 'BNQR' and 'b' in asym.keys():
                asym['l'] = asym['b']
                del asym['b']
            
            # format output: no dict needed if not enough keys
            if len(asym.keys()) == 2:
                keys = list(asym.keys())
                del keys[keys.index(xlab)]
                asym = np.vstack([asym[xlab], asym[keys[0]]])
                
            return asym
            
        # 2E ------------------------------------------------------------------
        elif self.mode in ('2e', ):
            adict = self._get_2e_asym()
            
            if option == 'slope_combined':  
                return (adict['freq'], *adict['sl_c'])
            elif option == 'difference_combined':  
                return (adict['freq'], *adict['dif_c'])
            elif option == 'raw_combined':  
                return (adict['freq'], adict['time'], *adict['raw_c'])
            else:
                return adict
        
        # unknown entry -------------------------------------------------------
        else:
            print("Unknown run type.")
            return

    # ======================================================================= #
    @property
    def beam_keV(self):     return self._beam_kev()
    
    # ======================================================================= #
    @property
    def beam_keV_err(self): return self._beam_kev(get_error=True)
    
    # ======================================================================= #
    def get_deadtime(self, dt=1e-9, c=1, return_minuit=False, fixed='c'):
        """
            Get detector deadtime in s (TD mode only)
            
            Based on bnmrfit physical script named bnmr_fdt.pcm written by Jay 
            and Zaher in June 2005
            
            dt:             deadtime initial parameter in s
            c:              negative helicity scaling factor
            return_minuit:  if true, return Minuit object, else return the 
                            unfixed parameters
            fixed:          if string fix that parameter, list fix those parameters
                            
            returns
                
                if return_minuit return Minuit object
                if one parameter fixed, return the other parameter
                if both parameters fixed, return the chi2 value
        """
        
        # check run mode
        if '2' not in self.mode:
            raise RuntimeError('Deadtimes only estimatable in time differentiated mode')
        
        # make chi2 function: compare the midpoint of the split helicity
        # to the total average value, which is somewhere in the middle
        def chi(dt_ns, c):
            
            # get split hel asym
            asym = self.asym('h', deadtime=dt_ns*1e-9)
            p, dp = asym['p']
            n, dn = asym['n']
            
            # midpoints
            midpts = 0.5*(p+c*n)
            dmidpts2 = 0.25*(dp**2 + (c*dn)**2)
            
            # weighted average midpoint
            avgmid = np.average(midpts, weights=1/dmidpts2)
            
            # get chi2
            return np.mean( ((midpts-avgmid)**2)/dmidpts2 )
        
        
        # search for best chi2
        m = Minuit(chi, dt_ns=dt*1e9, c=c)
        m.errordef = 1
        m.limits['dt_ns'] = (0, None)
        
        # fixing
        if 'c' in fixed:    m.fixed['c'] = True
        if 'dt' in fixed:   m.fixed['dt_ns'] = True
        
        # run minimization
        m.migrad()
        
        # check if valid 
        if not m.valid:
            print(m.fmin)
            print(m.params)
            raise MinimizationError("Minuit failed to converge to a valid minimum")
        
        # make output
        if return_minuit:   
            return m
        else:      
            output = []
            if not m.fixed['dt_ns']:
                output.append(m.values['dt_ns']*1e-9)
            if not m.fixed['c']:
                output.append(m.values['c'])
            
            # return
            len_out = len(output)
            if len_out == 0:    return m.fval           # all fixed: return chi2
            elif len_out == 1:  return output[0]
            else:               return np.array(output)
        
    # ======================================================================= #
    def get_time(self, n=0, rebin=1):
        """
            Get the time axis in mode 2 runs (bin centers)
            
            n = number of bins (ex: len(hist['B+'])
            rebin = how to average the time bins
        """
        
        # get n from ppg parameters
        if n <= 0:
            beam_on = self._get_ppg('beam_on')
            beam_off = self._get_ppg('beam_off')
            n = beam_on + beam_off
        
        # get time array    
        time = (np.arange(n)+0.5)*self._get_ppg('dwelltime')/1000
        
        # rebin time
        if rebin > 1:
            new_t_idx = np.arange(0, n, rebin)
            new_time = (np.average(time[i:i+rebin]) for i in new_t_idx)
            time = np.fromiter(new_time, dtype=float, count=len(new_t_idx))
            
        return time
        
    # ======================================================================= #
    @property
    def pulse_s(self):        
        """Get pulse duration in seconds, for pulsed measurements."""
        
        try:
            dwelltime = self._get_ppg('dwelltime')
        except KeyError:
            raise AttributeError("Missing ppg parameter: dwelltime") from None
        try:
            beam_on = self._get_ppg('beam_on')
        except KeyError:
            raise AttributeError("Missing ppg parameter: beam_on") from None
                    
        return dwelltime*beam_on/1000.
    
