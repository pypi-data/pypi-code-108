import os
import sys
import pandas as pd
import numpy as np
from docopt import docopt
from  multiprocessing import Pool
from comparedomains.domains import comp2domins_by_twtest, loadtads
import warnings
warnings.filterwarnings('ignore')