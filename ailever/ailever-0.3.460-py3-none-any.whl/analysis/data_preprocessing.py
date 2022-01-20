
from ..logging_system import logger
from .digitization_for_categorical_variables import CategoricalDataset, QuantifyingModel, Criterion, AdamaxOptimizer

from tqdm import tqdm
import numpy as np
import pandas as pd
import statsmodels.tsa.api as smt


class DataPreprocessor:
    def __init__(self):
        self.storage_box = list()

    def time_splitor(self, table, date_column=None, only_transform=False, keep=False):
        origin_columns = table.columns
        table = table.copy()

        if date_column is None:
            assert 'date' in table.columns, "Table must has 'date' column"
            table['date'] = pd.to_datetime(table['date'].astype(str))
            table = table.set_index('date')
        else:
            table[date_column] = pd.to_datetime(table[date_column].astype(str))
            table = table.set_index(date_column)

        table['TS_year'] = table.index.year
        table['TS_quarter'] = table.index.quarter
        table['TS_month'] = table.index.month
        table['TS_week'] = table.index.isocalendar().week
        table['TS_day'] = table.index.day
        table['TS_hour'] = table.index.hour
        table['TS_minute'] = table.index.minute
        table['TS_second'] = table.index.second
        table['TS_sequence'] = np.linspace(-1, 1, table.shape[0])
        #table['TS_daysinmonth'] = table.index.daysinmonth
        #table['TS_weekday'] = table.index.weekday
        table = table.reset_index()
        
        dropping_columns = list()
        for column in table.columns:
            num_unique = pd.unique(table[column]).shape[0]
            if num_unique == 1:
                dropping_columns.append(column)
        for d_column in dropping_columns:
            table = table.drop(d_column, axis=1)
        
        if only_transform:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            table = table[columns]

        if keep:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            self.storage_box.append(table[columns])

        return table

    def temporal_smoothing(self, table, target_column=None, date_column=None, freq='D', smoothing_order=1, decimal=None, including_model_object=False, only_transform=False, keep=False):
        assert target_column is not None, 'Target column must be defined. Set a target(target_column) on columns of your table'

        origin_columns = table.columns
        table = table.copy()

        if date_column is None:
            assert 'date' in table.columns, "Table must has 'date' column"
            table['date'] = pd.to_datetime(table['date'].astype(str))
            table = table.set_index('date')
        else:
            table[date_column] = pd.to_datetime(table[date_column].astype(str))
            table = table.set_index(date_column)

        table = table.asfreq(freq).fillna(method='bfill').fillna(method='ffill')
        
        trend_orders = [(1,0,0), (0,0,1), (1,0,1),
                        (2,0,0), (2,0,1), (0,0,2), (1,0,2), (2,0,2),
                        (0,1,0), (1,1,0), (0,1,1), (1,1,1),
                        (2,1,0), (2,1,1), (0,1,2), (1,1,2), (2,1,2), 
                        (0,2,0), (1,2,0), (0,2,1), (1,2,1), 
                        (2,2,0), (2,2,1), (0,2,2), (1,2,2), (2,2,2)]
        trend_orders = list(filter(lambda x: x[1] <= smoothing_order, trend_orders))
        if freq in ['D']:
            seasonal_orders = [(0,0,0,0), (0,1,0,7)]
        elif freq in ['B']:
            seasonal_orders = [(0,0,0,0), (0,1,0,5)]
        elif freq in ['W']:
            seasonal_orders = [(0,0,0,0), (0,1,0,4)]
        elif freq in ['M', 'MS', 'BM', 'BMS']:
            seasonal_orders = [(0,0,0,0), (0,1,0,12)]
        elif freq in ['Q', 'QS', 'BQ', 'BQS']:
            seasonal_orders = [(0,0,0,0), (0,1,0,4)]
        elif freq in ['A', 'AS']:
            seasonal_orders = [(0,0,0,0), (0,1,0,10)]
        else:
            seasonal_orders = [(0,0,0,0)]
        seasonal_orders = list(filter(lambda x: x[1] <= smoothing_order, seasonal_orders))

        smoothing_models = dict()
        freq = table.index.freq
        for seasonal_order in seasonal_orders:
            for trend_order in trend_orders:
                model = smt.SARIMAX(table[target_column], order=trend_order, seasonal_order=seasonal_order, trend=None, freq=freq, simple_differencing=False)
                model = model.fit(disp=False)
                column_name = target_column + '_smt' + str(trend_order).strip('()').replace(', ', '') + 'X' + str(seasonal_order).strip('()').replace(', ', '')
                if model.mle_retvals['converged']:
                    print(f'* {trend_order}X{seasonal_order} : CONVERGENT')
                    if decimal:
                        table[column_name] = model.predict().round(decimal)
                    else:
                        table[column_name] = model.predict()

                else:
                    print(f'* {trend_order}X{seasonal_order} : DIVERGENT')

                if including_model_object:
                    smoothing_models[column_name] = model

        table = table.reset_index()
 
        if only_transform:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            table = table[columns]

        if keep:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            self.storage_box.append(table[columns])

        if including_model_object:
            return table, smoothing_models
        else:
            return table

    def spatial_smoothing(self, table, target_column=None, only_transform=False, keep=False, windows:list=[10], stability_feature=False):
        assert target_column is not None, 'Target column must be defined. Set a target(target_column) on columns of your table'

        origin_columns = table.columns
        table = table.copy()
        target_series = table[target_column]
        
        if isinstance(windows, int):
            window = windows
            table[target_column+f'_win{window}'] = target_series.rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill')
            if not stability_feature:
                _ = target_series.rolling(window=window, center=True).apply(lambda x: ((x - x.sort_values().values)**2).sum())
                table[target_column+f'_stb{window}'] = _.fillna(_.mean()) # stability
        else:
            for window in windows:
                table[target_column+f'_win{window}'] = target_series.rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill')
                if not stability_feature:
                    _ = target_series.rolling(window=window, center=True).apply(lambda x: ((x - x.sort_values().values)**2).sum())
                    table[target_column+f'_stb{window}'] = _.fillna(_.mean()) # stability

        if only_transform:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            table = table[columns]

        if keep:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            self.storage_box.append(table[columns])
        
        return table

    def missing_value(self):
        pass

    def sequence_parallelizing(self, table, target_column=None, only_transform=False, keep=False, window=5):
        assert target_column is not None, 'Target column must be defined. Set a target(target_column) on columns of your table'
        origin_columns = table.columns
        table = table.copy()
        target_series = table[target_column]

        appending_table = pd.concat([target_series.shift(i).fillna(method='bfill') for i in range(window+1)], axis=1)
        appending_table.columns = [ target_column + f'_seqpara{i}' for i in range(window+1) ] 
        table = pd.concat([table, appending_table], axis=1)

        if only_transform:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            table = table[columns]

        if keep:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            self.storage_box.append(table[columns])

        return table

    def to_numeric(self, table, target_column=None, only_transform=False, keep=False, num_feature=3, epochs=1000):
        assert target_column is not None, 'Target column must be defined. Set a target(target_column) on columns of your table'

        origin_columns = table.columns
        table = table.copy()

        training_information = dict()
        training_information['NumUnique'] = table[target_column].unique().shape[0]
        training_information['NumFeature'] = num_feature
        training_information['Epochs'] = epochs
        
        target_series = table[target_column]
        dataset = CategoricalDataset(X=target_series)
        model = QuantifyingModel(training_information)
        optimizer = AdamaxOptimizer(model.parameters(), lr=0.01)
        criterion = Criterion()

        epochs = training_information['Epochs']
        for epoch in tqdm(range(epochs)):
            losses = list()
            for train, target in dataset:
                hypothesis = model(train, generate=True) if epochs-1 == epoch else model(train, generate=False)
                cost = criterion(hypothesis, target)
                optimizer.zero_grad()
                cost.backward()
                optimizer.step()
                losses.append(cost.data.item())
        logger['analysis'].info(f"EPOCH[{epochs}] LOSS[{sum(losses)}] NUMGENERATEDFEATURE[{num_feature}]")
        
        feature_columns = list(map(lambda x: f'{target_column}_f'+str(x), list(range(training_information['NumFeature']))))
        feature_frame = pd.DataFrame(data=model.latent_feature.numpy(), columns=feature_columns)
        
        _ = target_series.value_counts(ascending=False).to_frame().reset_index().drop(target_column, axis=1).rename(columns={'index':target_column})
        feature_frame = pd.concat((_, feature_frame), axis=1)
        table = pd.merge(table, feature_frame, on=target_column, how='left')

        if only_transform:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            table = table[columns]

        if keep:
            columns = table.columns.tolist()
            for origin_column in origin_columns:
                columns.pop(columns.index(origin_column))
            self.storage_box.append(table[columns])

        return table
