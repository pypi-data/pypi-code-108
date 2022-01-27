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

    def get_patients(self):
        return self.get_request(self._orthanc_url + 'patients')

    def get_studies(self):
        return self.get_request(self._orthanc_url + 'studies')

    def get_series(self):
        return self.get_request(self._orthanc_url + 'series')

    def get_instances(self):
        return self.get_request(self._orthanc_url + 'instances')

    def get_patients_info(self, ID):
        return self.get_request(self._orthanc_url + 'patients/' + ID)

    def get_studies_info(self, ID):
        return self.get_request(self._orthanc_url + 'studies/' + ID)

    def get_series_info(self, ID):
        return self.get_request(self._orthanc_url + 'series/' + ID)

    def get_instances_info(self, ID):
        return self.get_request(self._orthanc_url + 'instances/' + ID)




if __name__ == "__main__":
    print("main")