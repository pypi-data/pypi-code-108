import sys
import click

class NagErrors(object):
    '''

    The NagErrors object contains the processed Nagios Errors

    Args:
        - None -

    Attributes:
        critical (list of str's): The list of Critical Errors
        warning (list of str's): The list of Warning Errors
        unknown (list of str's): The list of Unknown Errors
    '''
    def __init__(self):
        self.critical = []
        self.warning = []
        self.unknown = []

    def addRecord(self, etype, etext):
        '''
        Add a record of a specific type

        Args:
            etype (enum str): One of 'crititcal', 'warning', 'unknown', the type of error
            etext (str): The descriptive text of the error
        '''
        if etype == 'critical':
            self.critical.append(etext)
        elif etype == 'warning':
            self.warning.append(etext)
        else:
            self.unknown.append(etext)

    def addCritical(self, etext):
        '''
        Add a critical record

        Args:
            etext (str): The descriptive text of the error
        '''
        self.addRecord('critical', etext)
    
    def addWarning(self, etext):
        '''
        Add a warning record

        Args:
            etext (str): The descriptive text of the error
        '''
        self.addRecord('warning', etext)
    
    def addUnknown(self, etext):
        '''
        Add a unknown record

        Args:
            etext (str): The descriptive text of the error
        '''
        self.addRecord('unknown', etext)

    def formatStatus(self, stype, sarr):
        '''
        Format an array of status lines

        Args:
            stype (str): Error Type of array
            sarr (List of str's): Error Messages

        Returns:
            str: Formated list of errors
        '''
        ret = ""
        if len(sarr) == 1:
            ret += "{} {}\r\n".format(stype, sarr[0])
        else:
            ret += "{}:\r\n".format(stype)
            for l in sarr:
                ret += "    {}\r\n".format(l)
        return(ret)

    def printStatus(self):
        '''
        Print properly formatted Nagios status information

        Args:
            - none -
        '''
        if len(self.unknown) > 0 :
            click.echo(self.formatStatus('UNKNOWN', self.unknown))
        if len(self.critical) > 0 :
            click.echo(self.formatStatus('CRITICAL', self.critical))
        if len(self.warning) > 0 :
            click.echo(self.formatStatus('WARNING', self.warning))
        if len(self.unknown) + len(self.critical) + len(self.warning) == 0 :
            click.echo('OK')
        
    def getExitCode(self):
        '''
        Get the returncode that should be exited with.

        Args:
            - none -

        Returns:
            int: Calculated returncode based on the current status lines
        '''
        if len(self.unknown) > 0 :
            return 3
        if len(self.critical) > 0 :
            return 2
        if len(self.warning) > 0 :
            return 1
        return 0

    def doExit(self):
        '''
        Exit with the proper returncode

        Args:
            - none -
        '''
        sys.exit(self.getExitCode())


