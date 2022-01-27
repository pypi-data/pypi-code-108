import importlib


def _exists(funcname, modname=None):
    import inspect
    if not modname:
        mod = importlib.import_module('main')
    else:
        mod = modname
    funcstring = "mod."+funcname  # get variable from main code
    try:
        testfunc = eval(funcstring)
        return(inspect.isfunction(testfunc))
    except Exception:
        return (False)


def _get_func(funcname, modname=None):
    if not modname:
        mod = importlib.import_module('main')
    else:
        mod = modname
    funcstring = "mod."+funcname  # get function from main code
    return(eval(funcstring))


def _input_vars(func, ins):
    from copy import deepcopy as dc
    inputs = dc(ins)
    try:
        if hasattr(inputs, "__len__"):
            func(*inputs)
        else:
            func(inputs)
        return True
    except TypeError:
        return (False)


def _returns(func, ins):
    from copy import deepcopy as dc
    inputs = dc(ins)
    try:
        if hasattr(inputs, "__len__"):
            res = func(*inputs)
        else:
            res = func(inputs)
        if hasattr(res, "__len__"):
            res = list(res)
        return (res is not None)
    except Exception:
        return False


def _check_outputs(func, ins, expected):
    from AutoFeedback.varchecks import check_value
    from copy import deepcopy as dc
    inputs = dc(ins)
    try:
        res = func(*inputs)
        if hasattr(expected, "check_value") and callable(expected.check_value):
            return expected.check_value(res)
        else:
            return (check_value(res, expected))
    except Exception:
        return False


def _check_calls(func, inputs, call):
    import inspect
    import ast
    try:
        all_names = [c.func for c in ast.walk(
            ast.parse(inspect.getsource(func))) if isinstance(c, ast.Call)]
        call_names = [name.id for name in all_names if
                      isinstance(name, ast.Name)]
        return (call in call_names)
    except Exception:
        return False


def check_func(funcname, inputs, expected, calls=[],
               modname=None, output=True):
    from AutoFeedback.function_error_messages import print_error_message
    from copy import deepcopy as copy
    call = []
    ins = inputs[0]
    outs = expected[0]
    res = -999
    try:
        assert(_exists(funcname, modname)), "existence"
        func = _get_func(funcname, modname)
        assert(_input_vars(func, inputs[0])), "inputs"

        assert(_returns(func, inputs[0])), "return"
        for ins, outs in zip(inputs, expected):
            res = func(*copy(ins))  # ensure the inputs are not overwritten
            assert(_check_outputs(func, ins, outs)), "outputs"
        for call in calls:
            assert(_check_calls(func, inputs[0], call)), "calls"
        if output:
            print_error_message("success", funcname)
    except AssertionError as error:
        if output:
            print_error_message(error, funcname, inp=ins,
                                exp=outs, result=res, callname=call)
        return(False)
    except Exception:
        if output:
            print_error_message("execution", funcname, inp=ins)
        return(False)

    return(True)
