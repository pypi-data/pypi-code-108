import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.tktool import validateentry

def test_int_initiate():
    c = validateentry.Int()

def test_double_initiate():
    c = validateentry.Double()

def test_intpositive_initiate():
    c = validateentry.IntPositive()

def test_doublepositive_initiate():
    c = validateentry.DoublePositive()

def test_vec2int_initiate():
    c = validateentry.Vec2Int()
