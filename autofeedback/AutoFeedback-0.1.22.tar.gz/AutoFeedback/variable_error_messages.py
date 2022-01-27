from __future__ import print_function


def _existence_error(varname):
    error_message = """The variable {} does not exist.
    Ensure you have named the variable properly,
    bearing in mind that capital letters matter.
    """.format(varname)
    return(error_message)


def _size_error(varname):
    error_message = """The variable {} is the wrong size.
    Try using len(...) to determine the size of the array, or print(...)
    to check the values look as you expect them to.
    """.format(varname)
    return(error_message)


def _value_error(varname, exp, res):
    error_message = """The variable {} has the wrong value(s)\n
        We expected the output:
        {}\n
        but instead we got:
        {}\n
        Try using print(...) to check the values look as you expect them to
        and ensure the expression used to calculate the variable
        is correct.
        """.format(varname, exp, res)
    return(error_message)


def _import_error():
    error_message = """Your code failes to execute.
    Please refer to the error messages printed in the terminal to resolve
    any errors in your code.
    """
    return(error_message)


def print_error_message(error, varname, exp, res):
    from AutoFeedback.bcolors import bcolors

    if (str(error) == "success"):
        print(f"{bcolors.OKGREEN}Variable {varname} is correct!\
              \n{bcolors.ENDC}")

    else:
        if (str(error) == "existence"):
            emsg = _existence_error(varname)
        elif (str(error) == "size"):
            emsg = _size_error(varname)
        elif (str(error) == "value"):
            emsg = _value_error(varname, exp, res)
        elif (str(error) == "import"):
            emsg = _import_error()
        else:
            emsg("something not right with "+varname)
        print(f"{bcolors.FAIL}{emsg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{30*'='}\n{bcolors.ENDC}")


def output_check(expected, executable="main.py"):
    import subprocess
    import sys
    from AutoFeedback.bcolors import bcolors

    def run(cmd):
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                )
        stdout = proc.communicate()

        return stdout

    out = run([sys.executable, executable])
    screen_out = str(out).split("'")[1]

    check = screen_out == expected+"\\n"

    errmsg = """The text printed to screen is not correct. Ensure you have
        printed the correct variables, in the correct order,
        and that nothing else is printed."""

    if not (check):
        print(f"{bcolors.FAIL}test_output has failed. \n{errmsg}")
    else:
        print(f"{bcolors.OKGREEN}Printing is correct!\n")

    print(f"{bcolors.WARNING}{30*'='}\n{bcolors.ENDC}")

    return check
