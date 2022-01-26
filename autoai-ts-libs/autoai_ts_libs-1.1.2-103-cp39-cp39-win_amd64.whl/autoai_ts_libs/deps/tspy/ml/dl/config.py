import json


class Config:
    """
    Creates and stores a dictionary of model configuration
    An example config in json:

    {"layers":[{"type":"LSTM", "units":100}, {"type":"LSTM", "units":80}, {"type":"LSTM", "units":70}],
                                        # layer type is either LSTM or BidirectionalLSTM
    "prediction_type": "distribution",  # prediction_type should be either "value" OR "distribution" OR
                                                                            "ad" OR "classification"
    "num_features":6,
    "distribution_buckets":10   #distribution_buckets will be used if prediction_type is distribution
    "num_classes":10            #num_classes will be used if prediction_type is classification}
    """

    def __init__(self):
        self.configs = {}
        self.layers = []
        self.prediction_type = "value"
        self.num_features = 1
        self.distribution_buckets = None
        self.num_classes = None
        self.prediction_length = 1

    def from_json_dict(self, json_dict):
        self.configs = json_dict
        self.layers = [Layer(l) for l in self.configs['layers']]
        self.prediction_type = self.configs['prediction_type']
        if 'num_features' in self.configs:
            self.num_features = self.configs['num_features']
        if 'distribution_buckets' in self.configs:
            self.distribution_buckets = self.configs['distribution_buckets']
        elif self.prediction_type == "distribution":
            self.distribution_buckets = 10  # some default if not provided
        if 'num_classes' in self.configs:
            self.num_classes = self.configs['num_classes']
        if 'prediction_length' in self.configs:
            self.prediction_length = self.configs['prediction_length']

    def from_json(self, json_path):
        with open(json_path) as json_file:
            self.configs = json.load(json_file)
        self.from_json_dict(self.configs)


class Layer:
    def __init__(self, layer_dict):
        self.type = layer_dict['type']
        self.units = layer_dict['units']
        self.dropout = None
        self.recurrent_dropout = None
        if 'dropout' in layer_dict:
            self.dropout = layer_dict['dropout']
        if 'recurrent_dropout' in layer_dict:
            self.recurrent_dropout = layer_dict['recurrent_dropout']

    def __str__(self):
        return self.type + ' ' + str(self.units)
