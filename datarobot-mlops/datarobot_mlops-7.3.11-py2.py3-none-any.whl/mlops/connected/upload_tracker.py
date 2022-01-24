#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import datetime
import json
import os


class MLOpsUploadTracker:
    DEFAULT_STATUS_FILENAME = "./upload_status.json"

    def __init__(self, status_filename=DEFAULT_STATUS_FILENAME):
        self._status_filename = status_filename
        self._row_count_uploaded_successfully = 0
        self._iteration = 1
        self._spooler = None
        if os.path.exists(self._status_filename):
            with open(self._status_filename) as status_file:
                status = json.load(status_file)
                self._row_count_uploaded_successfully = status["row_count"]
                self._iteration = status["iteration"] + 1
                if "spooler" in status:
                    self._spooler = status["spooler"]

        print("Using status file: '{}'".format(self._status_filename))
        if self._spooler is not None:
            print("Setting spooler configuration found in status file")
            self._setup_spooler()

    def _setup_spooler(self):
        # Because we are using the same key names, we can simply loop around the dict
        for key, value in self._spooler.items():
            if value is not None:
                print("Setting Spooler config '{}' to value '{}'".format(key, value))
                os.environ[key] = str(value)

    def get_status(self):
        print("Returning skipped rows count: {}".format(self._row_count_uploaded_successfully))
        return self._row_count_uploaded_successfully, self._iteration

    def save_spooler(self, spooler):
        self._spooler = spooler.__dict__()

    def update_status(self, row_count, iteration):
        self._row_count_uploaded_successfully = row_count
        status = {
            "row_count": row_count,
            "iteration": iteration,
            "time": datetime.datetime.now().isoformat()
        }
        if self._spooler:
            status["spooler"] = self._spooler
        with open(self._status_filename, "w") as status_file:
            json.dump(status, status_file)

    def get_status_file(self):
        return self._status_filename
