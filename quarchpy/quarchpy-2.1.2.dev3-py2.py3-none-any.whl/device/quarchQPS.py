from quarchpy.device import quarchDevice
from quarchpy.qps import toQpsTimeStamp
import os, time, datetime, sys, logging

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

current_milli_time = lambda: int (round (time.time() * 1000))
current_second_time = lambda: int (round (time.time()))

# Using standard Unix time,  milliseconds since the epoch (midnight 1 January 1970 UTC)
# Should avoid issues with time zones and summer time correction but the local and host
# clocks should still be synchronised
def qpsNowStr():
    return current_milli_time()                          # datetime supports microseconds


class quarchQPS(quarchDevice):
    def __init__(self, quarchDevice):

        self.quarchDevice = quarchDevice
        self.ConType = quarchDevice.ConType
        self.ConString = quarchDevice.ConString

        self.connectionObj = quarchDevice.connectionObj
        self.IP_address = quarchDevice.connectionObj.qps.host
        self.port_number = quarchDevice.connectionObj.qps.port

    def startStream(self, directory):
        time.sleep(1) #TODO remove this sleep once script->QPS timeing issue resolved. This works fine in the meantime
        return quarchStream(self.quarchDevice, directory)
    

class quarchStream(quarchQPS):
    def __init__(self, quarchQPS, directory):
        self.connectionObj = quarchQPS.connectionObj
        
        self.IP_address = quarchQPS.connectionObj.qps.host
        self.port_number = quarchQPS.connectionObj.qps.port

        self.ConString = quarchQPS.ConString
        self.ConType = quarchQPS.ConType
        
        time.sleep(1)
      
        #check to see if any invalid file entries
        newDirectory = self.failCheck(directory)
        
    def failCheck(self, newDirectory):
        validResponse = False

        while (validResponse == False):
            #send the command to start stream
            response = self.connectionObj.qps.sendCmdVerbose( "$start stream " + str(newDirectory))
            #if the stream fails, loop until user enters valid name
            if "Fail" in response: #TODO should check when this fail is not a path name issue
                print (response)
                print("Please enter a new file name:")
                #grab directory bar end file / folder
                path = os.path.dirname(newDirectory)
                #get a new file name
                if sys.version_info.major==3:                    
                    newEnd = input()
                else:
                    newEnd = raw_input()
                #append user input to directory
                newDirectory = path.replace("\\\\","\\") + newEnd
            else:
                validResponse = True;
        return newDirectory

    def get_stats(self):
        """
                      Returns the QPS annotation statistics grid information as a pandas dataframe object

                                  Returns
                                  -------
                                  df = : dataframe
                                      The response text from QPS. If successful "ok. Saving stats to : file_name" otherwise returns the exception thrown
        """
        try:
            import warnings
            warnings.simplefilter(action='ignore', category=FutureWarning)
            import pandas as pd
            pd.set_option('max_columns', None)
            pd.set_option('display.width', 1024)
        except:
            logging.warning("pandas not imported correctly")
            pass
        time.sleep(1) #TODO remove this sleep, Test if this is still needed, it was put in because re
        command_response = self.connectionObj.qps.sendCmdVerbose("$get stats", timeout=60)
        if command_response.startswith("Fail"):
            raise Exception(command_response)
        test_data = StringIO(command_response)
        df = pd.read_csv(test_data, sep=",", header=[0,1], error_bad_lines=False)

        #TODO trailing "/n" around 200 annotations is causing error hence this extra arg. Task: investigate trailing "\n", fix it, and remove this arg.
        return df

    def stats_to_CSV(self, file_name=""):
        """
        Saves the statistics grid to a csv file

                    Parameters
                    ----------
                    file-name= : str, optional
                        The absolute path of the file you would like to save the csv to. If left empty then a filename will be give.
                        Default location is the path of the executable.
                    Returns
                    -------
                    command_response : str or None

                        The response text from QPS. If successful "ok. Saving stats to : file_name" otherwise returns the exception thrown
        """
        command_response = self.connectionObj.qps.sendCmdVerbose("$stats to csv \""+file_name+"\"", timeout=60)
        if command_response.startswith("Fail"):
            raise Exception(command_response)
        return command_response

    def get_custom_stats_range(self, start_time, end_time):
        """
                      Returns the QPS statistics information over a specific time ignoring any set annotations.

                                Parameters
                                ----------
                                start_time = : str
                                    The time in seconds you would like the stats to start this can be in integer or sting format.
                                    or using the following format to specify daysDhours:minutes:seconds.milliseconds
                                    xxxDxx:xx:xx.xxxx
                                end_time = : str
                                    The time in seconds you would like the stats to stop this can be in integer or sting format
                                    or using the following format to specify daysDhours:minutes:seconds.milliseconds
                                    xxxDxx:xx:xx.xxxx
                                Returns
                                -------
                                df = : dataframe
                                    The response text from QPS. If successful "ok. Saving stats to : file_name" otherwise returns the exception thrown
        """
        try:
            import warnings
            warnings.simplefilter(action='ignore', category=FutureWarning)
            import pandas as pd
            pd.set_option('max_columns', None)
            pd.set_option('display.width', 1024)
        except:
            logging.warning("pandas not imported correctly")
            pass
        command_response = self.connectionObj.qps.sendCmdVerbose("$get custom stats range " + str(start_time)+ " " + str(end_time), timeout=60)
        if command_response.startswith("Fail"):
            raise Exception(command_response)
        test_data = StringIO(command_response)
        try:
            df = pd.read_csv(test_data, sep=",", header=[0,1])
        except Exception as e:
            logging.error("Unable to create pandas data frame from command response :" + str(command_response))
            raise e
        return df

    def takeSnapshot(self):
        """
                      Triggers QPS take snapshot function and saves it in the streams directory.
        """
        command_response = self.connectionObj.qps.sendCmdVerbose("$take snapshot")
        if command_response.startswith("Fail"):
            raise Exception(command_response)
        return(command_response)
        
    def addAnnotation(self, title, annotationTime = 0, extraText="", yPos="", titleColor ="", annotationColor = "", annotationType = "", annotationGroup =""):
        """
                    Adds a custom annotation to stream with given parameters.

                    Parameters
                    ----------
                    title= : str
                        The title appears next to the annotation in the stream
                    extraText= : str, optional
                        The additional text that can be viewed when selecting the annotation
                    yPos : str, optional
                        The percetange of how high up the screen the annotation should appear 0 is the bottom and 100 the top
                    titleColor : str, optional
                        The color of the text next to the annotation in hex format 000000 to FFFFFF
                    annotationColor : str, optional
                        The color of the annotation marker in hex format 000000 to FFFFFF
                    annotationGroup : str, optional
                        The group the annotation belongs to
                    annotationTime : int, optional
                        The time in milliseconds after the start of the stream at which the annotation should be placed. 0 will plot the annotation live at the most recent sample

                    Returns
                    -------
                    command_response : str or None

                        The response text from QPS. "ok" if annotation successfully added
            """
        annotationTime = str(annotationTime)
        annotationType = annotationType.lower()
        if annotationType == "" or annotationType == "annotation":
            annotationType = "annotate"
        elif annotationType == "comment":
            pass # already in the correct format for command
        else:
            retString = "Fail annotationType must be 'annotation' or 'comment'"
            logging.warning(retString)
            return retString

        # If the function has already been passed the XML string to give to QPS
        if ("<<" in title.replace(" ", "")):
            annotationString = str(title)
        else:
            annotationString = "<"

            if annotationTime == "0":
                # Use current time
                annotationTime = qpsNowStr()
            elif(annotationTime.startswith("e")):
                pass
            else:
                # Convert timestamp to QPS format
                annotationTime = toQpsTimeStamp(annotationTime)

            if title != "":
                annotationString += "<text>" + str(title) + "</text>"
            if extraText != "":
                annotationString += "<extraText>" + str(extraText) + "</extraText>"
            if yPos != "":
                annotationString += "<yPos>" + str(yPos) + "</yPos>"
            if titleColor != "":
                annotationString += "<textColor>" + str(titleColor) + "</textColor>"
            if annotationColor != "":
                annotationString += "<color>" + str(annotationColor) + "</color>"
            if annotationGroup != "":
                annotationString += "<userType>" + str(annotationGroup) + "</userType>"
            annotationString += ">"

        # command is sent on newline so \n needs to be chnaged to \\n which is changed back just before printing in qps.
        annotationString = annotationString.replace("\n", "\\n")
        logging.debug("Time sending to QPS:" + str(annotationTime))
        return self.connectionObj.qps.sendCmdVerbose("$" +annotationType+" "+str(annotationTime)+" "+annotationString)

    def addComment(self, title, commentTime = 0, extraText="", yPos="", titleColor ="", commentColor = "", annotationType = "", annotationGroup =""):
        #Comments are just annotations that do not affect the statistics grid.
        #This function was kept to be backwards compatible and is a simple pass through to add annotation.
        if annotationType == "":
            annotationType = "comment"
        return self.addAnnotation(title = title, annotationTime=commentTime, extraText=extraText, yPos=yPos, titleColor=titleColor, annotationColor=commentColor, annotationType=annotationType, annotationGroup=annotationGroup)

    def saveCSV(self,filePath, linesPerFile=None, cr=None, delimiter=None):
        """
            Saves the stream to csv file at specified location

            Parameters
            ----------
            filePath= : str
                The file path that ou would like the CSV file saved to.
            linesPerFile= : str, optional
                    The number of lines per CSV file. Can be any int number or "all"
            cr : bool, optional
                Whether the end of line terminator should include a carriage return.
            delimiter : str, optional
                The delimiter to be used by the csv file.

            Returns
            -------
            command_response : str or None
                The response text from QPS. "ok" if command is successful or the stack trace if exception thrown
        """
        args = ""

        if linesPerFile != None:
            args +=" -l" + str(linesPerFile)
        if cr !=None:
            if cr is True:
                args+= " -cyes"
            elif cr is False:
                args += " -cno"
        if delimiter !=None:
            args += " -s"+delimiter

        #, filePath, linesPerFile, cr, delimiter
        return self.connectionObj.qps.sendCmdVerbose("$save csv \"" + filePath + "\" " + args, timeout=60)

    def createChannel(self, channelName, channelGroup, baseUnits, usePrefix):
        #Conditions to convert false / true inputs to specification input
        if usePrefix == False: 
            usePrefix = "no"
        if usePrefix == True:
            usePrefix = "yes"

        return self.connectionObj.qps.sendCmdVerbose("$create channel " + channelName + " " + channelGroup  + " " + baseUnits + " " + usePrefix)

    def hideChannel(self, channelSpecifier):
        return self.connectionObj.qps.sendCmdVerbose("$hide channel " + channelSpecifier)

    def showChannel(self, channelSpecifier):
        return self.connectionObj.qps.sendCmdVerbose("$show channel " + channelSpecifier)

    def myChannels(self):
        return self.connectionObj.qps.sendCmdVerbose("$channels")

    def channels(self):
        return self.connectionObj.qps.sendCmdVerbose("$channels").splitlines()
             
    def stopStream(self):
        return self.connectionObj.qps.sendCmdVerbose("$stop stream")

    def hideAllDefaultChannels(self):
    	
    	#TODO query QPS / Device for all channel names and hide all of them
    	#All Default Channels
        self.hideChannel ("3.3v:voltage")
        self.hideChannel ("3v3:voltage")
        self.hideChannel ("5v:voltage")
        self.hideChannel ("12v:voltage")
        self.hideChannel ("3v3:current")
        self.hideChannel ("3.3v:current")
        self.hideChannel ("5v:current")
        self.hideChannel ("12v:current")
        self.hideChannel ("3v3:power")
        self.hideChannel ("3.3v:power")
        self.hideChannel ("5v:power")
        self.hideChannel ("12v:power")
        self.hideChannel ("tot:power")
        #Default PAM channels
        self.hideChannel ("perst#:digital")
        self.hideChannel ("wake#:digital")
        self.hideChannel ("lkreq#:digital")
        self.hideChannel ("smclk:digital")
        self.hideChannel ("smdat:digital")
    
    #function to add a data point the the stream
    #time value will default to current time if none passed
    def addDataPoint(self, channelName, groupName, dataValue, dataPointTime = 0):
        if dataPointTime == 0:
            dataPointTime = qpsNowStr()
        else:
            dataPointTime = toQpsTimeStamp (dataPointTime)

        #print ("printing command:  $log " + channelName + " " + groupName + " " + str(dataPointTime) + " " + str(dataValue))
        self.connectionObj.qps.sendCmdVerbose("$log " + channelName + " " + groupName + " " + str(dataPointTime) + " " + str(dataValue))