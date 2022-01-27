import requests


class ModelServer(object):
    def __init__(self, url='http://10.1.42.180:30061', serving='pmml'):
        self.metadata_url = f"{url}/{serving}/serving/metadata"
        self.predict_url = f"{url}/{serving}/serving/predict"

        fields = self.get_fields()
        self.input_fields, self.output_fields, self.target_fields = fields.values()
        print(fields)

    def get_fields(self):
        self._metadata = requests.get(self.metadata_url).json()
        _ = self._metadata.get('data', {})
        func = lambda field: list(map(lambda x: x['field'].get('name', {}).get('value'), _[field]))
        return {field: func(field) for field in ['inputFields', 'outputFields', 'targetFields']}

    def predict(self, values=None):
        json = dict(zip(self.input_fields, values if values is None else range(len(self.input_fields))))
        return requests.post(ms.predict_url, json=json).json()
