class BaseModelHandler:
    def model_inputs(self):
        raise NotImplementedError

    def input(self):
        raise NotImplementedError

    def output(self):
        raise NotImplementedError
