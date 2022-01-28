#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
from typing import Iterator


def new(classin="class_", input="[]", translated_input="[]", output="obj", configin="config=None", version=0, **kwargs):
    r"""
    Instantiate a Python class

    'config' overrides 'input', when conflicting keys are provided.

    >>> from idict import idict, let
    >>> d = idict.fromtoy(output_format="df")
    >>> from sklearn.model_selection import StratifiedKFold
    >>> config = {"n_splits":2, "random_state":0, "shuffle":True}
    >>> d >>= let(new, class_=StratifiedKFold, config=config)
    >>> d.obj
    StratifiedKFold(n_splits=2, random_state=0, shuffle=True)
    """
    if input == "[]":
        input = []
    if translated_input == "[]":
        translated_input = []
    class_ = kwargs[classin]
    config = kwargs[configin]
    if translated_input:
        multidynamic_input = {}
        for i, tr in enumerate(translated_input):
            multidynamic_input[tr] = kwargs[input[i]]
        result = class_(**multidynamic_input, **config)
    else:
        multidynamic_input = [kwargs[_i] for _i in input]
        result = class_(*multidynamic_input, **config)
    return {output: result, "_history": ...}


# REMINDER: A field cannot be used to define a dependence on another field.
#   Only parameters can do that.
#   Otherwise, it would lead to kwargs[kwargs[field]], whose detection is messy at the application step.
def call(
    field="obj",
    methodin="method",
    input="[]",
    translated_input="[]",
    output="call",
    configin="config=None",
    version=0,
    **kwargs
):
    r"""
    Call a method on a field

    Evaluate iterators, if any.
    'config' overrides 'input', when conflicting keys are provided.

    >>> from idict import idict, let
    >>> d = idict.fromtoy(output_format="Xy")
    >>> from sklearn.model_selection import StratifiedKFold
    >>> config = {"n_splits":3, "random_state":0, "shuffle":True}
    >>> d >>= let(new, class_=StratifiedKFold, config=config)
    >>> d.obj
    StratifiedKFold(n_splits=3, random_state=0, shuffle=True)
    >>> d >>= let(call, method="split", input=["X","y"], output=["partition1", "partition2", "partition3"])
    >>> d.partition2
    (array([ 0,  2,  5,  6,  7,  8,  9, 11, 12, 13, 14, 16, 17]), array([ 1,  3,  4, 10, 15, 18, 19]))
    """
    # Multidynamic input is only detected when the kwargs index is also indexed by something.
    if input == "[]":
        input = []
    if translated_input == "[]":
        translated_input = []
    config = kwargs[configin] if configin in kwargs else {}
    if translated_input:
        multidynamic_input = {}
        for i, tr in enumerate(translated_input):
            multidynamic_input[tr] = kwargs[input[i]]
        result = getattr(kwargs[field], kwargs[methodin])(**multidynamic_input, **config)
    else:
        multidynamic_input = [kwargs[_i] for _i in input]
        result = getattr(kwargs[field], kwargs[methodin])(*multidynamic_input, **config)

    if isinstance(result, Iterator):
        result = list(result)
    if isinstance(output, str):
        return {output: result}
    # Multidynamic output cannot be detected, so it can only be defined as metadata.
    return {k: v for k, v in zip(output, result)}


def at(field="obj", indexin="index", output="at", version=0, **kwargs):
    r"""
    Access value inside an indexed field

    Evaluate value-iterator, if it is the case.

    >>> from idict import idict, let
    >>> d = idict.fromtoy(output_format="df")
    >>> from sklearn.model_selection import StratifiedKFold
    >>> config = {"n_splits":3, "random_state":0, "shuffle":True}
    >>> d >>= let(new, class_=StratifiedKFold, config=config)
    >>> d.obj
    StratifiedKFold(n_splits=3, random_state=0, shuffle=True)
    >>> d["y"] = d.df.iloc[:,-1]
    >>> d >>= let(call, method="split", input=["df", "y"], translated_input=["X", "y"], output=[f"p{i}" for i in range(3)])
    >>> d["itr"], d["its"] = d.p2
    >>> d.its
    array([ 2,  6,  9, 11, 12, 17])
    >>> d >>= let(at, field="df", indexin="its", output="ts")
    >>> d.ts
        attr1  attr2  class
    2     6.1    3.6      0
    6     9.1    3.5      0
    9     2.5    4.5      1
    11    0.1    4.3      1
    12    2.1    0.1      0
    17    2.2    8.5      1
    """
    obj = kwargs[field]
    if hasattr(obj, "iloc"):
        result = obj.iloc[kwargs[indexin]]
    else:
        result = obj[kwargs[indexin]]
    if isinstance(result, Iterator):
        result = list(result)
    if isinstance(output, str):
        return {output: result}
    # Multidynamic output cannot be detected, so it can only be defined as metadata.
    return {k: v for k, v in zip(output, result)}


