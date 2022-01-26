# Copyright 2019 Cognite AS

import os

if not os.getenv("READ_THE_DOCS"):
    from cognite.seismic.protos import types_pb2 as stypes


class API:
    def __init__(self, query=None, ingestion=None):
        self.query = query
        self.ingestion = ingestion

    @staticmethod
    def identify(thing_id=None, thing_name=None):
        """
        Returns an identifier with filled with id or name. If both are filled, will prefer id.
        """
        if not thing_id and not thing_name:
            raise Exception("Either `thing_name` or `thing_id` needs to be specified")
        return stypes.Identifier(id=thing_id) if thing_id else stypes.Identifier(name=thing_name)
