import sys
import traceback
from typing import Optional, Dict, List
from contextlib import contextmanager

@contextmanager
def standard_log(log_path:Optional[str]=None):
    import ROOT
    try:
        if log_path is not None:
            sys.stdout = open(log_path, 'w')
            ROOT.gSystem.RedirectOutput(log_path)
        yield sys.stdout
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        # recover stdout
        if log_path is not None:
            sys.stdout.close()
        sys.stdout = sys.__stdout__
        ROOT.gROOT.ProcessLine('gSystem->RedirectOutput(0);')