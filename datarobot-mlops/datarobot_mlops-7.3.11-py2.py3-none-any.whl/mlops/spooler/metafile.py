#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
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

import io
import json

"""
Metafile class is spooler helper.
It was decided not to use it for enqueue purposes.
"""


class Metafile(object):
    FILENAME_ATTRIBUTE_NAME = "filename"
    OFFSET_ATTRIBUTE_NAME = "offset"

    def __init__(self, filename, offset):
        setattr(self, Metafile.FILENAME_ATTRIBUTE_NAME, filename)
        setattr(self, Metafile.OFFSET_ATTRIBUTE_NAME, offset)

    def get_filename(self):
        return getattr(self, Metafile.FILENAME_ATTRIBUTE_NAME)

    def get_offset(self):
        return getattr(self, Metafile.OFFSET_ATTRIBUTE_NAME)

    def to_json(self):
        # Force output of unicode string, because io.write requires unicode string.
        return u"{}".format(json.dumps(self.__dict__, ensure_ascii=False))

    def dump_to_file(self, filename):
        with io.open(filename, "w", encoding="utf8") as f:
            f.write(self.to_json())

    @staticmethod
    def read_from_file(filename):
        with io.open(filename, "r", encoding="utf8") as f:
            json_s = f.read()
            json_o = json.loads(json_s)
            return Metafile(json_o.get(Metafile.FILENAME_ATTRIBUTE_NAME),
                            json_o.get(Metafile.FILENAME_ATTRIBUTE_NAME))
