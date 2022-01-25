import pandas as pd
import numpy as np
import gc
# from ml_tools.model.model_ import Model
from ngocbienml import Model, ModelWithPipelineAndKfold, ModelWithPipeline, PipelineKfold
from ngocbienml.metrics.metrics_ import binary_score, gini
from sklearn.datasets import load_iris, load_diabetes

import warnings

warnings.filterwarnings('ignore')

PATH_TO_RAW_DATA = "/Users/NhatMinh/Desktop/ML/credit_scoring/data/data/train.csv"
PATH_TO_TITANIC = "C:\\Users\\os_biennn\\Desktop\\data\\titanic.csv"
MODEL_PATH = "C:\\Users\\os_biennn\\Desktop\\data\\"


def test2label_classification():
    print('test 2 class')
    diabets = load_diabetes()
    data = diabets.data
    target = diabets.target
    target = target > target.mean()
    print(np.unique(target))
    for name in ['lgb', 'RF']:
        model = Model(data=pd.DataFrame(data, columns=diabets.feature_names), \
                      target=pd.Series(target), name=name)
        model.run()


def test_multi_classification():
    from collections import Counter
    print('test mutilcalss class')
    data = load_iris()
    target = data.target
    print('target', Counter(target))
    data_df = data.data
    data_df = pd.DataFrame(data_df, columns=data.feature_name)
    target_df = pd.Series(target)
    model = Model(data=data_df, target=target_df, name="lgb")
    model.run()


def test_pipline():
    from collections import Counter
    from ngocbienml import MyPipeline, ModelWithPipelineAndKfold

    diabets = load_diabetes()
    data = diabets.data
    target = diabets.target
    target = target > target.mean()
    print(Counter(target))
    model = MyPipeline()
    model.steps.pop(-1)
    model.steps.append(['step name', ModelWithPipelineAndKfold()])
    model.fit(X=pd.DataFrame(data), y=pd.Series(target))
    model.score(X=pd.DataFrame(data), y=pd.Series(target))


def test_pipline2():
    from collections import Counter
    from ngocbienml import MyPipeline
    from sklearn.model_selection import train_test_split
    import random
    data = pd.read_csv(PATH_TO_RAW_DATA)
    target = data.apply(lambda x: random.choice([0, 1]), axis=1)
    train, test, y_train, y_test = train_test_split(data, target, test_size=.4)
    model = MyPipeline()
    model.fit(train, y_train)
    model.score(test, y_test)
    # help(model)
    from joblib import dump, load
    dump(model, MODEL_PATH + "model.joblib")
    this_model = load(MODEL_PATH + "model.joblib")
    print(this_model.steps)
    this_model.score(data, target)


def create_random_data(shape=(10000, 100)):
    print("create a random data whith shape=", shape)
    n_row = shape[0]
    n_col = shape[1]
    rd1 = np.random.uniform(0, 100, size=(n_row, 40))
    rd2 = np.random.randint(0, 1000, size=(n_row, 30))
    rd3 = np.random.normal(loc=10, scale=100, size=(n_row, 20))
    data = np.concatenate((rd1, rd2, rd3), axis=1)
    cols_names = ["uniform_%s" % i for i in range(40)]
    cols_names += ["uniform_int_%s" % i for i in range(30)]
    cols_names += ['normal_%s' % i for i in range(20)]
    df = pd.DataFrame(data, columns=cols_names)
    l_str = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    df[['cat_%s' % str(i) for i in range(10)]] = np.random.choice(l_str, size=(n_row, n_col - 90))
    target = df.apply(lambda x: np.random.randint(0, 2), axis=1)
    assert len(target) == len(df)
    return df, target


def data_loader(key):
    from collections import Counter

    from sklearn.model_selection import train_test_split
    import random

    if key == 'titanic':
        print('using titanic data')
        data = pd.read_csv(PATH_TO_TITANIC)
        target = data['Survived']
        data = data.drop(columns=['Survived'])
    elif key == 'kalapa':
        print('using kalapa data')
        data = pd.read_csv(PATH_TO_RAW_DATA)
        target = data.label
        data = data.drop(columns=['label'])
    elif key == 'adult':
        print('using adult data')
        data = pd.read_csv(MODEL_PATH + "adult.data")
        data.columns = [
            "Age", "WorkClass", "fnlwgt", "Education", "EducationNum",
            "MaritalStatus", "Occupation", "Relationship", "Race", "Gender",
            "CapitalGain", "CapitalLoss", "HoursPerWeek", "NativeCountry", "Income"
        ]
        target = data.Income
        target = target == target.iloc[0]
        data = data.drop(columns=['Income'])
    elif key == 'random':
        data, target = create_random_data()
    else:
        raise
    train, test, y_train, y_test = train_test_split(data, target, test_size=.2, stratify=target)
    return train, test, y_train, y_test


def test_pipline(key='random'):
    train, test, y_train, y_test = data_loader(key)
    from ngocbienml import MyPipeline
    train1 = train.copy()
    assert train.equals(train1)
    print('before processing in pipeline, shape of dataset=', train.shape)
    from ngocbienml import params_prevent_overfit
    model = PipelineKfold(name='regression', params=params_prevent_overfit)
    # model = MyPipeline(model_name='deep_learning',
    # epochs=200, hidden_layers=[20,10], activation=['sigmoid', 'sigmoid'],  dropout=.5)
    # print(model.steps)
    model.fit(train, y_train)
    # model.score(test.copy(), y_test)
    print('after processing, shape of dataset=', train.shape)
    print('before and after, the dataset is the same=', train.equals(train1))
    # help(model)
    print("*" * 100)
    print('try to use dump and load model')
    from joblib import dump, load
    # dump(model, MODEL_PATH + "model.joblib")
    # this_model = load(MODEL_PATH + "model.joblib")
    print('predict on test by Pipeline')
    model.score(train, y_train)
    # score = this_model.get_score(train, y_train)
    # print(score.shape)
    # print(score)
    print('ok ok ok')
    return None


def research_cv(method='bayes'):
    from ngocbienml import MyPipeline
    from ngocbienml import SearchCv
    from collections import Counter
    import warnings
    warnings.filterwarnings('ignore')

    train, _, y_train, _ = data_loader(key='kalapa')
    train = MyPipeline(model_name=None).fit_transform(train)
    searchcv = SearchCv(method=method, n_iter=40)
    print(train.shape)
    print(train.head())
    print(Counter(y_train))
    # return None
    searchcv.fit(train, y_train)
    searchcv.get_best_params()

# if __name__ == '__main__':
#
#     pipline(key='random')
