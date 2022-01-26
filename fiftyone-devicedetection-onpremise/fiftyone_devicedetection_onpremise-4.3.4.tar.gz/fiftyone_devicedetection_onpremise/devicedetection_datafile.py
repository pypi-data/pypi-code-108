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
# *********************************************************************/

from __future__ import absolute_import
from fiftyone_pipeline_engines.datafile import DataFile

import datetime

try:
    #python2
    from urllib import urlencode
except ImportError:
    #python3
    from urllib.parse import urlencode

class DeviceDetectionDataFile(DataFile):

    """!
    Extension of the DataFile class for DeviceDetection
    This helps construct the update url based on url parameters provided
    by the engine, provides methods to get the published date and
    update date of the datafile and refreshes the on premise 
    engine when the datafile is updated. 
    """

    def get_url_formatter(self):

        """!
        Generate a url for the data file update service to call
        These parameters are passed in to the constructor of the
        Device Detection On Premise engine
        @returns string : URL
        """

        query_params = {
            "Type": self.update_url_params["type"]
        }

        if ("license_keys" in self.update_url_params):
            query_params["licenseKeys"] = self.update_url_params["license_keys"]

        return self.update_url_params["base_url"] + '?' + urlencode(query_params)

    def swig_date_to_date(self, swig_date):

        """!
        Helper function to convert the SWIG wrapper date object
        into a python date
        @returns date
        """

        return datetime.datetime.strptime(str(swig_date.getYear()) + "-" + str(swig_date.getMonth()) + "-" + str(swig_date.getDay()), "%Y-%m-%d")
    
    def get_date_published(self):

        """!
        Get the date the datafile was published
        @returns date
        """
        
        if self.flow_element.engine:
            return self.swig_date_to_date(self.flow_element.engine.getPublishedTime())
        else:
            return datetime.date.now()

    def get_next_update(self):

        """!
        Get the date of the next datafile update
        @returns date
        """

        if self.flow_element.engine:
            return self.swig_date_to_date(self.flow_element.engine.getUpdateAvailableTime())
        else:
            return datetime.date.now()

    def refresh(self):

        """!
        Once the datafile has updated, refresh the engine
        """

        if not hasattr(self.flow_element, "engine"):
            self.flow_element.init_engine()
        
        if self.download == False:
            self.flow_element.engine.refreshDataFromMemory(self.data)
        else:
            self.flow_element.engine.refreshData()
