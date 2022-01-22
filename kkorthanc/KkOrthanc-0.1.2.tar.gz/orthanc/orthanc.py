import requests

class Orthanc:
    def __init__(self, orthanc_url):
        self._orthanc_url = orthanc_url

    def get_request(self, url):
        response = requests.get(url)

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return response.content

    def get_patient(self):
        return self.get_request(self._orthanc_url + 'patients')