def access(field="obj", propertyin="property", output="access", version=0, **kwargs):
    r"""
    Access a property on a field

    >>> from idict import idict, let
    >>> d = idict.fromtoy(output_format="df")
    >>> cache = {}
    >>> d >>= let(access, field="df", property="head", output="head") >> [cache]
    >>> d.head
    <bound method NDFrame.head of     attr1  attr2  class
    0     5.1    6.4      0
    1     1.1    2.5      1
    2     6.1    3.6      0
    3     1.1    3.5      1
    4     3.1    2.5      0
    5     4.7    4.9      1
    6     9.1    3.5      0
    7     8.3    2.9      1
    8     9.1    7.2      0
    9     2.5    4.5      1
    10    7.1    6.6      0
    11    0.1    4.3      1
    12    2.1    0.1      0
    13    0.1    4.0      1
    14    5.1    4.5      0
    15   31.1    4.7      1
    16    1.1    3.2      0
    17    2.2    8.5      1
    18    3.1    2.5      0
    19    1.1    8.5      1>
    >>> d = idict(d.id, cache)
    >>> d.history
    {'idict--------------------wrapper--access': {'name': 'access', 'description': 'Access a property on a given field.', 'parameters': {'field': 'df', 'propertyin': 'property', 'output': 'head', 'version': 0, 'property': 'head'}, 'code': "def f(field='obj', propertyin='property', output='access', version=0, **kwargs):\nreturn {output: getattr(kwargs[field], kwargs[propertyin]), '_history': ...}"}}
    """
    return {output: getattr(kwargs[field], kwargs[propertyin]), "_history": ...}


def apply(
    functionin="function",
    input="[]",
    translated_input="[]",
    output=["apply"],
    configin="config=None",
    version=0,
    **kwargs
):
    r"""
    >>> from sklearn.utils import resample
    >>> from idict import idict, let
    >>> d = idict(X=[[1,2,3], [4,5,6], [11,12,13]], y=[7,8,9])
    >>> d >>= let(apply, function=resample, input=["X", "y"], output=["X", "y"], config={"n_samples":2, "random_state":0})
    >>> d.X
    [[1, 2, 3], [4, 5, 6]]
    >>> d.y
    [7, 8]
    """
    if input == "[]":
        input = []
    if translated_input == "[]":
        translated_input = []
    f = kwargs[functionin]
    config = kwargs[configin]
    if translated_input:
        multidynamic_input = {}
        for i, tr in enumerate(translated_input):
            multidynamic_input[tr] = kwargs[input[i]]
        result = f(**multidynamic_input, **config)
    else:
        multidynamic_input = [kwargs[_i] for _i in input]
        result = f(*multidynamic_input, **config)

    out = {k: v for k, v in zip(output, result)}
    # Multidynamic output cannot be detected, so it can only be defined as metadata.
    return out


new.metadata = {
    "id": "idict-----------------------wrapper--new",
    "name": "new",
    "description": "Instantiate a Python class.",
    "parameters": ...,
    "code": ...,
}
call.metadata = {
    "id": "idict----------------------wrapper--call",
    "name": "call",
    "description": "Call a method on a given field.",
    "parameters": ...,
    "code": ...,
    "output": {"fields": [], "auto": ["_history"], "meta": [], "dynamic": ["output"]},
}
at.metadata = {
    "id": "idict------------------------wrapper--at",
    "name": "at",
    "description": "Access value inside an indexed field.",
    "parameters": ...,
    "code": ...,
    "output": {"fields": [], "auto": ["_history"], "meta": [], "dynamic": ["output"]},
}
access.metadata = {
    "id": "idict--------------------wrapper--access",
    "name": "access",
    "description": "Access a property on a given field.",
    "parameters": ...,
    "code": ...,
}
apply.metadata = {
    "id": "idict---------------------wrapper--apply",
    "name": "apply",
    "description": "Apply a function.",
    "parameters": ...,
    "code": ...,
    "output": {"fields": [], "auto": ["_history"], "meta": [], "dynamic": ["output"]},
}
