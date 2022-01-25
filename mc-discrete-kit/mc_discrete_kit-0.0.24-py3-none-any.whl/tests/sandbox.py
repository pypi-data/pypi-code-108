"""This  module is for testing function on developing"""

from discrete_kit.functions import metadata_convertor as ms

import os
import glob
directory = '/home/ronenk1/Downloads/testing/1/'
glob.glob('./*.*')
# ms.change_resolution_value('test12345', '/home/ronenk1/Downloads/testing/1/tiff/O_arzi_mz_w84geo_Apr19_tiff_0.2.tfw')
ms.replace_discrete_resolution(directory, 'test123')

# some temporary note change