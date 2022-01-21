import matplotlib.pyplot as plt
import seaborn as sns
import lightgbm as lgb
import pandas as pd
from rltrade import config
from rltrade.data import FeatureEngineer, load_csv

csv_path = 'testdata/meta.csv'
train_period = ('2012-08-04','2021-01-01') #for training the model
test_period = ('2021-01-02','2021-12-20') #for testing the model

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

all_indicators = tech_indicators + additional_indicators

fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators)

df = load_csv(csv_path)
df = fe.create_data(df)

df['target'] = df.groupby('tic')['close'].shift(-1)
df = df.dropna()

train = fe.time_series_split(df, start = train_period[0], end = train_period[1])
test = fe.time_series_split(df, start = test_period[0], end = test_period[1])

x_train = train[all_indicators].values
y_train = train['target'].values
x_test = test[all_indicators].values
y_test = test['target'].values


params = {'reg_alpha': 6.147694913504962,
 'reg_lambda': 0.002457826062076097,
 'colsample_bytree': 0.3,
 'subsample': 0.8,
 'learning_rate': 0.001,
 'max_depth': 20,
 'num_leaves': 111,
 'min_child_samples': 285,
 'random_state': 48,
 'verbose':-1,
 'n_estimators': 10_000,
 'metric': 'rmse',
 'cat_smooth': 39}

lgb_train = lgb.Dataset(x_train,y_train)
lgb_test = lgb.Dataset(x_test,y_test)

lgb_model = lgb.train(
    params,
    lgb_train,
    valid_sets=[lgb_train,lgb_test],
    verbose_eval=1000,
    early_stopping_rounds=800,
)

def plot_feature_importance(model,features,plot=False):
    feature_importance = pd.DataFrame({"feature":features,"importance":model.feature_importance(importance_type='gain')})
    feature_importance = feature_importance.sort_values(by='importance',ascending=False)
    
    if plot:
        plt.figure(figsize=(10,10))
        sns.barplot(data=feature_importance,x='importance',y='feature')
        
        for idx, v in enumerate(feature_importance.importance):
                plt.text(v, idx, "  {:.2e}".format(v))
        
        plt.show()
    return feature_importance

feature_importance = plot_feature_importance(lgb_model,all_indicators)
print(feature_importance)
feature_importance.to_csv('featureimportance.csv',index=False)