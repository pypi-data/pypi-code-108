import os
import time
import threading

class TelemetryLogMonitor:

    def __init__(self, ct_instance):
        self.showWarning = True
        self.ct_instance = ct_instance

    # Limit in kilobytes
    def isWithinLimit(self, filename, limit):
        try:
            filesize = os.path.getsize(filename)/1024
            if (filesize > limit):
                if (self.showWarning):
                    print ("Logfile size is too large. Disabling telemetry.")
                    print ("Filesize: " + str(filesize))
                    print ("Limit: " + str(limit))
                    self.ct_instance.telemetry_enabled = False
                self.showWarning = False
        except OSError:
            # If file doesn't exist, we'll create a new one
            pass
        # Else if telemetry disabled enable it again?

    def monitorLogFileSize(self, filename, limit, interval):
        while (True):
            #print("Monitoring logfile " + filename + " " + str(limit) + " " + str(interval) )
            self.isWithinLimit (filename, limit)
            time.sleep(interval)

    def start(self, filename, limit, interval):
        try:
            logmonitor_thread = threading.Thread(target=self.monitorLogFileSize, args=[filename, limit, interval])
            logmonitor_thread.daemon = True
            logmonitor_thread.start()
        except (KeyboardInterrupt, SystemExit):
            cleanup_stop_thread()
            sys.exit()
