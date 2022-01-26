from sklearn.pipeline import Pipeline


class TSPipeline(Pipeline):
    # def __init__(self, steps, *, memory=None, verbose=False):
    def __init__(self, steps, **kwargs):
        super().__init__(steps, **kwargs)

    def predict(self, X=None, **predict_params):
        return super().predict(X, **predict_params)