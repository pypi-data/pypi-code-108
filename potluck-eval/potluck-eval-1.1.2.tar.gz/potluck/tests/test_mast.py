"""
Tests of the mast module.

test_mast.py
"""

import ast

from .. import mast, mast_utils

TESTS = [
    (True, 1, '2', '2'),
    (False, 0, '2', '3'),
    (True, 1, 'x', '_a_'),
    (True, 1, '(x, y)', '(_a_, _b_)'),
    (False, 0, '(x, y)', '(_a_, _a_)'),
    (True, 1, '(x, x)', '(_a_, _a_)'),
    (True, 4, 'max(7,3)', '_x_'),
    (True, 1, 'max(7,3)', 'max(7,3)'),
    (False, 0, 'max(7,2)', 'max(7,3)'),
    (True, 1, 'max(7,3,5)', 'max(___args___)'),
    (False, 1, 'min(max(7,3),5)', 'max(___args___)'),
    (True, 2, 'min(max(7,3),5)', '_f_(___args___)'),
    (True, 1, 'min(max(7,3),5)', 'min(max(___maxargs___),___minargs___)'),
    (True, 1, 'max()', 'max(___args___)'),
    (True, 1, 'max(4)', 'max(4,___args___)'),
    (True, 1, 'max(4,5,6)', 'max(4,___args___)'),
    (True, 1, '"hello %s" % x', '_a_str_ % _b_'),
    (False, 0, 'y % x', '_a_str_ % _b_'),
    (False, 0, '7 % x', '_a_str_ % _b_'),
    (True, 1, '3', '_a_int_'),
    (True, 1, '3.4', '_a_float_'),
    (False, 0, '3', '_a_float_'),
    (False, 0, '3.4', '_a_int_'),
    (True, 1, 'True', '_a_bool_'),
    (True, 1, 'False', '_a_bool_'),
    (True, 1, 'None', 'None'),
    # node vard can bind statements or exprs based on context.
    (True, 7, 'print("hello"+str(3))', '_x_'), # 6 => 7 in Python 3
    (True, 1, 'print("hello"+str(3))', 'print(_x_)'),
    (True, 1, 'print(1)', 'print(_x_, ___args___)'),
    (False, 0, 'print(1)', 'print(_x_, _y_, ___args___)'),
    (False, 0, 'print(1, 2)', 'print(_x_)'),
    (True, 1, 'print(1, 2)', 'print(_x_, ___args___)'),
    (True, 1, 'print(1, 2)', 'print(_x_, _y_, ___args___)'),
    (True, 1, 'print(1, 2, 3)', 'print(_x_, ___args___)'),
    (True, 1, 'print(1, 2, 3)', 'print(_x_, _y_, ___args___)'),
    (True, 1,
     '''
def f(x):
    return 17
     ''',
     '''
def f(_a_):
    return _b_
     '''),
    (True, 1,
     '''
def f(x):
    return x
     ''',
     '''
def f(_a_):
    return _b_
     '''),
    (True, 1,
     '''
def f(x):
    return x
     ''',
     '''
def f(_a_):
    return _a_
     '''),
    (False, 0,
     '''
def f(x):
    return 17
     ''',
     '''
def f(_a_):
    return _a_
     '''),
    (True, 1,
     '''
def f(x):
    return 17
     ''',
     '''
def f(_x_):
    return _y_
     '''),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    return x
     ''',
     '''
def f(_x_,_y_):
    print('hi')
    return _x_
     '''),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    return x
     ''',
     '''
def _f_(_x_,_y_):
    print('hi')
    return _x_
     '''),
    (False, 0,
     '''
def f(x,y):
    print('hi')
    return y
     ''',
     '''
def f(_a_,_b_):
    print('hi')
    return _a_
     '''),
    (False, 0, 'x', 'y'),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    return y
     ''',
     '''
