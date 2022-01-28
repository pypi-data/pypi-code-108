from auger_ml.preprocessors.base import BasePreprocessor
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

class EliminatePreprocessor(BasePreprocessor):
    def __init__(self, params):
        super(EliminatePreprocessor, self).__init__(
            params=params,
            params_keys=['thresh_var']
        )
        self._thresh_var = params.get('thresh_var', 0.05)

    def fit(self, df):
        super(EliminatePreprocessor, self).fit(df)

        #logging.info("EliminatePreprocessor var start")
        var = df.var()
        #logging.info("EliminatePreprocessor var end")
        self._cols = var[var <= self._thresh_var].index.tolist()
        self._cols = [col for col in self._cols if (col.startswith("cyclic__") or
                                                    col.startswith("cat__") or
                                                    var[col] == 0.0)]

    def transform(self, df):
        super(EliminatePreprocessor, self).transform(df)
        df.drop(self._cols, axis=1, inplace=True)
        return df
