from nose.tools import assert_equals, nottest
import sys
from os.path import join, dirname
sys.path.insert(0, join(dirname(__file__), '..'))
from annotations.impc_xml import load_xml

import os

current_dir = os.path.dirname(os.path.realpath(__file__))

test_xml_path = join(current_dir, 'Inpp5e-MBM-popavg.xml')

load_xml(test_xml_path)