from .stockprophet_0000 import StockForecaster as SF0000

import numpy as np
import pandas as pd

class StockProphet:
    def __init__(self, code, lag_shift, sequence_length=5):
        self.MainForecaster = SF0000(code, lag_shift, sequence_length)
        self.evaluation = self.MainForecaster.eval_table.copy()
        self.code = code
        self.lag_shift = lag_shift
        self.sequence_length = sequence_length
    
        self.dataset = self.MainForecaster.dataset.copy()
        self.price = self.MainForecaster.price.copy()
        self.X = self.MainForecaster.X.copy()
        self.y = self.MainForecaster.y.copy()
        self.model = self.MainForecaster.model

    def evaluate(self, model_name='GradientBoostingClassifier', trainstartdate='2015-03-01', teststartdate='2019-10-01', code=None, lag_shift=None, sequence_length=None, comment=None, visual_on=True):
        if sequence_length is None:
            sequence_length = self.sequence_length
        self.evaluation = self.MainForecaster.validate(model_name, trainstartdate, teststartdate, code, lag_shift, sequence_length, comment, visual_on)

        """
        After feature selection, dataset is divided into X, y
        dataset : num(columns of dataset) > num(columns of X) + num(columns of y)
        """
        self.dataset = self.MainForecaster.dataset.copy()
        self.price = self.MainForecaster.price.copy()
        self.X = self.MainForecaster.X.copy()
        self.y = self.MainForecaster.y.copy()
        self.model = self.MainForecaster.model

        if code is not None:
            self.code = code
        if lag_shift is not None:
            self.lag_shift = lag_shift
        if sequence_length is not None:
            self.sequence_length = sequence_length

        return self.evaluation

    def simulate(self, model_name, code, max_lag, sequence_length, trainstartdate, invest_begin):
        if sequence_length is None:
            sequence_length = self.sequence_length

        results = list()
        for lag_shift in range(1, max_lag):
            self.evaluation = self.MainForecaster.validate(model_name=model_name, trainstartdate=trainstartdate, teststartdate=invest_begin, code=code, lag_shift=lag_shift, sequence_length=sequence_length, comment=None, visual_on=False)

            self.dataset = self.MainForecaster.dataset.copy()
            self.price = self.MainForecaster.price.copy()
            self.X = self.MainForecaster.X.copy()
            self.y = self.MainForecaster.y.copy()
            self.model = self.MainForecaster.model

            if code is not None:
                self.code = code
            if lag_shift is not None:
                self.lag_shift = lag_shift
            if sequence_length is not None:
                self.sequence_length = sequence_length

            account = pd.DataFrame(data=np.c_[self.price.loc[invest_begin:].values.squeeze(), self.model.predict(self.X.loc[invest_begin:]).squeeze()], index=self.X.loc[invest_begin:].index.copy(), columns=['Price', 'Decision'])
            account['LagShift'] = lag_shift
            account = account.assign(Buy=lambda x: - x.Price * x.Decision)
            account = account.assign(Sell=lambda x: x.Price * (x.Decision*(-1)+1))
            account['Cash'] = account.assign(Cash=lambda x: x.Buy + x.Sell).Cash.cumsum() - account.Sell.astype(bool).sum()*account.Price[0]
            account['Cash'].iat[-1] = account['Cash'][-1] + account.Buy.astype(bool).sum()*account.Price[-1]
            
            invest = - account['Cash'][0]
            margin = account.Buy.astype(bool).sum()*account.Price[-1] - account.Sell.astype(bool).sum()*account.Price[0] + account.Sell.sum() + account.Buy.sum()
            profit = margin / invest
            invest_end = self.X.index[-1].strftime('%Y-%m-%d')
            results.append([code, invest_begin, invest_end, lag_shift, margin, invest, profit])
        report = pd.DataFrame(data=results, columns=['Code', 'Start', 'End', 'LagShift', 'Margin', 'Invest', 'Profit'])
        self.account = account
        self.report = report
        return report

    def observe(self):
        return

    def analyze(self):
        pass

    def forecast(self):
        pass