class NagEval(object):
    '''

    The NagEval object provides common comparison/evaluators for testdata

    Args:
        errObj (NagErrors): NagErrors object used to store results

    Attributes:
        errObj (NagErrors): NagErrors object used to store results
    '''
    def __init__(self, errObj):
        self.errObj = errObj


    def evalListEnum(self, values, emptyStatus="UNKNOWN", unknownValueStatus="UNKNOWN", okValues=[], warningValues=[], criticalValues=[], unknownValues=[], prefixText="", postfixText= ""):
        '''
        Evaluate a list of values based on lists of enumerated values

        Args:
            values (List of str/num): Values to test
            emptyStatus (str): Result if values is an empty list
            unknownValueStatus (str): Status to assign to values that are not in any lists (OK, WARNING, CRITICAL, or UNKNOWN)
            okValues (List of str/num): Values to match for OK Status
            warningValues (List of str/num): Values to match for Warning Status
            criticalValues (List of str/num): Values to match for Critical Status
            unknownValues (List of str/num): Values to match for Unknown Status
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL,UNKNOWN)
        '''
        if (type(values) == list and len(values) == 0) or (type(values) != list and values == ""):
            if emptyStatus != "OK":
                self.errObj.addRecord(emptyStatus.lower(),"{}list is Empty{}".format(prefixText, postfixText))
            return(emptyStatus)
        if type(values) != list:
            return self.evalEnum(values, unknownValueStatus, okValues, warningValues, criticalValues, unknownValues, prefixText, postfixText)

        ret = "OK"
        rvals = {"OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3}
        for value in values:
            r = self.evalEnum(value, unknownValueStatus, okValues, warningValues, criticalValues, unknownValues, prefixText, postfixText)
            if rvals[r] > rvals[ret]:
                ret = r
        return ret


    def evalEnum(self, value, defaultStatus="UNKNOWN", okValues=[], warningValues=[], criticalValues=[], unknownValues=[], prefixText="", postfixText= ""):
        '''
        Evaluate a value based on lists of enumerated values

        Args:
            value (str/num): Value to test
            defaultStatus (str): Result if value does not match any list
            okValues (List of str/num): Values to match for OK Status
            warningValues (List of str/num): Values to match for Warning Status
            criticalValues (List of str/num): Values to match for Critical Status
            unknownValues (List of str/num): Values to match for Unknown Status
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL,UNKNOWN)
        '''
        if value in unknownValues:
            self.errObj.addUnknown("{}value is {}{}".format(prefixText, value, postfixText))
            return("UNKNOWN")
        if value in criticalValues:
            self.errObj.addCritical("{}value is {}{}".format(prefixText, value, postfixText))
            return("CRITICAL")
        if value in warningValues:
            self.errObj.addWarning("{}value is {}{}".format(prefixText, value, postfixText))
            return("WARNING")
        if value in okValues:
            return("OK")
        if defaultStatus != "OK":
            self.errObj.addRecord(defaultStatus.lower(), "{}value {} not found{}".format(prefixText, value, postfixText))
        return(defaultStatus)
    

    def evalListNumberAsc(self, values, emptyStatus="UNKNOWN", warningAbove=None, criticalAbove=None, prefixText="", postfixText="", numberUnits=""):
        '''
        Evaluate a list of values based on ascending thresholds

        Args:
            values (List of num): Values to test
            emptyStatus (str): Result if values is an empty list
            warningAbove (num): Generate a warning if value is above this threshold
            criticalAbove (num): Generate a critical error if value is above this threshold
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports
            numberUnits (str): Units to append to numbers in error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL,UNKNOWN)
        '''
        if (type(values) == list and len(values) == 0) or (type(values) != list and values == ""):
            if emptyStatus != "OK":
                self.errObj.addRecord(emptyStatus.lower(),"{}list is Empty{}".format(prefixText, postfixText))
            return(emptyStatus)
        if type(values) != list:
            return self.evalNumberAsc(values, warningAbove, criticalAbove, prefixText, postfixText, numberUnits)

        ret = "OK"
        rvals = {"OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3}
        for value in values:
            r = self.evalNumberAsc(value, warningAbove, criticalAbove, prefixText, postfixText, numberUnits)
            if rvals[r] > rvals[ret]:
                ret = r
        return ret


    def evalNumberAsc(self, value, warningAbove=None, criticalAbove=None, prefixText="", postfixText="", numberUnits=""):
        '''
        Evaluate a number, generate warning or critical if above certain thresholds

        Args:
            value (num): Value to test
            warningAbove (num): Generate a warning if value is above this threshold
            criticalAbove (num): Generate a critical error if value is above this threshold
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports
            numberUnits (str): Units to append to numbers in error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL)
        '''
        if criticalAbove is not None and value > criticalAbove:
            self.errObj.addCritical("{}{}{} is > {}{}{}".format(prefixText, value, numberUnits, criticalAbove, numberUnits, postfixText))
            return("CRITICAL")
        if warningAbove is not None and value > warningAbove:
            self.errObj.addWarning("{}{}{} is > {}{}{}".format(prefixText, value, numberUnits, warningAbove, numberUnits, postfixText))
            return("WARNING")
        return("OK")
    

    def evalListNumberDesc(self, values, emptyStatus="UNKNOWN", warningBelow=None, criticalBelow=None, prefixText="", postfixText="", numberUnits=""):
        '''
        Evaluate a list of values based on descending thresholds

        Args:
            values (List of num): Values to test
            emptyStatus (str): Result if values is an empty list
            warningBelow (num): Generate a warning if value is below this threshold
            criticalBelow (num): Generate a critical error if value is below this threshold
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports
            numberUnits (str): Units to append to numbers in error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL,UNKNOWN)
        '''
        if (type(values) == list and len(values) == 0) or (type(values) != list and values == ""):
            if emptyStatus != "OK":
                self.errObj.addRecord(emptyStatus.lower(),"{}list is Empty{}".format(prefixText, postfixText))
            return(emptyStatus)
        if type(values) != list:
            return self.evalNumberDesc(values, warningBelow, criticalBelow, prefixText, postfixText, numberUnits)

        ret = "OK"
        rvals = {"OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3}
        for value in values:
            r = self.evalNumberDesc(value, warningBelow, criticalBelow, prefixText, postfixText, numberUnits)
            if rvals[r] > rvals[ret]:
                ret = r
        return ret

    def evalNumberDesc(self, value, warningBelow=None, criticalBelow=None, prefixText="", postfixText= "", numberUnits=""):
        '''
        Evaluate a number, generate warning or critical if below certain thresholds

        Args:
            value (num): Value to test
            warningBelow (num): Generate a warning if value is below this threshold
            criticalBelow (num): Generate a critical error if value is below this threshold
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports
            numberUnits (str): Units to append to numbers in error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL)
        '''
        if criticalBelow is not None and value < criticalBelow:
            self.errObj.addCritical("{}{}{} is < {}{}{}".format(prefixText, value, numberUnits, criticalBelow, numberUnits, postfixText))
            return("CRITICAL")
        if warningBelow is not None and value < warningBelow:
            self.errObj.addWarning("{}{}{} is < {}{}{}".format(prefixText, value, numberUnits, warningBelow, numberUnits, postfixText))
            return("WARNING")
        return("OK")

    def evalNumberRange(self, value, warningBelow=None, warningAbove=None, warningRange=None, criticalBelow=None, criticalAbove=None, criticalRange=None, prefixText="", postfixText= "", numberUnits=""):
        '''
        Evaluate a number, generate warning or critical if below certain thresholds

        Args:
            value (num): Value to test
            warningBelow (num): Generate a warning if value is below this threshold
            warningAbove (num): Generate a warning if value is above this threshold
            warningRange (numL:numH): Generate a warning if value is < numL or > numH
            criticalBelow (num): Generate a critical error if value is below this threshold
            criticalAbove (num): Generate a critical error if value is above this threshold
            criticalRange (numL:numH): Generate a critical error if value is < numL or > numH
            prefixText (str): String to prefix error reports
            postfixText (str): String to append to error reports
            numberUnits (str): Units to append to numbers in error reports

        Effects:
            self.errObj (NagErrors): Updated with error strings

        Returns:
            str: Result of test, One of (OK,WARNING,CRITICAL)
        '''

        if warningRange is not None:
            (wl, wh) = warningRange.split(":")
            if warningBelow is None:
                warningBelow = float(wl.replace(',', ''))
            if warningAbove is None:
                warningAbove = float(wh.replace(',', ''))
        if criticalRange is not None:
            (cl, ch) = criticalRange.split(":")
            if criticalBelow is None:
                criticalBelow = float(cl.replace(',', ''))
            if criticalAbove is None:
                criticalAbove = float(ch.replace(',', ''))

        if criticalBelow is not None and value < criticalBelow:
            self.errObj.addCritical("{}{}{} is < {}{}{}".format(prefixText, value, numberUnits, criticalBelow, numberUnits, postfixText))
            return("CRITICAL")
        if criticalAbove is not None and value > criticalAbove:
            self.errObj.addCritical("{}{}{} is > {}{}{}".format(prefixText, value, numberUnits, criticalAbove, numberUnits, postfixText))
            return("CRITICAL")
        if warningAbove is not None and value > warningAbove:
            self.errObj.addWarning("{}{}{} is > {}{}{}".format(prefixText, value, numberUnits, warningAbove, numberUnits, postfixText))
            return("WARNING")
        if warningBelow is not None and value < warningBelow:
            self.errObj.addWarning("{}{}{} is < {}{}{}".format(prefixText, value, numberUnits, warningBelow, numberUnits, postfixText))
            return("WARNING")
        return("OK")
