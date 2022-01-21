import sys
import os
sys.path.insert(0, os.path.join(__file__, '..', '..'))

import nose

import io

from marlowe_ui import vpar_moliere

native1 = {'BPAR':{(1, 2):0.05}}
json1 = {'BPAR':[{'i':1, 'j':2, 'value':0.05}]}

def test_param_to_json1():
    ans = vpar_moliere.param_to_json(native1)
    nose.tools.eq_(ans, json1)

def test_param_from_json1():
    ans = vpar_moliere.param_from_json(json1)
    nose.tools.eq_(ans, native1)

native2 = {'BPAR':{
    (1, 2):0.05,
    (2, 3):0.07,
    (2, 2):-0.01
    }}
json2 = {'BPAR':[
    {'i':1, 'j':2, 'value':0.05},
    {'i':2, 'j':2, 'value':-0.01},
    {'i':2, 'j':3, 'value':0.07}
    ]}

def test_param_to_json2():
    ans = vpar_moliere.param_to_json(native2)
    # dict.items() does not confirm key order
    def sort_key(e):
        return e['i'], e['j']
    nose.tools.eq_(sorted(ans['BPAR'], key=sort_key),
            sorted(json2['BPAR'], key=sort_key))

def test_param_from_json2():
    ans = vpar_moliere.param_from_json(json2)
    nose.tools.eq_(ans, native2)
