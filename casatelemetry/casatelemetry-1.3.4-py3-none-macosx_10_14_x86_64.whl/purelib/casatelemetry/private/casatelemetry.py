import os
import fnmatch
import subprocess
import tarfile
import datetime
import time
import urllib.request
import urllib.error
import casatools
import casatasks
from casatelemetry import CrashReporter
import casatelemetry.private.TelemetryLogMonitor as TelemetryLogMonitor
import ssl
import logging
import sys
      
class telemetry:

    def __init__(self, logdir_in=None):

        from pathlib import Path
        home = str(Path.home())
        self.casalogger = casatools.logsink()
        self.setCasaVersion()
        self.setHostId()
        self.telemetry_enabled = True
        casa_util = casatools.utils.utils()
        if logdir_in == None:
            self.logdir = home +"/.casa"
            # Check if user has defined a telemetry log location
            if (casatasks.config.telemetry_log_directory != None):
                self.logdir = casatasks.config.telemetry_log_directory
        else:
            self.logdir = os.path.abspath(os.path.expanduser(logdir_in))
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        self.variantSuffix = ""
        #if len(casa['variant'])>1:
        #    self.variantSuffix = "-" + casa['variant']
        self.logpattern = 'casastats-' + self.casaver + '-' + self.hostid + '*' + self.variantSuffix + '.log'
        self.sendlogpattern = 'casastats-*'+ self.hostid + '*.log'
        self.stampfile = self.logdir + '/telemetry-' + self.hostid + '.stamp'
        #self.logfile = 'casastats-' + self.casaver + '-' + self.hostid + self.variantSuffix + '.log'
        #self.casa = casa
     
        logfiles = []

       
        for file in os.listdir(self.logdir):
            if fnmatch.fnmatch(file, self.logpattern):
                 #print ("Matched: " + file)
                 logfiles.append(file)

        logfiles.sort(reverse=True)
        # Size of the existing (non-active) logfiles
        inactiveTLogSize = 0

        if (logfiles and logfiles[0] != None):
            self.casalogger.post ("Found an existing telemetry logfile: " + self.logdir  + "/" + logfiles[0])
            self.logfile= self.logdir  + "/" + logfiles[0]
            for i in range(1, len(logfiles)):
                inactiveTLogSize = inactiveTLogSize + os.path.getsize(self.logdir  + "/" + logfiles[i])/1024
                #print ("Inactive log size: " + str(inactiveTLogSize))
            self.init_log_file()
        else :
            print ("Creating a new telemetry file")
            self.setNewTelemetryFile()



        # Setup Telemetry log size monitoring
        # Size limit for the telemetry logs
        tLogSizeLimit = 20000
        # File size check interval
        tLogSizeInterval = 60
        
        if (casatasks.config.telemetry_log_limit != None):
            tLogSizeLimit = int(casatasks.config.telemetry_log_limit)
            self.casalogger.post("tLogSizeLimit: " + str(tLogSizeLimit))
        if (casatasks.config.telemetry_log_size_interval != None):
            tLogSizeInterval = int(casatasks.config.telemetry_log_size_interval)
            self.casalogger.post("tLogSizeInterval: " + str(tLogSizeInterval))
         
        # Subtract the inactive log sizes from the total log file size limit
        tLogSizeLimit = tLogSizeLimit - inactiveTLogSize
        #print("tLogSizeLimit " + str(tLogSizeLimit))
        if (tLogSizeLimit <= 0):
            print ("Telemetry log size limit exceeded. Disabling telemetry.", file=sys.stderr)
            self.telemetry_enabled = False
        else :
            tLogMonitor = TelemetryLogMonitor.TelemetryLogMonitor(ct_instance=self)
            tLogMonitor.start(self.logfile,tLogSizeLimit, tLogSizeInterval)
            if self.telemetry_enabled:
                print ("Telemetry initialized. Telemetry will send anonymized usage statistics to NRAO.", file=sys.stderr)
                print ('You can disable telemetry by adding the following line to the config.py file in your rcdir (e.g. ~/.casa/config.py):', file=sys.stderr)
                print ('telemetry_enabled = False', file=sys.stderr)

    def setNewTelemetryFile(self):
         try:
            self.logger.removehandler(self.loghandler)
         except:
            pass
         self.logfile =  self.logdir + '/casastats-' + self.casaver +'-'  + self.hostid + "-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + self.variantSuffix + '.log'
         self.init_log_file()

    def init_log_file(self):
         try:
            self.casalogger.post("Telemetry log file: " + self.logfile)
            self.logger = logging.getLogger('log')
            self.logger.setLevel(logging.INFO)
            self.loghandler = logging.FileHandler(self.logfile)
            self.loghandler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(self.loghandler)
         except:
            self.casalogger.post("Telemetry log is not writeable.")
            pass
      
    def setCasaVersion(self):
        self.casaver = casatasks.version_string() # str(ver[0])+ str(ver[1]) + str(ver[2])+ "-" + str(ver[3])

    def setHostId(self):
        telemetryhelper = CrashReporter.CrashReportHelper()
        self.hostid = telemetryhelper.getUniqueId()

    #def setCasaLog(self, logger):
    #    self.logger = logger

    def submitStatistics(self):
        #if (self.casa['state']['telemetry-enabled'] == True):
            self.casalogger.post("Checking telemetry submission interval")
            self.createStampFile()
            if (self.isSubmitInterval()):
                postingUrl = 'https://casa.nrao.edu/cgi-bin/crash-report.pl'
                if 'CASA_CRASHREPORT_URL' in os.environ:
                    postingUrl = os.environ['CASA_CRASHREPORT_URL']
                self.send(postingUrl)
                self.refreshStampFile()
                self.setNewTelemetryFile()


    def isSubmitInterval(self):
        currentTime = time.time()
        lastUpdateTime = time.time()
        if (os.path.isfile(self.stampfile)):
            lastUpdateTime = os.path.getmtime(self.stampfile)

        # Check update checkSubmitInterval
        interval = 604800
        utils = casatools.utils.utils()
        if (casatasks.config.telemetry_submit_interval != None):
            interval = float(casatasks.config.telemetry_submit_interval)
        if ((currentTime - lastUpdateTime)> interval):
            self.casalogger.post("Telemetry submit interval reached, submitting telemetry data.")
            return True
        else:
            self.casalogger.post("Telemetry submit interval not reached. Not submitting data.")
            #print "lastUpdateTime" +str(lastUpdateTime)
            #print "currentTime" +str(currentTime)
            self.casalogger.post("Next telemetry data submission in: " + str(datetime.timedelta(  \
                    seconds=(interval-(currentTime-lastUpdateTime)))))
            return False

    def createStampFile(self):
        #print "Checking for stampfile " + self.stampfile
        if not os.path.isfile(self.stampfile):
            self.casalogger.post("Creating a new telemetry time stamp file." + self.stampfile)
            open(self.stampfile, 'a').close()

    def refreshStampFile(self):
        os.utime(self.stampfile, None)

    def send(self, telemetry_url):

        telemetryhelper = CrashReporter.CrashReportHelper()
        logfiles = []

        # Test if internet connection is available.
        context = ssl._create_unverified_context()
        try:
            urllib.request.urlopen('https://casa.nrao.edu/', timeout=20, context=context)
        except urllib.error.URLError as err:
            self.casalogger.post("No telemetry server available. Not submitting data")
            return

        # Find logfiles
        for file in os.listdir(self.logdir):
            if fnmatch.fnmatch(file, self.sendlogpattern):
                #print "Matched: " + file
                logfiles.append(file)

        if (len(logfiles) > 0):
            #Tar logfiles
            current_date = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            tarfileid = self.logdir + "/telemetry-" \
                            + telemetryhelper.getUniqueId() + "-" \
                            + current_date + ".tar.gz"
            try:
                tar = tarfile.open(tarfileid, "w:gz")
                for logfile in logfiles:
                    tar.add(self.logdir + "/" + logfile,
                            arcname='telemetry/'+logfile)
                tar.close()
            except Exception as e:
                self.casalogger.post("Couldn't create telemetry tarfile")
                self.casalogger.post(str(e))

            try:
                file_param = 'file=@' + tarfileid #+ '\"'
                # Submit tarfile
                #self.casalogger.post ['curl', '-F', file_param , telemetry_url]
                proc = subprocess.Popen(['curl', '-F', file_param , telemetry_url],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                cmd_out, cmd_err = proc.communicate()
                if cmd_out != None:
                    self.casalogger.post(cmd_out)
                    self.casalogger.post(cmd_out, 'DEBUG1')
                if cmd_err != None:
                    self.casalogger.post(cmd_err)
                    self.casalogger.post(cmd_err, 'DEBUG1')
            except Exception as e:
                self.casalogger.post("Couldn't submit telemetry logs")
                self.casalogger.post(str(e))

            # Remove files
            for logfile in logfiles:
                try:
                    os.remove(self.logdir + "/" + logfile)
                except Exception as e:
                    self.casalogger.post("Couldn't remove logfile " + self.logdir + "/" + logfile)
                    self.casalogger.post(str(e))
                    #print "Removed " + self.logdir + "/" + logfile
            try:
                os.remove(tarfileid)
                self.casalogger.post("Removed" + tarfileid)
            except Exception as e:
                self.casalogger.post("Couldn't remove  " + tarfileid)
                self.casalogger.post(str(e))
        else:
             self.casalogger.post("No telemetry files to submit.")
