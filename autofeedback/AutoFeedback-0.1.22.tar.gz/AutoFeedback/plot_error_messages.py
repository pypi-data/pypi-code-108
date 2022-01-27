from __future__ import print_function


class error_message():
    def _data(label):
        return (f"""Data set {label} is plotted with incorrect data.
    Check that all variables are correctly defined, and that you are plotting
    the right variables in the right order (i.e. plt.plot(X,Y))""")

    def _linestyle(label):
        return (f"""Data set {label} is plotted with the incorrect linestyle.
    Set the linestyle with the optional third argument in the plot command e.g.
        plt.plot(X,Y,'--')
    for dashed lines or
        plt.plot(X,Y,'.')
    for dots.""")

    def _marker(label):
        return (f"""Data set {label} is plotted with incorrect markers.
    Set the marker with the optional third argument in the plot command e.g.
        plt.plot(X,Y,'.')
    for points
        plt.plot(X,Y,'o ')
    for circles.""")

    def _colour(label):
        return (f"""Data set {label} is plotted with the incorrect colour.
    Set the colour with the optional third argument in the plot command e.g.
        plt.plot(X,Y,'k')
    for black or
        plt.plot(X,Y,'r')
    for red.""")

    _axes = """The axis limits in your plot are set incorrectly.
    Set the axis limits with the plt.axis command like this
        plt.axis([ -1 , 1, -2, 2])
    where the four numbers correspond to the lower and upper limits of the x
    and y-axes respectively."""

    _labels = """The axis labels or titles in your plot are set incorrectly.
    Set the axis labels with the plt.xlabel and plt.ylabel commands like this
        plt.xlabel('this is the x axis label')
        plt.ylabel('this is the y axis label')
        plt.title('this is the title')
    remembering to check that the spacing, case and spelling of all words are
    correct """

    _legend = """The legend does not contain the correct data labels
    Set the legend entries with the option 'label' keyword argument in the plot
    command like this
        plt.plot(X,Y,label="my data set")
    and then reveal the legend in your plot like this
        plt.legend()
    remembering to check that the spacing, case and spelling of all words are
    correct.

    You must place the plt.legend() command AFTER you have plotted ALL the data
    sets, or only some of the legend entries will show.
        """

    _datasets = """The number of data sets plotted is incorrect.
    Check that the number of datasets plotted matches the number requested in
    the instructions"""

    def _partial(name):
        return (f"""Dataset {name} plotted correctly!\n""")

    _success = "Plot is correct!\n"


def print_error_message(error, expline):
    from AutoFeedback.bcolors import bcolors
    if (str(error) == "_success" or str(error)[0:8] == "_partial"):
        emsg = eval("error_message."+str(error))
        print(f"{bcolors.OKGREEN}{emsg}{bcolors.ENDC}")
    elif hasattr(expline, "diagnosis") and expline.diagnosis != "ok":
        emsg = expline.get_error(
            str(error).replace("_data(", "").replace(")", ""))
        print(f"{bcolors.FAIL}{emsg}{bcolors.ENDC}")
    else:
        emsg = eval("error_message."+str(error))
        print(f"{bcolors.FAIL}{emsg}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}{30*'='}\n{bcolors.ENDC}")
