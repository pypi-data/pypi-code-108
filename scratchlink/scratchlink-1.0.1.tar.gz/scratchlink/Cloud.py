"""
The Cloud Data Code
"""

import requests

_website = "scratch.mit.edu"
_api = f"api.{_website}"


class Cloud:
    def __init__(self, project_id):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        self.project_id = str(project_id)

    def get_variable_data(self, limit=100, offset=0):
        """
        Returns the cloud variable data
        :param limit: The limit
        :param offset: The offset or the number of values you want to skip from the beginning
        """
        response = requests.get(
            f"https://clouddata.scratch.mit.edu/logs?projectid={self.project_id}&limit={limit}&offset={offset}",
            headers=self.headers).json()
        data = []
        for i in range(0, len(response)):
            data.append({'User': response[i]['user'],
                         'Action': response[i]['verb'],
                         'Name': response[i]['name'],
                         'Value': response[i]['value'],
                         'Timestamp': response[i]['timestamp']
                         })
        return data

    def get_cloud_variable_value(self, variable_name, limit=100):
        """
        Returns the cloud variable value
        :param variable_name: The name of the variable
        :param limit: The limit
        """
        if str(variable_name.strip())[0] != "☁":
            n = f"☁ {variable_name.strip()}"
        else:
            n = f"{variable_name.strip()}"
        data = []
        d = self.get_variable_data(limit=limit)
        i = 0
        while i < len(d):
            if d[i]['Name'] == n:
                data.append(d[i]['Value'])
            i = i + 1
        return data

    def pretty_print_cloud_data(self):
        """
        Pretty Print the Cloud Data
        """
        data = self.get_variable_data()[0]
        length = self._find_max_length(data) + 10
        print("\033[1;33;40m" + "-" * length)
        print("\033[1;35;40m" + "Cloud Data of Project with ID", str(self.project_id) + ":")
        for i in data:
            print("\t\033[1;32;40m" + i + ":", "\033[1;34;40m" + str(data[i]).replace("\n", " "))
        print("\033[1;33;40m" + "-" * length)
        print("\033[0m")

    def _find_max_length(self, d):
        """
        DON'T USE THIS
        """
        length = 0
        for i in d.values():
            if len(str(i)) > length:
                length = len(str(i))
        return length
