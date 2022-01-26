 # *********************************************************************
 # This Original Work is copyright of 51 Degrees Mobile Experts Limited.
 # Copyright 2019 51 Degrees Mobile Experts Limited, 5 Charlotte Close,
 # Caversham, Reading, Berkshire, United Kingdom RG4 7BY.
 #
 # This Original Work is licensed under the European Union Public Licence (EUPL) 
 # v.1.2 and is subject to its terms as set out below.
 #
 # If a copy of the EUPL was not distributed with this file, You can obtain
 # one at https://opensource.org/licenses/EUPL-1.2.
 #
 # The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
 # amended by the European Commission) shall be deemed incompatible for
 # the purposes of the Work and the provisions of the compatibility
 # clause in Article 5 of the EUPL shall not apply.
 # 
 # If using the Work as, or as part of, a network application, by 
 # including the attribution notice(s) required under Article 5 of the EUPL
 # in the end user terms of the application under an appropriate heading, 
 # such notice(s) shall fulfill the requirements of that article.
 # ********************************************************************

import gzip
import shutil
import os
import random
import threading
import time
import requests

# gzip decompress alternative for python 2

if not hasattr(gzip, "decompress"):
    from io import StringIO

class DataFileUpdateService():

    """!
    A data file update service is attached to a pipeline and manages
    the download of datafiles used by engines
    """


    def __init__(self, pipeline):
     
        """!
        Constructor for the DataFileUpdateService
        @type pipeline: Pipeline
        @param pipeline: The pipeline the datafile update service is attached to
        """
        
        self.pipeline = pipeline

    def update_data_file(self, data_file):

        """!
        Function to request, download, check and unzip a datafile from
        an update service via an HTTP request
        @type data_file: DataFile
        @param data_file: Datafile to update
        """

        # exit if already updating

        if data_file.updating:
            pass

        # Get the update url

        url = data_file.get_update_url()

        headers = {}

        # Add if modified since header if enabled and available
        if data_file.verify_if_modified_since:
            try:
                headers["If-Modified_since"] = str(data_file.get_date_published().timestamp())
            except:
                pass
    
        response = requests.get(url, headers=headers)

        if response.status_code != 200:

            # Handle errors

            if response.status_code == 429:
                self.pipeline.log("error", "Too many requests to " + url + "for engine " + data_file.flow_element.datakey)
            elif response.status_code == 304:
                self.pipeline.log("warn", "No data update available from " + url + "for engine " + data_file.flow_element.datakey)
        
            elif response.status_code == 403:
                self.pipeline.log("error", "Access denied from " + url + "for engine " + data_file.flow_element.datakey)
            else:
                self.pipeline.log("error", str(response.status_code) + url + "for engine " + data_file.flow_element.datakey)

            data_file.updating = False
            self.check_next_update(data_file)

            return False

        # Verify MD5 hash if enabled

        if data_file.verify_md5:
            header_md5 = response.headers["content-md5"]

            import hashlib
            hash_md5 = hashlib.md5()

            for data in response.iter_content(8192):
                hash_md5.update(data)
            
            if header_md5 != hash_md5.hexdigest():
                self.pipeline.log("error", "MD5 doesn't match from " + url + "for engine " + data_file.flow_element.datakey)

                data_file.updating = False
                self.check_next_update(data_file)

                return False

        data = response.content

        # Decompress if set
        if data_file.decompress:
            # Python 3 version
            if(hasattr(gzip, "decompress")):
                data = gzip.decompress(response.content)
            else:
                compressed_stream = StringIO(response.content)
                gzipper = gzip.GzipFile(fileobj=compressed_stream)
                data = gzipper.read()

        # Download datafile if needed, or pass through memory
        if data_file.download:

            if data_file.create_temp_copy:

                filename = data_file.temp_directory + "/" + data_file.identifier + str(time.time())
            
            else:

                filename = data_file.path

            with open(filename, 'wb') as f:
                f.write(data)

            if data_file.create_temp_copy:

                # Move to real file

                shutil.move(filename, data_file.path)

        else:

            data_file.data = data

        # If updating on start, cancel as done

        if data_file.update_on_start:
            data_file.updated_on_start = True

        # Done. Refresh the file.

        data_file.refresh()
        data_file.updating = False
        self.check_next_update(data_file)

        return True

    def async_update_data_file(self, data_file):

        """!
        Non blocking version of update_data_file
        @type data_file: DataFile
        @param data_file: Datafile to update
        """
        
        thread = threading.Thread(name="Update service", target=self.update_data_file, args=[data_file], daemon=True)
        thread.start()
        return thread
    
    def check_next_update(self, data_file):
        """!
        Function to periodically check if a datafile needs updating
        also updates the datafile on start if it is set with the update_on_start option
        @type data_file: DataFile
        @param data_file: Datafile to check updates for
        """

        if data_file.update_on_start and not data_file.updated_on_start:
            self.update_data_file(data_file)

        if data_file.auto_update:
   
            random_offset = random.randint(0, data_file.update_time_maximum_randomisation)

            interval = random_offset + data_file.polling_interval
            
            t = threading.Timer(interval, self.async_update_data_file, args=[data_file])
            t.daemon = True
            t.start()

    def register_data_file(self, data_file):
        """!
        Function to register a datafile with the update service
        @type data_file: DataFile
        @param data_file: Datafile to check updates for
        """

        data_file.registered = True

        if data_file.update_on_start or data_file.auto_update:
            self.check_next_update(data_file)

        # Watch for changes in file and refresh if
        # file_system_watcher is enabled on data_file

        if data_file.file_system_watcher:
            data_file.last_changed_time = os.stat(data_file.path).st_mtime
            self.track_local_data_file_changes(data_file)    


    def track_local_data_file_changes(self, data_file):
        """!
        Check for local changes to a datafile. Used by
        the file system watcher
        @type data_file: DataFile
        @param data_file: Datafile to check updates for
        """
        if os.stat(data_file.path).st_mtime > data_file.last_changed_time:
            # Don't change if data_file is updating
            if not data_file.updating:
                data_file.last_changed_time = os.stat(data_file.path).st_mtime
                data_file.refresh()
        t = threading.Timer(10, self.track_local_data_file_changes, args=[data_file])
        t.start()
