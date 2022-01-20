class BasketTransferCore:
    def __init__(self):
        self.files = None
        self.symbols = None
        self.names = None
        self.indices0 = None
        self.indices1 = None
        self.indices2 = None
        self.indices3 = None


class DataTransferCore:
    def __init__(self):
        self.dataset = None
        self.log = None
        self.pkl = None
        self.list = None
        self.dict = None
        self.hdfs = None
        self.pdframe = None
        self.ndarray = None
        self.pttensor = None
        self.tftensor = None
 

class ModelTransferCore:
    def __init__(self):
        self.forecaster = None
        self.log = None
        self.prediction = None
        self.pkl = None
        self.joblib = None
        self.onnx = None
        self.pt = None
        self.pb = None
    


def basket_wrapper(baskets, kind=None):
    assert kind is not None, 'The kind argument must be defined.'
    BTC = BasketTransferCore()
    
    if kind == 'files': 
        BTC.files = baskets
    elif kind == 'symbols':
        BTC.symbols = baskets
    elif kind == 'names':
        BTC.names = baskets
    elif kind == 'indices0':
        BTC.indices0 = baskets
    elif kind == 'indices1':
        BTC.indices1 = baskets
    elif kind == 'indices2':
        BTC.indices2 = baskets
    elif kind == 'indices3':
        BTC.indices3 = baskets
    else:
        setattr(BTC, kind, baskets)

    return getattr(BTC, kind)
