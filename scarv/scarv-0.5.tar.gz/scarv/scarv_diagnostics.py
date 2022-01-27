def split(x, f):
    import itertools

    count = max(f) + 1
    return tuple( list(itertools.compress(x, (el == i for el in f))) for i in range(count) )  


def reliability_plot (confidence, accuracy):
    import matplotlib.pyplot as plt

    min_acc = min(accuracy)
    min_conf = min(confidence)

    plt.plot(confidence, accuracy, color="blue")
    plt.plot([0,1],[0,1])
    
    plt.ylim((min(min_acc, min_conf), 1))
    plt.xlim((min(min_acc, min_conf), 1))
    
    plt.xlabel('Confidence')
    plt.ylabel('Accuracy')

    print(plt.show())

    return 


def expected_calibration_error(n_bins, preds, y_mat, weights, plot=True):
    import collections
    import numpy as np
    import pandas as pd

    y_hat = np.argmax(preds, axis=1)
    p_hat = np.max(preds, axis=1)

    binned_preds = pd.qcut(p_hat, n_bins, labels=False, duplicates='drop').astype(int)
    bin_sizes = collections.Counter(binned_preds)

    y = np.argmax(y_mat, axis=1)
    n = len(y_hat)

    l1 = list(map(sum, split((y==y_hat) * weights, binned_preds))) 
    l2 = list(map(sum, split(weights, binned_preds))) 
    acc_by_bin = [x/y for x, y in zip(l1, l2) if y > 0]

    l3 = list(map(sum, split(p_hat * weights, binned_preds)))
    conf_by_bin = [x/y for x, y in zip(l3, l2) if y > 0]

    if plot:
        reliability_plot(conf_by_bin, acc_by_bin)

    ECE = np.sum([abs(x-y)*z for x,y,z in zip(acc_by_bin, conf_by_bin, l2)])/sum(l2)

    return ECE


def hand_till_auc(preds, y_test, weights=None):
    import collections
    import numpy as np

    if weights is None:
        weights = np.repeat(1, preds.shape[0])

    running_total_AUC = 0

    pairs = [[i, j] for i in range(4) for j  in range(4) if i!=j]
    for i, j in pairs:
        # select indices for which either i or j is observed
        ix = (y_test[:,i] == 1) | (y_test[:,j] == 1)

        # determine the prediction for class i and whether i occurred 
        preds_i = preds[ix, i]
        y = y_test[ix, i]
        w = weights[ix]

        # determine the order of the predictions
        order = np.argsort(preds_i)
        preds_i_std = preds_i[order]
        y_std = y[order]
        w_std = w[order]

        start_ix = (np.concatenate(([0], np.cumsum(w_std))) + 1)[:-1]
        end_ix = start_ix + w_std

        S_i = 0
        for i in range(len(start_ix)):
            if y_std[i] == 1:
                S_i = S_i + sum(range(start_ix[i], end_ix[i]))

        n_i = sum(w_std[y_std == 1])
        n_j = sum(w_std[y_std == 0])

        # calculate A(i|j) is order to prevent overflow
        A_ij = (S_i/n_i)/n_j - (n_i + 1)/(2 * n_j)
        running_total_AUC += A_ij

    AUC = running_total_AUC / len(pairs)
    return AUC



def max_auc(preds, weights=None):
    import numpy as np

    if weights is None:
        weights = np.repeat(1, preds.shape[0])

    output = np.empty(shape=(preds.shape[0], 5), dtype=int)

    for i in range(preds.shape[0]):
        output[i,:] = np.random.multinomial(weights[i], preds[i,:], size=1)
    
    output_extd = output[np.repeat(np.arange(output.shape[0]), np.sum(output > 0, axis=1))] 
    weight = np.sum(output_extd, axis=1)
    output_binary = (output_extd > 0)*1
    p = preds[np.repeat(np.arange(output.shape[0]), np.sum(output > 0, axis=1))]

    AUC = hand_till_auc(p, output_binary, weight)
    return AUC



from keras.callbacks import Callback
class IntervalEvaluation(Callback):

    def __init__(self, validation_data, flank, interval=1, wait=0, patience=1):
        super(Callback, self).__init__()

        self.interval = interval
        self.patience = patience
        self.wait = wait
        self.flank = flank
        self.X_val, self.y_val = validation_data
        self.auc = 0
        self.best_weights = None

    # update auc if maximum
    # if not, wait incremented
    # if wait equals patience, training is stopped
    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.interval == 0:
            preds = self.model.predict(self.X_val)
            score = hand_till_auc(preds, self.y_val)
            if score <= self.auc:
                if self.wait >= self.patience:
                    self.model.stop_training = True
                    print('Restoring model weights from the end of the best epoch.')
                    self.model.set_weights(self.best_weights)
                else:
                    self.wait += 1
            else:
                self.best_weights = self.model.get_weights()
                self.auc = score
                self.wait = 0
            print(score)



