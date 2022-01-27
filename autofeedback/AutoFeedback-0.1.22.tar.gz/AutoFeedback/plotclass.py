from AutoFeedback.varchecks import check_value
from AutoFeedback import plot_error_messages


class line:
    def __init__(self, xdata, ydata, linestyle=None, colour=None,
                 label=None, marker=None):
        self.xdata = xdata
        self.ydata = ydata
        self.linestyle = linestyle
        self.colour = colour
        self.label = label
        self.marker = marker
        self.diagnosis = "ok"

    def get_xydata(self):
        return(self.xdata, self.ydata)

    def check_linedata(self, x, y, no_diagnose=False):
        goodx, goody = False, False
        if hasattr(self.xdata, "check_value") and\
                callable(self.xdata.check_value):
            goodx = self.xdata.check_value(x)
        else:
            goodx = check_value(x, self.xdata)
        if hasattr(self.ydata, "check_value") and\
                callable(self.ydata.check_value):
            goody = self.ydata.check_value(y)
        else:
            goody = check_value(y, self.ydata)
        if not goodx and not goody:
            self.diagnosis = "badxy"
        elif not goodx:
            self.diagnosis = "badx"
        elif not goody:
            self.diagnosis = "bady"
        if no_diagnose:
            # reset self.diagnose if we are just running check_linedata
            # to get the lines in the right order
            self.diagnosis = "ok"
        return(goodx and goody)

    def generic_error(self, label, axis):
        return(f"The {axis}-coordinates of the points in the data set {label} \
are incorrect\n" +
               ("""
       The instructions in the README file explain the specific values
       for the coordinates of the points in your graph.
       Make sure you have read those instructions carefully and that you
       know what the coordinates of the points in your graph should be
                """))

    def get_error(self, label):
        if self.diagnosis == "badxy":
            error_message = plot_error_messages.error_message._data(label)
        elif self.diagnosis == "badx":
            if hasattr(self.xdata, "get_error") and\
                    callable(self.xdata.get_error):
                error_message = self.xdata.get_error(
                    "x coordinates of the data series in the graph labelled "
                    + label)
            else:
                error_message = self.generic_error(label, "x")
        elif self.diagnosis == "bady":
            if hasattr(self.ydata, "get_error") and\
                    callable(self.ydata.get_error):
                error_message = self.ydata.get_error(
                    "y coordinates of the data series in the graph labelled "
                    + label)
            else:
                error_message = self.generic_error(label, "y")
        return error_message
