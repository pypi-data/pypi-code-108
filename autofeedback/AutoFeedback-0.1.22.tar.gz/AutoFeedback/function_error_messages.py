from __future__ import print_function


def _existence_error(varname):
    error_message = f"""The function {varname} does not exist.
    Ensure you have named the function properly, bearing in mind that capital
    letters matter. Also ensure that you have used the proper syntax for the
    definition of a function, i.e.
        def {varname}(inputs):
            ...
    """
    return(error_message)


def _input_error(varname, numargs):
    error_message = f"""The function {varname} does not accept input correctly.
    The function is supposed to accept {numargs} input argument(s).
    Ensure you have specified the input arguments in the function definition.
    i.e.
        def {varname}(input_1, input_2, ...):
            ...
    """
    return(error_message)


def _value_error(varname, inp,  exp, res):
    error_message = f"""The function {varname} returns the wrong value(s).
    When executed with the input(s), {inp}, we expected the output, {exp}, but
    instead we got {res}.
    """
    return(error_message)


def _return_error(varname):
    error_message = f"""The function {varname} does not return a value.
    Ensure that the function uses the correct syntax for a return statement.
    i.e.
        def {varname}(input):
            ...
            return (answer)
    """
    return(error_message)


def _call_error(varname, callname):
    error_message = f"""The function {varname} does not call the function {callname}.
    Make sure that rather than repeating lines of code, your function passes
    input to the previously defined function, e.g.

        def {callname}(input):
            ...
            return (answer)
        def {varname}(input):
            ...
            new_answer = some_operation + {callname}(input)
            return(new_answer)
    """
    return(error_message)


def _execution_error(varname, inp):
    error_message = f"""The function {varname} does not execute correctly.
    Test it by adding a function call, e.g.
        print({varname}({inp})
        """
    return(error_message)


def print_error_message(error, varname, inp=(0,), exp=7, result=0,
                        callname='print'):
    from AutoFeedback.bcolors import bcolors

    if (str(error) == "success"):
        print(f"{bcolors.OKGREEN}Function, {varname} is correct!\
              \n{bcolors.ENDC}")

    else:
        if (str(error) == "existence"):
            emsg = _existence_error(varname)
        elif (str(error) == "inputs"):
            emsg = _input_error(varname, len(inp))
        elif (str(error) == "outputs"):
            if hasattr(exp, "get_error") and callable(exp.get_error):
                emsg = exp.get_error(
                    f"values returned from the function {varname} with input\
                    parameters {inp}")
            else:
                emsg = _value_error(varname, inp, exp, result)
        elif (str(error) == "return"):
            emsg = _return_error(varname)
        elif (str(error) == "calls"):
            emsg = _call_error(varname, callname)
        elif (str(error) == "execution"):
            emsg = _execution_error(varname, inp)
        else:
            emsg = (f"something not right with {varname}")
        print(f"{bcolors.FAIL}{emsg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{30*'='}\n{bcolors.ENDC}")
