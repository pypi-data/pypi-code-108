# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from io import BytesIO

class Client(object):
    """
    This is a stream module
    """
    def __init__(self):
        pass

    @staticmethod
    def read_from_file_path(path):
        return open(path, 'rb')

    @staticmethod
    def read_from_bytes(raw):
        f = BytesIO()
        f.write(raw)
        return f

    @staticmethod
    def read_from_string(raw):
        by = bytes(raw, 'utf-8')
        f = BytesIO()
        f.write(by)
        return f

    @staticmethod
    def reset(raw):
        raise Exception('Un-implemented')
