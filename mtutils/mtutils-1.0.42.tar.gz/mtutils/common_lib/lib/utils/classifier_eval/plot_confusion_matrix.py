# 该代码由sklearn官方提供

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels


def plot_confusion_matrix(y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues):
    """该函数用于画混淆矩阵。
    Args:
        y_true: 真实标签，1维array，如np.array([0, 3, 3, 2, 4, 2, 1, 3])
        y_pred: 预测标签，1维array, 如np.array([0, 2, 3, 2, 4, 2, 0, 3])
        classes: 标签名数组，1维np.array, 不能为list, e.g., np.array(['ok', 'ng1', 'ng2', 'ng3', 'ng4'])
        normalize: True：输出的为具体分对和分错的样本个数，False：输出的为分对和分错的比例
        title：混淆矩阵标题
        cmap：颜色
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    return ax


if __name__ == '__main__':
    
    # y_true = [0, 3, 3, 2, 4, 2, 1, 3]
    # y_pred = [0, 2, 3, 2, 4, 2, 0, 3]
    # class_names = np.array(['cls1', 'cls2', 'cls3', 'cls4', 'cls5'])
    # plot_confusion_matrix(np.array(y_true), np.array(y_pred), class_names,
    #                       normalize=False, title='hehe')
    # plt.show()

    cls1 = np.ones(15447) * 0
    cls2 = np.ones(813) * 1
    cls3 = np.ones(266) * 2
    cls4 = np.ones(909) * 3
    cls5 = np.ones(379) * 4
    cls6 = np.ones(60) * 5

    y_true = np.concatenate([cls1, cls2, cls3, cls4, cls5, cls6])
    print(y_true.shape)