import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr


def pred_real_chart(name, pred, true):
    fig, ax = plt.subplots()
    ax.scatter(true, pred, s=0.2)
    ax.plot([true.min(), true.max()], [true.min(), true.max()], 'k--', lw=2)
    ax.set_xlabel('True ' + name)
    ax.set_ylabel('Predicted ' + name)
    plt.show()


def r2(pred, true):
    corr, _ = pearsonr(true, pred)
    return corr ** 2


def nmse(pred, true): return np.mean((true - pred) ** 2) / np.var(true)


def profit(nmse0, nmse1): return 100 * (nmse0 - nmse1) / nmse0
