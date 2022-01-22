import os

def standTextOut(string, printMechanismDash=print, printMechanismString=print, fallbackToPrint=True):
    """
    *** NEW IN 2.0: FALLS BACK TO printMechanismDash("\t") FOLLOWED BY printMechanismString(string) IF FANCY TEXT FAILS.
        * To fall back to original functionality, switch fallbackToPrint to False.
    param string: the string to sandwich in between the dashes.
    param printMechanismDash: how it will output the dashes. e.g. do `logging.info' to output it with logging.info. Defaults to print.
        ***IF YOU CHOOSE A PRINT MECHANISM IT NEEDS TO BE IMPORTED IN YOUR ORIGINAL PROGRAM, **NOT** THIS MODULE! How does it work?! you pass the function of output and it uses it.
    param printMechanismString: how it will output the string that is sandwidched in between the dashes. Defaults to print.
        ***READ THE ABOVE IMPORTANT NOTICE (of printMechanismDash)!!!***
    """
    try:
        width = os.get_terminal_size().columns
        dashes = "-" * width
        return (
                printMechanismDash(dashes),
                printMechanismString(string.center(width)),
                printMechanismDash(dashes)
                )
    except OSError:
        if fallbackToPrint:
            return printMechanismDash("\t"), printMechanismString(string), None
        raise

def standTextOut_Return(string):
    """
    Will return the finished string so you can output it the way you want.
    """
    width = os.get_terminal_size().columns
    result = "-" * width
    result = (result + "\n" + string.center(width))
    result = (result + "\n" + ("-" * width))
    return result
