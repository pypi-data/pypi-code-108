import matplotlib
try:
    matplotlib.use('TkAgg')
except ImportError:
    pass

from .fitting.functions import lorentzian, bilorentzian, gaussian, quadlorentzian
from .fitting.functions import pulsed_exp, pulsed_strexp, pulsed_biexp
from .fitting.global_fitter import global_fitter
from .fitting.global_bdata_fitter import global_bdata_fitter
from .fitting.fit_bdata import fit_bdata
from .fitting.minuit import minuit
from .fitting.gen_init_par import gen_init_par
from .global_variables import __version__

import logging, os, sys, argparse, subprocess, requests, json, code
from logging.handlers import RotatingFileHandler
from textwrap import dedent
from pkg_resources import parse_version 
from tkinter import messagebox

__all__ = ['gui', 'fitting', 'backend', 'test']
__author__ = 'Derek Fujimoto'
logger_name = 'bfit'
icon_path = os.path.join(os.path.dirname(__file__), 'data', 'icon.gif')

__all__.extend(("lorentzian", 
                "bilorentzian", 
                "gaussian", 
                "quadlorentzian",
                "pulsed_exp",
                "pulsed_strexp",
                "pulsed_biexp",
                "global_fitter",
                "global_bdata_fitter",
                "fit_bdata",
                "minuit",
                "gen_init_par",
                ))

from bfit.gui.bfit import bfit

# RUN BFIT ================================================================== #
def main():
    
    # check if maxOS
    if sys.platform == 'darwin':
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

    # check if windows
    if sys.platform == 'win32':
        homedir = os.environ['HOMEPATH']
    else:
        homedir = os.environ['HOME']

    # command line switches ---------------------------------------------------
    parser = argparse.ArgumentParser(description=dedent("""\
        Run BNMR data viewer and fitter for online application."""), 
        formatter_class=argparse.RawTextHelpFormatter)
    
    # logging level
    parser.add_argument("-d", "--debug", 
                        help='Run in debug mode', 
                        dest='debug', 
                        action='store_true', 
                        default=False)
    
    # no gui mode
    parser.add_argument("-c", "--commandline", 
                        help='Run in command line mode', 
                        dest='commandline', 
                        action='store_true', 
                        default=False)

    # parse
    args = parser.parse_args()

    # Setup logging -----------------------------------------------------------
    logger = logging.getLogger(logger_name)

    # get log filename
    try:
        filename = os.path.join(homedir, '.bfit.log')
    except KeyError:
        filename = 'bfit.log'

    # make handler
    handler = RotatingFileHandler(filename, 
                                  mode='a', 
                                  maxBytes=500*1000, # 500 kB max
                                  backupCount=1)

    # get level and format for output string
    if args.debug:
        level = logging.DEBUG
        fmt = '%(asctime)s %(levelname)-8s %(module)s.%(funcName)s() [%(lineno)d] -- %(message)s'
    else:
        level = logging.INFO
        fmt = '%(asctime)s %(levelname)-8s %(module)s -- %(message)s'
    
    # set
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.setLevel(level)
    
    # testing
    testfn = None
    # ~ def testfn(self):
        # ~ self.fetch_files.run.set("40123, 40127")
        # ~ self.fetch_files.year.set(2012)
        # ~ self.fetch_files.get_data()
        # ~ self.fit_files.fit_function_title.set("QuadLorentz")
        # ~ self.fit_files.populate()
        # ~ self.notebook.select(2)
        # ~ self.fit_files.do_fit()
        # ~ import matplotlib.pyplot as plt
        # ~ plt.close('all')
        # ~ self.fit_files.do_add_param()
        
    # Check version (credit: https://github.com/alexmojaki/outdated) ----------
    try:
        latest_version = requests.get('https://pypi.python.org/pypi/bfit/json').text
        latest_version = json.loads(latest_version)['info']['version']
        latest_version2 = parse_version(latest_version)
        current_version = parse_version(str(__version__))
        if current_version < latest_version2: 
            testfn = lambda x: messagebox.showinfo("Please update", 
                                "Version %s available!" % latest_version)
    except Exception:
        pass
    
    # start bfit --------------------------------------------------------------
    b = bfit(testfn, args.commandline)
    if args.commandline:
        code.interact(local=locals())
        print('bfit object set to variable "b"')
    

    
        
