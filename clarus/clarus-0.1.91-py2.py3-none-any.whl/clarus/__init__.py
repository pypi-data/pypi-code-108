#Name: clarus.py
#Runtimes: Python,Python_Lambda
#Leave blank line below to mark end of header

from __future__ import print_function
from six.moves import urllib
import requests
import json
import os
import sys
import logging

from clarus.services import ccp, ccpqd, compliance, credit, dates, etd, frtb, hedge, load, margin, market, portfolio, profitloss, risk, sdr, simm, trade, util, xva, mifid, sef
from clarus.api_config import ApiConfig
from clarus.models import ApiResponse
from clarus.output_types import *
from clarus.api import request
from clarus.resource_util import read, write

def is_gui_call(event):
    if (event.get('__invocationsrc') == 'gui'):
        return True
    else:
        return False
    
def is_api_call(event):
    return not(is_gui_call(event))

def get_output_type(event):
    return event.get('__output')