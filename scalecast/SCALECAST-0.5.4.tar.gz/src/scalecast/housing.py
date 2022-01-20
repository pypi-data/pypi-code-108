import pandas as pd
import pandas_datareader as pdr
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from Forecaster import Forecaster

models = ('mlr','knn','svr','xgboost','gbt','elasticnet','mlp','prophet','silverkite')
df = pdr.get_data_fred('HOUSTNSA',start='1900-01-01',end='2021-06-01')
f = Forecaster(y=df['HOUSTNSA'],current_dates=df.index) # to initialize, specify y and current_dates (must be arrays of the same length)
f.set_test_length(12) # specify a test length for your models - do this before eda

# model preprocessing
f.generate_future_dates(24) # this will create future dates that are on the same interval as the current dates and it will also set the forecast length

f.set_estimator('rnn')
f.manual_forecast(lags=36,
	epochs=15,
	call_me='rnn_default',
	validation_split=0.2,
	plot_loss=True)
f.manual_forecast(lags=36,
	hidden_layers_struct={'simple':{'units':64},'simple':{'units':64},'simple':{'units':64}},
	call_me='rnn_3lay',
	epochs=36,
	validation_split=0.2,
	plot_loss=True)
f.manual_forecast(lags=36,
	hidden_layers_struct={'lstm':{'units':64},'lstm':{'units':64},'lstm':{'units':64}},
	call_me='lstm_3lay',
	epochs=15,
	validation_split=0.2,
	plot_loss=True)
f.manual_forecast(lags=36,
	hidden_layers_struct={'lstm':{'units':64},'lstm':{'units':64,'dropout':0.2},'simple':{'units':64,'recurrent_dropout':0.2}},
	call_me='lstm_2lay_simple1lay',
	epochs=5,
	validation_split=0.2,
	plot_loss=True)

# combine models and run manually specified models of other varieties
f.set_estimator('combo')
f.manual_forecast() # simple average of top_3 models based on performance in validation

# plot results
matplotlib.use('QT5Agg')
f.plot(ci=True,models='top_5',order_by='TestSetRMSE',print_attr=['TestSetRMSE','TestSetR2','TestSetMAPE','HyperParams','Xvars','models']) # plots the forecast differences or levels based on the level the forecast was performed on
f.plot_test_set(ci=True,models='top_5',order_by='TestSetR2',include_train=60) # see test-set performance visually of top 5 best models by r2 (last 60 obs only)
f.plot_fitted(order_by='TestSetR2') # plot fitted values of all models ordered by r2

# export key results
f.export(to_excel=True,determine_best_by='LevelTestSetMAPE',excel_name='housing_results.xlsx') # export interesting model metrics and forecasts (both level and non-level)