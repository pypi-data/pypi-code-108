#-------------------------------------------------------------------------
#
# Copyright (c) 2009, IMB, RWTH Aachen.
# All rights reserved.


from os.path import \
    join
import os.path
import platform
import os
from traits.api import \
    HasTraits, Property, Str, Constant
from traits.util.home_directory import \
    get_home_directory
if platform.system() == 'Linux':
    pathchar = '/'
elif platform.system() == 'Windows':
    pathchar = '\\'


class DataCache(HasTraits):
    '''
Basic structure of the database directory.
Implements the relative paths for the three different
categories of data that are managed using the svn server.
'''
    home_dir = Property

    def _get_home_dir(self):
        return get_home_directory()

    dir = Property

    def _get_dir(self):
        dir_path = join(self.home_dir, 'bmcs_cache')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

data_cache = DataCache()