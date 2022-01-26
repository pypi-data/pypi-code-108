import configparser
import requests
import json

class binubuo:
    def __init__(self, apikey):
        self.rapidapi_key = apikey
        self.readconfig()

    def readconfig(self):
        self.rapidapi_host = "binubuo.p.rapidapi.com"
        self.baseurl = "https://" + self.rapidapi_host
        self.default_generator_rows = 1

    def setheaders(self):
        self.headers = {}
        self.headers["x-rapidapi-host"] = self.rapidapi_host
        self.headers["x-rapidapi-key"] = self.rapidapi_key

    def call_binubuo(self, rest_path, query_string):
        self.setheaders()
        self.resp = requests.request("GET", self.baseurl + self.category + rest_path, headers=self.headers, params=query_string)
        if self.resp.ok:
            self.response_json = json.loads(self.resp.text)
        else:
            if self.resp.status_code == 403:
                print("Invalid API key specified.")
            elif self.resp.status_code == 404:
                print("Generator not found. Category: " + self.category + ". Generator: " + rest_path)
            else:
                print("Communication failure")

    def get_generator_response_value(self):
        first_key = list(self.response_json)[0]
        self.generator_response_value = list(list(self.response_json.values())[0][0].values())[0]

    def generate(self, category, function):
        # Incase called directly
        self.category = "/generator/" + category
        rest_path = "/" + function
        query_string = {"rows": self.default_generator_rows}
        self.call_binubuo(rest_path, query_string)
        if self.resp.ok:
            self.get_generator_response_value()
            return self.generator_response_value