def _f_(_x_,_y_):
    ___
    return _y_
     '''),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    print('world')
    print('bye')
    return y
     ''',
     '''
def _f_(_x_,_y_):
    ___stmts___
    return _y_
     '''),
    (False, 0,
     '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
     ''',
     '''
def _f_(_x_,_y_):
    ___stmts___
    print(_z_)
    _y_ = _a_int_
    return _y_
     '''),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
     ''',
     '''
def _f_(_x_,_y_):
    ___stmts___
    print(_z_)
    _y_ = _a_int_
    ___more___
    return _y_
     '''),
    (True, 1,
     '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
     ''',
     '''
def _f_(_x_,_y_):
    ___stmts___
    print(_a_)
    _b_ = _c_
    ___more___
    return _d_
     '''),
    (False, 1,
     '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
     ''',
     '''
___stmts___
print(_a_)
_b_ = _c_
___more___
return _d_
     '''),
    (True, 1,
     '''
def eyes():
    eye1 = Layer()
    eye2 = Layer()
    face = Layer()
    face.add(eye)
    face.add(eye2)
    return face
     ''',
     '''
def eyes():
    ___
    _face_ = Layer()
    ___
    return _face_
     '''),
    (True, 1, '1 == 2', '2 == 1'),
    (True, 1, '1 <= 2', '2 >= 1'),
    (False, 0, '1 <= 2', '2 <= 1'),
    (False, 0, 'f() <= 2', '2 >= f()'),
    # Hmnm, is this the semantics we want for `and`?
    (True, 1, 'a and b and c', 'b and a and c'),
    (True, 1, '(a == b) == (b == c)', '(a == b) == (c == b)'),
    (True, 1, '(a and b) and c', 'a and (b and c)'),
    (True, 1, 'a and b', 'a and b'),
    (True, 1, 'g == "a" or g == "b" or g == "c"',
     '_g_ == _a_ or _g_ == _b_ or _c_ == _g_'),
    (True, 1, '''
x = 1
y = 2
''', '''
x = 1
y = 2
'''),
    (True, 1, '''
x = 1
y = 2
''', '''
___
y = 2
'''),
    (True, 1, '''
x = 1
if (a or b or c):
    return True
else:
    return False
     ''',
     '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
___
     '''),
    (True, 1, '''
if (a or b or c):
    return True
else:
    return False
     ''',
     '''
if _:
    return _a_bool_
else:
    return _b_bool_
     '''),
    (True, 1, '''
x = 1
if (a or b or c):
    return True
else:
    return False
     ''',
     '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
     '''),
    (False, 1, '''
def f():
    if (a or b or c):
        return True
    else:
        return False
     ''',
     '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
___
     '''),
    (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    else:
        return False
        ''', '''
if _:
    return _a_bool_
else:
    return _b_bool_
     '''),
    (False, 1, '''
def isValidGesture(gesture):
    print('blah')
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
        ''', '''
___
if _:
    return _a_bool_
return _b_bool_
     '''),

    (False, 1, '''
def isValidGesture(gesture):
    print('blah')
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
    ''', '''
if _:
    return _a_bool_
return _b_bool_
    '''),
    (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
     ''', '''
if _:
    return _a_bool_
return _b_bool_
     '''),
    (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        x = True
    x = False
    return x
     ''', '''
if _:
    _x_ = _a_bool_
_x_ = _b_bool_
     '''),
    (True, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
     ''', '''
def _(_):
    if _:
        return _a_bool_
    return _b_bool_
     '''),
    (True, 1, 'x, y = f()', '___vars___ = f()'),
    (True, 1, 'x, y = f()', '_vars_ = f()'),
    (True, 1, 'f(a=1, b=2)', 'f(b=2, a=1)'),
    (True, 1, '''
def f(x,y):
    """with a docstring"""
    if level <= 0:
        pass
    else:
        fd(3)
        lt(90)
    ''', '''
def f(_, _):
    ___
    if _:
        ___t___
    else:
        ___e___
    ___s___
     '''),
    (True, 1, '''
class A(B):
    def f(self, x):
        pass
     ''', 'class _(_): ___'),
    # (True, True,
    #  'for x, y in f():\n    ___',
    #  'for ___vars___ in f():\n    ___'),
    (False, 0, 'drawLs(size/2, level - 1)', 'drawLs(_size_/2.0, _)'),
    (False, 0, '2', '2.0'),
    (False, 0, '2', '_d_float_'),
    (True, 1, '''
def keepFirstLetter(phrase):
    """Returns a new string that contains only the first occurrence of a
    letter from the original phrase.
    The first letter occurrence can be upper or lower case.
    Non-alpha characters (such as punctuations and space) are left unchanged.
    """
    #this list holds lower-cased versions of all of the letters already used
    usedCharacters = []

    finalPhrase = ""
    for n in phrase:
        if n.isalpha():
            #we need to create a temporary lower-cased version of the letter,
            #so that we can check and see if we've seen an upper or lower-cased
            #version of this letter before
            tempN = n.lower()
            if tempN not in usedCharacters:
                usedCharacters.append(tempN)
                #but we need to add the original n, so that we can preserve
                #if it was upper cased or not
                finalPhrase = finalPhrase + n

        #this adds all non-letter characters into the final phrase list
        else:
            finalPhrase = finalPhrase + n

    return finalPhrase
    ''', '''
def _(___):
    ___
    _acc_ = ""
    ___
    for _ in _:
        ___
    return _acc_
    ___
    '''),
    (False, # Pattern should not match program
     1, # Pattern should be found within program
     # Program
     '''
def keepFirstLetter(phrase):
    #this list holds lower-cased versions of all of the letters already used
    usedCharacters = []

    finalPhrase = ""
    for n in phrase:
        if n.isalpha():
            #we need to create a temporary lower-cased version of the letter,
            #so that we can check and see if we've seen an upper or lower-cased
            #version of this letter before
            tempN = n.lower()
            if tempN not in usedCharacters:
                usedCharacters.append(tempN)
                #but we need to add the original n, so that we can preserve
                #if it was upper cased or not
                finalPhrase = finalPhrase + n

        #this adds all non-letter characters into the final phrase list
        else:
            finalPhrase = finalPhrase + n

    return finalPhrase
     ''',
     # Pattern
     '''
___prefix___
_acc_ = ""
___middle___
for _ in _:
    ___
return _acc_
___suffix___
     '''),
    (True, 1, '''
a = 1
b = 2
c = 3
     ''', '''___; _x_ = _n_'''),
    (False, # Pattern should not match program
     1, # Pattern should be found within program
     # Program
     '''
def f(a):
    x = ""
    return x
     ''',
     # Pattern
     '''
_acc_ = ""
return _acc_
     '''),

    # Treatment of elses:
    (True, 1, 'if x: print(1)', 'if _: _'),
    (False, 0, 'if x: print(1)\nelse: pass', 'if _: _'),
    (True, 1, 'if x: print(1)\nelse: pass', 'if _: _\nelse: ___'),
    (False, 0, 'if x: print(1)', '''
if _: _
else:
    _
    ___
     '''),
    (True, 1, 'if x: print(1)\nelse: pass', '''
if _: _
else:
    _
    ___
     '''),

    # If ExpandExplicitElsePattern is used:
    # (False, 0, 'if x: print(1)', 'if _: _\nelse: ___'),

    # If ExpandExplicitElsePattern is NOT used:
    (True, 1, 'if x: print(1)', 'if _: _\nelse: ___'),

    # Keyword arguments
    (True, 1, 'f(a=1)', 'f(a=1)'),
    (True, 1, 'f(a=1)', 'f(_kw_=1)'),
    (True, 1, 'f(a=1)', 'f(_kw_=_arg_)'),
    (True, 1, 'f(a=1)', 'f(_=1)'),
    (True, 1, 'f(a=1)', 'f(_=_arg_)'),
    (True, 1, 'f(a=1, b=2)', 'f(_x_=_, _y_=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(_x_=2, _y_=_)'),
    (False, 0, 'f(a=1, b=2)', 'f(_x_=_)'),
    (False, 0, 'f(a=1, b=2)', 'f(_x_=_, _y_=_, _z_=_)'),
    (False, 0, 'f(a=1, b=2)', 'f(_x_=2, _y_=2)'),
    (True, 1, 'f(a=1, b=2)', 'f(_x_=_, b=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(b=_, _x_=_)'),
    (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'),
    (True, 1, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'),
    (True, 1, 'f(a=1+2, b=2+1)', 'f(_c_=_x_+_y_, _d_=_y_+_x_)'),
    (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'),
    (False, 0, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'),
    (True, 1, 'f(a=1, b=2)', 'f(___=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, a=_, b=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(a=_, b=_, ___kwargs___=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_, a=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(b=_, a=_, ___kwargs___=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(a=_, ___kwargs___=_, b=_)'),
    (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_, a=_)'),
    (True, 1, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=_, _y_=_)'),
    (False, 0, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=1, _y_=_)'),

    # and/or set wildcards
    (True, 1, 'x or y or z', '_x_ or ___rest___'),
    (True, 1, 'x or y or z', '_x_ or _y_ or ___rest___'),
    (True, 1, 'x or y or z', '_x_ or _y_ or _z_ or ___rest___'),

    # kwarg matching
    (True, 1, 'def f(x=3):\n  return x', 'def _f_(x=3):\n  return x'),
    (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  return _'),
    (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  ___'),
    (True, 1, 'def f(x=3):\n  return x', 'def _f_(_x_=3):\n  return _x_'),
    (True, 1,
     'def f(y=7):\n  return y', 'def _f_(_x_=_y_):\n  return _x_'),
    (False, 0, 'def f(x=3):\n  return x', 'def _f_(_y_=7):\n  return _x_'),

    # Succeeds!
    (True, 1, 'def f(x=12):\n  return x', 'def _f_(_=_):\n  ___'),

    # Should match because ___ has no default
    (True, 1, 'def f(x=17):\n  return x', 'def _f_(___, _=17):\n  ___'),

    # Multiple kwargs
    (True, 1, 'def f(x=3, y=4):\n  return x', 'def _f_(_=3, _=4):\n  ___'),
    (True, 1, 'def f(x=5, y=6):\n  return x', 'def _f_(_=_, _=_):\n  ___'),
    # ___ doesn't match kwargs
    (False, 0, 'def f(x=7, y=8):\n  return x', 'def _f_(___):\n  ___'),

    # Exact matching of kwarg expressions
    (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=y+3):\n  ___'),

    # Matching of kw-only args
    (True, 1,
     'def f(*a, x=5):\n  return x',
     'def _f_(*_, _x_=5):\n  return _x_'),
    # ___ does not match *_
    (False, 0,
     'def f(*a, x=6):\n  return x',
     'def _f_(___, _x_=6):\n  return _x_'),

    # Multiple kw-only args
    (True, 1,
     'def f(*a, x=5, y=6):\n  return x, y',
     'def _f_(*_, _x_=5, _y_=6):\n  return _x_, _y_'),
    (False, 0,
     'def f(*a, x=7, y=8):\n  return x, y',
     'def _f_(___, _x_=7, _y_=8):\n  return _x_, _y_'),

    # Function with docstring (must use ast.get_docstring!)
    (False, 0, 'def f():\n  """docstring"""', 'def _f_(___):\n  _a_str_'),

    # Function with docstring (using ast.get_docstring)
    (True, 1,
     'def f(x):\n  """doc1"""\n  return x',
     'def _f_(___):\n  ___',
     lambda node, env: ast.get_docstring(node) is not None),

    # Function without docstring (using ast.get_docstring)
    (False, 0,
     'def f(x):\n  """doc2"""\n  return x',
     'def _f_(___):\n  ___',
     lambda node, env:(
         ast.get_docstring(node) is None
      or ast.get_docstring(node).strip() == ''
     )),
    (True, 1,
     'def f(x):\n  """"""\n  return x',
     'def _f_(___):\n  ___',
     lambda node, env:(
         ast.get_docstring(node) is None
      or ast.get_docstring(node).strip() == ''
     )),
    (True, 1,
     'def nodoc(x):\n  return x',
     'def _f_(___):\n  ___',
     lambda node, env:(
         ast.get_docstring(node) is None
      or ast.get_docstring(node).strip() == ''
     )),

    # TODO: Recursive matching of kwarg expressions
    (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=_+3):\n  ___'),

    # Function with multiple normal arguments
    (True, 1, 'def f(x, y, z):\n  return x', 'def _f_(___):\n  ___'),

    # Matching redundant elif conditions
    (
      True,
      1,
      'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
    ),
    ( # order matters
      False,
      0,
      'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
    ),
    ( # not == is not the same as !=
      False,
      0,
      'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
    ),
    ( # not == is not the same as !=
      True,
      1,
      'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2',
      'if _cond_:\n  ___\nelif ___ and not _cond_:\n  ___'
    ),
    ( # not == is not the same as !=
      True,
      1,
      'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2',
      'if _n_ == _v_:\n  ___\nelif ___ and _n_ != _v_:\n  ___'
    ),
    ( # extra conditions do matter!
      False,
      0,
      'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
    + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
    ),
    ( # match extra conditions:
      True,
      1,
      'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
    + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'
    ),
    ( # number of conditions must match exactly:
      False,
      0,
      'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
    + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0\n'
    + 'elif not x == 3 and x <= 5 and x >= 0 and x == 1:\n  return 1.5',
      'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'
    ),
    ( # matching with elif:
      True,
      2,
      'if x < 0:\n  x += 1\nelif x < 10:\n  x += 0.5\nelse:\n  x += 0.25',
      'if _:\n  ___\nelse:\n  ___'
    ),
    ( # left/right branches are both okay
      True,
      1,
      'x == 3',
      '3 == x',
    ),
    ( # order does matter for some operators
     False,
     0,
     '1 + 2 + 3',
     '3 + 2 + 1'
    ),
    ( # but not for others
     True,
     1,
     '1 and 2 and 3',
     '3 and 2 and 1'
    ),

    # Import matching
    (True, 1, 'import math', 'import _'),
    (False, 0, 'import math as m', 'import _'),
    (True, 1, 'import math as m', 'import _ as _'),
    (True, 1, 'import math as m', 'import _ as _'),
    (True, 1, 'import math as m', 'import math as _'),
    (True, 1, 'import math as m', 'import _ as m'),
    (True, 1, 'import math as m', 'import math as m'),
    (True, 1, 'import math, io', 'import ___'),
    (True, 1, 'import math, io', 'import math, ___'),
    (True, 1, 'import math, io', 'import io, ___'),
    (False, 0, 'from math import cos, sin', 'import math'),
    (False, 0, 'from math import cos, sin', 'import _'),
    (False, 0, 'from math import cos, sin', 'import ___'),
    (True, 1, 'from math import cos, sin', 'from _ import ___'),
    (True, 1, 'from math import cos, sin', 'from _ import _x_, sin'),
    (True, 1, 'from math import cos, sin', 'from _ import cos, _x_'),
    (True, 1, 'from math import cos, sin', 'from _ import _x_, cos'),
    (True, 1, 'from math import cos, sin', 'from _ import sin, _x_'),
    (True, 1, 'from math import cos, sin', 'from _ import _x_, ___'),
    # Note: two bindings, but only one node match
    (True, 1, 'from math import cos, sin', 'from math import ___'),
    (True, 1, 'from math import cos, sin', 'from math import cos, sin'),
    (True, 1, 'from math import cos, sin', 'from math import sin, cos'),
]

# These tests fail, but in the future, maybe they could pass?
FAILING = [
    # TODO: Fails probably because of docstring issues?
    (True, 1,
     '''
def f(x,y):
    """I have a docstring.
    It is a couple lines long."""
    eye = Layer()
    if eye:
        face = Layer()
    else:
        face = Layer()
    eye2 = Layer()
    face.add(eye)
    face.add(eye2)
    return face
     ''',
     '''
def f(___args___):
    eye = Layer()
    ___
     '''),

    # TODO: Fails because we compare all defaults as one block
    # Zero extra keyword arguments:
    (True, 1, 'def f(x=17):\n  return x', 'def _f_(_=17, ___=_):\n  ___'),

    # TODO: Fails because of default matching bug
    (True, 1, 'def f(x=9, y=10):\n  return x', 'def _f_(___=_):\n  ___'),
]


# TODO: Get this to work!!!
def _test_import_findall_envs():
    """
    Tests # of environment matches w/ findall & a mix of scalar/set vars.
    Note that this DOESN'T work for 3+ imports, and that's a bug...
    """
    node = mast.parse("from math import cos, sin, tan")
    pat = mast.parse_pattern("from _ import _x_, ___")
    results = list(mast.findall(node, pat))
    assert len(results) == 1
    mn, me = results[0]
    assert isinstance(mn, ast.ImportFrom)
    assert mn.module == "math"
    assert mn.level == 0
    print("names:", [e['x'].id for e in me])
    assert len(me) == 3
    assert all(len(env) == 1 for env in me)
    assert all('x' in env for env in me)
    xs = [env['x'] for env in me]
    assert len([x for x in xs if x.id == "cos"]) == 1
    assert len([x for x in xs if x.id == "sin"]) == 1
    assert len([x for x in xs if x.id == "tan"]) == 1


def test_two_aliases():
    """
    Tests matching a list of two aliases against different permutations
    of a scalar + set var.
    """
    node = [
        ast.alias(name="cos", asname=None),
        ast.alias(name="sin", asname=None)
    ]
    pat1 = [
        ast.alias(name="_x_", asname=None),
        ast.alias(name="___", asname=None)
    ]
    pat2 = [
        ast.alias(name="___", asname=None),
        ast.alias(name="_x_", asname=None)
    ]

    m1 = list(mast.imatches(node, pat1, mast_utils.Some({}), True))
    m2 = list(mast.imatches(node, pat2, mast_utils.Some({}), True))

    assert len(m1) == 1
    assert len(m2) == 1
    e1 = m1[0]
    e2 = m2[0]
    assert len(e1) == 1
    assert len(e2) == 1
    assert 'x' in e1
    assert 'x' in e2
    x1 = e1['x']
    x2 = e2['x']
    assert x1.id == 'cos'
    assert x2.id == 'sin'


def test_mast():
    """
    Runs all of the TESTS.
    """
    for test_spec in TESTS:
        run_test(*test_spec)


def run_test(
    expect_match,
    expect_count,
    src,
    pattern,
    matchpred=mast.predtrue
):
    """
    Runs a test of the match, find, and count functions using a given
    source string to match against and pattern to match. A match
    predicate may also be provided to test that functionality, but is
    optional.

    You must specify whether a match is expected for the full pattern,
    and the number of matches expected in count mode.
    """
    # Create & reduce the node to match against
    node = mast.parse(src)
    node = (
        node.body[0].value
        if type(node.body[0]) == ast.Expr and len(node.body) == 1
        else (
            node.body[0]
            if len(node.body) == 1
            else node.body
        )
    )

    # Create our pattern node
    pat_node = mast.parse_pattern(pattern)

    # Messages to include when we assert for context
    baggage = ''
    baggage += f'Program: {src} => {mast.dump(node)}\n'
    if isinstance(node, ast.FunctionDef):
        baggage += f'Docstring: {ast.get_docstring(node)}\n'

    baggage += f'Pattern: {pattern} => {mast.dump(pat_node)}\n'

    if matchpred != mast.predtrue:
        baggage += f'Matchpred: {matchpred.__name__}\n'

    # gen = False
    assert (
        bool(mast.match(node, pat_node, gen=False, matchpred=matchpred))
     == expect_match
    ), baggage

    # gen = True
    assert (
        bool(
            mast_utils.takeone(
                mast.match(node, pat_node, gen=True, matchpred=matchpred)
            )
        )
     == expect_match
    ), baggage

    opt = mast.find(node, pat_node, matchpred=matchpred)
    assert bool(opt) == (0 < expect_count), baggage

    c = mast.count(node, pat_node, matchpred=matchpred)
    assert c == expect_count, baggage

    nmatches = 0
    for (node, envs) in mast.findall(node, pat_node, matchpred=matchpred):
        # find should return first findall result.
        if nmatches == 0:
            fnode, fenvs = opt.get()
            # Note: because of arg -> name conversion, == doesn't work on
            # the envs, since the name nodes produced will be the same,
            # but they won't be == to each other!

            assert fnode == node, baggage
            assert [
                {k: mast.dump(env[k]) for k in env}
                for env in envs
            ] == [
                {k: mast.dump(env[k]) for k in env}
                for env in fenvs
            ], baggage
        nmatches += 1
        pass

    # count should count the same number of matches that findall finds.
    assert nmatches == c, baggage
