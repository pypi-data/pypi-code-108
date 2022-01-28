# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split as tts

def get_train_validation_test(df, covariate_columns, observed_column = 'observed', training_frac = 0.6, validation_frac = 0.2):
    training_n = int(np.floor(len(df) * training_frac))
    validation_n = int(np.floor(len(df) * validation_frac))
    test_n = len(df) - training_n - validation_n

    df_train, df_test, df_train_y, df_test_y = tts(df[covariate_columns], 
                                                    df[observed_column],
                                                    train_size = training_n,
                                                    test_size = validation_n+test_n,
                                                    shuffle = True, 
                                                    stratify = df[observed_column])

    df_train[observed_column] = df_train_y
    df_test[observed_column] = df_test_y

    df_validation, df_test, df_validation_y, df_test_y = tts(df_test[covariate_columns], 
                                                    df_test[observed_column],
                                                    train_size = validation_n,
                                                    test_size = test_n,
                                                    shuffle = True, 
                                                    stratify = df_test[observed_column])

    df_validation[observed_column] = df_validation_y
    df_test[observed_column] = df_test_y

    return df_train, df_validation, df_test


def get_balanced_set(df, observed_column = 'observed'):

    num_pos = df.observed.sum()
    num_neg = len(df) - num_pos
    sample_n = min(num_pos, num_neg)

    balanced_training_data = pd.DataFrame()
    balanced_training_data = df[df[observed_column] == 1].sample(n=sample_n, random_state=1)
    balanced_training_data = balanced_training_data.append(df[df[observed_column] != 1].sample(n=sample_n, random_state=2))

    # Shuffle so that the labels occur randomly
    balanced_training_data = balanced_training_data.sample(frac=1)

    return balanced_training_data


def x_sin(x):
    return x * np.sin(x)


def sin_cos(x):
    return pd.DataFrame(dict(a=np.sin(x), b=np.cos(x)), index=x)


def rnn_data(data, time_steps, labels=False):
    """
    creates new data frame based on previous observation
      * example:
        l = [1, 2, 3, 4, 5]
        time_steps = 2
        -> labels == False [[1, 2], [2, 3], [3, 4]]
        -> labels == True [3, 4, 5]
    """
    rnn_df = []
    for i in range(len(data) - time_steps):
        if labels:
            try:
                rnn_df.append(data.iloc[i + time_steps].as_matrix())
            except AttributeError:
                rnn_df.append(data.iloc[i + time_steps])
        else:
            data_ = data.iloc[i: i + time_steps].as_matrix()
            rnn_df.append(data_ if len(data_.shape) > 1 else [[i] for i in data_])

    return np.array(rnn_df, dtype=np.float32)


def split_data(data, val_size=0.1, test_size=0.1):
    """
    splits data to training, validation and testing parts
    """
    ntest = int(round(len(data) * (1 - test_size)))
    nval = int(round(len(data.iloc[:ntest]) * (1 - val_size)))

    df_train, df_val, df_test = data.iloc[:nval], data.iloc[nval:ntest], data.iloc[ntest:]

    return df_train, df_val, df_test


def prepare_data(data, time_steps, labels=False, val_size=0.1, test_size=0.1):
    """
    Given the number of `time_steps` and some data,
    prepares training, validation and test data for an lstm cell.
    """
    df_train, df_val, df_test = split_data(data, val_size, test_size)
    return (rnn_data(df_train, time_steps, labels=labels),
            rnn_data(df_val, time_steps, labels=labels),
            rnn_data(df_test, time_steps, labels=labels))


def load_csvdata(rawdata, time_steps, seperate=False):
    data = rawdata
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    train_x, val_x, test_x = prepare_data(data['a'] if seperate else data, time_steps)
    train_y, val_y, test_y = prepare_data(data['b'] if seperate else data, time_steps, labels=True)
    return dict(train=train_x, val=val_x, test=test_x), dict(train=train_y, val=val_y, test=test_y)


def generate_data(fct, x, time_steps, seperate=False):
    """generates data with based on a function fct"""
    data = fct(x)
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)
    train_x, val_x, test_x = prepare_data(data['a'] if seperate else data, time_steps)
    train_y, val_y, test_y = prepare_data(data['b'] if seperate else data, time_steps, labels=True)
    return dict(train=train_x, val=val_x, test=test_x), dict(train=train_y, val=val_y, test=test_y)
