import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import numpy as np
import pandas as pd
import pathlib

# plotting functions
def jointplot(
    x, y, xlabel='Truth', ylabel='Prediction', title=None, adjust_top=0.9, split_frac=None,
    kind='reg', stat_func=sklearn.metrics.r2_score, score_label=r'$R^2$', **joint_kws):
    ''' Plot the joint distribution of x and y

    Parameters
    ----------

    split_frac : float
        if not None, it represents the fraction for data splitting by CVSplit.
        For example, when CVSplit(5) is used, the first 20% samples will be used as validation,
        while the rest 80% samples are used for trainning, and in this case split_frac=0.2 should be set.
    '''
    if split_frac is not None:
        x = x[int(len(x)*split_frac):]
        y = y[int(len(y)*split_frac):]

    h = sns.jointplot(x=x, y=y, kind=kind, **joint_kws)
    score = stat_func(x, y)

    fake, = h.ax_joint.plot([], [], linestyle='', alpha=0)
    h.ax_joint.legend([fake], [f'{score_label}={score:.2f}'], frameon=False)

    h.ax_joint.set_ylabel(f'{xlabel} (n={np.size(x)})')
    h.ax_joint.set_xlabel(f'{ylabel} (n={np.size(y)})')
    if title is not None:
        h.fig.suptitle(title)
        h.fig.subplots_adjust(top=adjust_top) # Reduce plot to make room 

    return h.fig, h


def tsplot(x, y, ax=None, figsize=[10, 4], **plot_kwargs):
    plt.ioff()
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax.plot(x, y, **plot_kwargs)

    if 'fig' in locals():
        return fig, ax
    else:
        return ax

def lossplot(model, ax=None, figsize=[10, 4], **plot_kwargs):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    train_loss = np.array(model.history[:, 'train_loss'])
    valid_loss = np.array(model.history[:, 'valid_loss'])
    idx_stop = np.argmin(valid_loss) + 1
    epochs = np.arange(len(train_loss)) + 1

    tsplot(epochs, train_loss, mute=True, zorder=99, ax=ax, label='Training')
    tsplot(epochs, valid_loss, mute=True, zorder=99, ax=ax, label='Validation')
    ax.axvline(x=idx_stop, ymax=0.5, linestyle='--', color='grey', label=f'Optimal epoch: {idx_stop}')
    ax.set_yscale('log')
    ax.set_ylabel('Loss')
    ax.set_xlabel('Epochs')
    ax.legend(frameon=False, loc='upper right')
    ax.set_xlim(0, epochs[-1])

    if 'fig' in locals():
        return fig, ax
    else:
        return ax