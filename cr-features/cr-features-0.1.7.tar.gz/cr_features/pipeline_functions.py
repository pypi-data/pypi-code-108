import pandas as pd
import numpy as np
from hmmlearn import hmm
from sklearn.feature_selection import mutual_info_classif
from scipy.stats import pearsonr
from sklearn.metrics import accuracy_score


def normalizeMatrix(matrix, rows=False):
    mtrx = np.array(matrix).astype(float)
    if rows:
        for row in range(mtrx.shape[0]):
            if np.sum(mtrx[row]) > 0:
                mtrx[row] /= np.sum(mtrx[row])
            else:
                mtrx[row][row] = 1
        return mtrx
    return mtrx / np.sum(mtrx)


def numerize(y, activities):
    return y.apply(lambda x: activities.index(x))


def denumerize(y, activities):
    return y.apply(lambda x: activities[x])


def get_proportions(y, act_number):
    return [sum(y == i) / len(y) for i in range(act_number)]


def get_transitions(y, act_number):
    lst = [[0] * act_number for i in range(act_number)]
    for i in range(act_number):
        for j in range(act_number):
            num_trans = sum((y == i) & (y.shift(-1) == j))
            lst[i][j] = num_trans
    return np.array(lst)



def hmm_smooth(y_train, confusion, predictions, activities=None):
    #Check if numeric
    y_train = pd.Series(y_train)
    predictions = pd.Series(predictions)
    act_number = len(y_train.unique())
    if activities is not None:
        y_train = numerize(y_train, activities)
        predictions = numerize(predictions, activities)
        act_number = len(activities)
    y_train = pd.Series(y_train).astype(int)
    predictions = pd.Series(predictions).astype(int)

    cm_norm = normalizeMatrix(confusion.astype(float), rows=True)
    transitions = get_transitions(y_train, act_number)
    proportions = get_proportions(y_train, act_number)
    t_norm = normalizeMatrix(transitions.astype(float), rows=True)
    smoothed = hmm_model(np.array(predictions), proportions, t_norm, cm_norm, act_number)
    if activities is not None:
        smoothed = denumerize(smoothed, activities)
    return smoothed


def hmm_model(predictions, start_prob, t_norm, cm_norm, act_number):

    model = hmm.MultinomialHMM(n_components=act_number)
    model.startprob_ = start_prob
    model.transmat_ = t_norm
    model.emissionprob_ = cm_norm

    reshaped = predictions.reshape(-1, 1).astype(int)

    predicted = model.predict(reshaped)
    return pd.Series(predicted)

def three_step_fs(x_train, y_train, x_valid, y_valid, classifier, base_cutoff=1000, correlation_threshold=0.8,
                  verbose=False):
    scores = mutual_info_classif(x_train, y_train)
    indices = list(range(len(x_train.columns)))
    indices.sort(key=lambda x: scores[x], reverse=True)
    indices = indices[:base_cutoff]

    n = 100  # how many features are added in into correlation each round
    selected = []
    for i in range(min(base_cutoff, (len(indices)) // n) + 1):
        drop_index = len(selected)
        selected += indices[i * n: (i + 1) * n]
        if verbose:
            print('\tRound # %d: %d features, dropping from %d' % (i, len(selected), drop_index))
        selected = remove_correlated_features(
            selected, x_train, threshold=correlation_threshold, start_index=drop_index)
    if verbose:
        print('\tCompleted. Found %d not correlated features.' % len(selected))

    scores = []
    current_columns = []
    best_score = 0
    feature_threshold = 0.005

    for i, name in enumerate(selected):
        current_columns.append(name)
        if verbose:
            print(i, len(current_columns)),

        x_train_temp = x_train[x_train.columns[current_columns]]
        classifier.fit(x_train_temp, y_train)

        x_valid_temp = x_valid[x_valid.columns[current_columns]]
        predicted = classifier.predict(x_valid_temp)
        accuracy = accuracy_score(y_valid, predicted)

        if accuracy + feature_threshold >= best_score:
            if verbose:
                print("%2.1f" % (accuracy * 100), '... Keeping this feature', x_train.columns[name])
            best_score = accuracy
        else:
            if verbose:
                print("%2.1f" % (accuracy * 100), '... Removing this feature')
            current_columns.pop()

    return [x_train.columns[i] for i in current_columns]


def remove_correlated_features(indices, X, threshold=0.8, start_index=1):

    if start_index >= len(indices):
        return indices

    drop = [False for i in range(len(indices))]

    for i, first_index in enumerate(indices):
        if drop[i]: continue

        for j in range(max(i + 1, start_index), len(indices)):
            if drop[j]:
                continue

            second_index = indices[j]

            correlation, _ = pearsonr(X[X.columns[first_index]], X[X.columns[second_index]])

            if abs(correlation) > threshold:
                drop[j] = True

    return [index for i, index in enumerate(indices) if not drop[i]]
