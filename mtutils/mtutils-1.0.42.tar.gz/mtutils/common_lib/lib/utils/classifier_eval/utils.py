import numpy as np

def label_to_onehot(label_list, nb_classes):
    """将一个2维的label index list转为2维的onehot array 
    Args:
        label_list: 一个2维的label list, e.g., [[2], [0, 1], [1]]
        nb_classes: 类别数量, e.g., 3
    Return:
        一个二维的array, e.g., np.array([[0, 0, 1], [1, 1, 0], [0, 1, 0]])
    """
    res_arr = np.zeros([len(label_list), nb_classes])
    for i, label in enumerate(label_list):
        res_arr[i][label] = 1
    return res_arr

def onehot_to_label(onehot_array):
    """将一个2维的onehot array 转为1维的label list， 支持多标签形式
    Args:
        一个二维的array, e.g., [[0, 0, 1], [1, 0, 0], [0, 1, 1]]
    Return:
        label_list: 一个2维的label list, e.g., [[2], [0], [1, 2]]
    """
    label_list = []
    for arr in onehot_array:
        label_list.append(list(np.where(arr == 1)[0]))
    return label_list


if __name__ == '__main__':
    a = np.array([[0, 0, 1, 0], [1, 0, 1, 0], [0, 0, 0, 1]])
    b = onehot_to_label(a)
    print(b)
    c = label_to_onehot(b, 4)
    print(c)