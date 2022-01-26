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

import tempfile
import datetime

class DataFile():
     
    """!
    
    A datafile used by a FlowElement / Engine to get calculate properties values

    """

    def __init__(self, flow_element, identifier, update_url_params = None, data = None, path = "", temp_directory = tempfile.gettempdir(), create_temp_copy = True, auto_update = True, file_system_watcher = True, polling_interval = 30, update_time_maximum_randomisation = 10, verify_md5 = True, decompress = True, download = True, verify_if_modified_since = True, update_on_start = False):

        """!
            
        Constructor for a DataFile.
        @type flow_element: FlowElement
        @param flow_element: The FlowElement using the datafile
        @type identifier : string
        @param identifier : Name of the datafile
        @type update_url_params: dict
        @param update_url_params: Dictionary containing parameters used to
        construct the datafile update url
        @type data: mixed
        @param data: Data to use in the datafile if kept in memory rather than file
        @type path: string
        @param path: path to the data file itself
        @type temp_directory: string
        @param temp_directory: temporary file location (defaults to the operating system defualt)
        @type create_temp_copy: bool
        @param create_temp_copy: whether to copy datafile to temporary location when updating
        @type auto_update: bool
        @param: auto_update: whether to automatically update the datafile when required
        @type file_system_watcher: bool
        @param file_system_watcher: whether to check the datafile's path for changes and update the connected FlowElement's data automatically when the file is changed in the operating system
        @type polling_interval: int
        @param polling_interval: How often to poll for updates to the datafile (minutes)
        @type update_time_maximum_randomisation : int
        @param update_time_maximum_randomisation :
        Maximum randomisation offset in seconds to polling time interval
        @type verify_md5 : bool
        @param verify_md5 : whether to check a 'content-md5' header in the data file update service against the datafile to verify its contents
        @type decompress: bool
        @param: is the datafile gziped when returning from the update service?
        @type download: bool
        @param download: should the datafile be downloaded or stored in memory
        @type update_on_start : bool
        @param update_on_start : When this is set to true the datafile is updated / downloaded immediately on initialisation. This is useful if no initial datafile is present.
        @type verify_if_modified_since : bool
        @param verify_if_modified_since : whether to check an "If-Modified-Since" header on the update service against the last datafile update date
            
        """

        #  Set values on data file object

        self.flow_element = flow_element
        self.identifier = identifier
        if update_url_params is None:
            update_url_params = {}
        else:
            self.update_url_params = update_url_params
        self.temp_directory = temp_directory
        self.create_temp_copy = create_temp_copy
        self.auto_update = auto_update
        self.file_system_watcher = file_system_watcher
        self.polling_interval = polling_interval
        self.update_time_maximum_randomisation = update_time_maximum_randomisation
        self.verify_md5 = verify_md5
        self.decompress = decompress
        self.download = download
        self.verify_if_modified_since = verify_if_modified_since
        self.update_on_start = update_on_start

        # If update on start mode is set, we need a flag to stop
        # it forever looping and updating.
        if self.update_on_start:
            self.updated_on_start = False

        # Check if in memory only or if path is provided

        if data:
            self.data = data
        elif path:
            self.path = path
        else:
            raise Exception("You must provide either a file system path or data for the datafile")

        # Flag for whether the datafile is currently being updated
        self.updating = False

    def get_date_published(self):
        """!
        Function called to get the date the datafile was published
        @returns date: Date the datafile was published
        """
        return datetime.date.today()

    def get_next_update(self):
        """!
        Function called to get the date of the next datafile version
        @returns date: Date of the next update
        """
        return datetime.date.today()

    def refresh(self, identifier):
        """!
        Function called when datafile has been updated.
        Defaults to a refresh method on the attached FlowElement
        @type identifier : string
        @param identifier : identifier of the datafile
        """
        self.flow_element.refresh(identifier)

    def get_update_url(self):
        """!
        Internal function that constructs the url for the datafile update service to use from the result of get_url_formatter
        """
        return self.get_url_formatter()
    
    def get_url_formatter(self):
        """!
        Function that constructs the url for the datafile update service to use
        """
        return self.update_url_params.url
