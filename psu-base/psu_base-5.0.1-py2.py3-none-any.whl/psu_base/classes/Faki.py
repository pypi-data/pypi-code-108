from django.conf import settings
from psu_base.classes.Log import Log
from psu_base.models.faki import FakiResponse
from psu_base.services import message_service
import requests
import hashlib
import json

log = Log()


class Faki:
    path = None
    method = None

    parameters = None
    payload = None
    headers = None

    db_parameters = None
    db_payload = None
    db_headers = None
    db_hash = None

    instance = None

    def __init__(self, path, method, parameters=None, payload=None, headers=None):
        self.path = path
        self.method = method
        self.parameters = parameters
        self.payload = payload
        self.headers = headers

        # Data will be stored as JSON in the database
        self.db_parameters = json.dumps(self.parameters) if self.parameters else None
        self.db_payload = json.dumps(self.payload) if self.payload else None
        self.db_headers = json.dumps(self.headers) if self.headers else None

        # For convenience, a hash of all the things will be used to lookup existing records
        hash_str = f"{self.path}.{self.method}.{self.db_parameters}.{self.db_payload}.{self.db_headers}"
        self.db_hash = hashlib.md5(hash_str.encode("utf-8")).hexdigest()
        del hash_str

        self.retrieve()

    def retrieve(self):
        queryset = FakiResponse.objects.filter(hash_identifier=self.db_hash)

        if queryset:
            self.instance = queryset[0]
            return self.instance.json_response
        else:
            return json.dumps(
                {
                    "status": 404,
                    "message": "No data found",
                    "version": "0.0",
                    "jwt": None,
                    "result": "error",
                }
            )

    def response(self):
        return self.instance.json_response if self.instance else None

    def save(self, json_response):
        if not self.instance:
            # Create a new (empty) record
            self.instance = FakiResponse()
        self.instance.path = self.path
        self.instance.method = self.method
        self.instance.parameters = self.db_parameters
        self.instance.payload = self.db_payload
        self.instance.headers = self.db_headers
        self.instance.hash_identifier = self.db_hash
        self.instance.json_response = json_response
        self.instance.save()
