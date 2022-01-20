from typing import List, Set

import pandas as pd


def entity_recognition_metrics(
        y_true: List[Set],
        y_pred: List[Set],
        pos_neg_ratio: str = None,
        self_metric=False
) -> pd.DataFrame:
    """
    the metric of entity_recognition, version-v2, reference: https://docs.qq.com/doc/DYXRYQU1YbkVvT3V2

    Args:
        y_true: list[set],the list of true target texts,each element is a set
        y_pred: list[set],the list of pred target texts,each element is a set
        pos_neg_ratio: the ratio of positive and negative sample importance, default: the ratio of positive and
                       negative sample sizes, you can set it,like"7:3"
        self_metric: self_metric

    Returns:
        show report and res
    """

    neg_data = 0
    neg_correct_dt = 0
    neg_wrong_dt = 0
    neg_redundant_entities = 0

    pos_data = 0
    pos_correct_dt = 0
    pos_wrong_dt = 0
    pos_correct_entities = 0
    pos_wrong_entities = 0
    pos_omitted_entities = 0
    pos_redundant_entities = 0

    for i, j in zip(y_true, y_pred):
        if i == set():
            neg_data += 1
            if j == set():
                neg_correct_dt += 1
            else:
                neg_wrong_dt += 1
                neg_redundant_entities += len(j)
        else:
            pos_data += 1
            true_pred = len(i & j)
            pos_correct_entities += true_pred

            if i == j:
                pos_correct_dt += 1
            elif len(i) > len(j):
                pos_wrong_dt += 1
                pos_wrong_entities += (len(j) - true_pred)
                pos_omitted_entities += (len(i) - len(j))
            else:
                pos_wrong_dt += 1
                pos_redundant_entities += (len(j) - len(i))
                pos_wrong_entities += (len(i) - true_pred)

    all_pos_entities = pos_correct_entities + pos_wrong_entities + pos_omitted_entities + pos_redundant_entities
    pred_neg = sum([1 for j in y_pred if len(j) == 0])
    true_neg = sum([1 for i in y_true if len(i) == 0])
    pred_pos = sum([len(j) for j in y_pred])
    true_pos = sum([len(i) for i in y_true])
    if neg_data == 0:
        neg_metric = neg_precision = neg_recall = neg_f1 = 0
    else:
        neg_metric = neg_correct_dt / (neg_correct_dt + neg_redundant_entities)
        neg_precision = neg_correct_dt / pred_neg if pred_neg else 0
        neg_recall = neg_correct_dt / true_neg if true_neg else 0
        neg_f1 = 2 * neg_precision * neg_recall / (neg_precision + neg_recall + 1e-10)
    if pos_data == 0:
        pos_metric = pos_precision = pos_recall = pos_f1 = 0
    else:
        pos_metric = pos_correct_entities / all_pos_entities
        pos_precision = pos_correct_entities / pred_pos if pred_pos else 0
        pos_recall = pos_correct_entities / true_pos if true_pos else 0
        pos_f1 = 2 * pos_precision * pos_recall / (pos_precision + pos_recall + 1e-10)

    sum_metric_micro = (pos_correct_entities + neg_correct_dt) / (
            neg_correct_dt + neg_redundant_entities + all_pos_entities)
    # sum_metric_macro = neg_metric * 0.5 + pos_metric * 0.5
    precision = (neg_correct_dt + pos_correct_entities) / (pred_pos + pred_neg + 1e-10)
    recall = (neg_correct_dt + pos_correct_entities) / (true_pos + true_neg + 1e-10)
    f1 = 2 * precision * recall / (precision + recall + 1e-10)

    if pos_neg_ratio:
        pos_all = float(pos_neg_ratio.split(':')[0])
        neg_all = float(pos_neg_ratio.split(':')[1])
        pos_ratio = pos_all / (pos_all + neg_all)
        neg_ratio = neg_all / (pos_all + neg_all)
    else:
        pos_ratio = pos_data / (pos_data + neg_data)
        neg_ratio = neg_data / (pos_data + neg_data)

    sum_metric_weighted = pos_ratio * pos_metric + neg_ratio * neg_metric

    # pos_precision = pos_correct_dt / (neg_correct_dt + pos_correct_dt)
    # recall = pos_correct_dt / pos_data
    tp = pos_correct_dt
    fn = pos_wrong_dt
    fp = neg_wrong_dt
    tn = neg_correct_dt

    accuracy = (tp + tn) / (tp + fn + fp + tn)
    # precision = tp / (tp + fp)
    # recall = tp / (tp + fn)
    # f1 = 2 / (1 / precision + 1 / recall)
    r = {
        'positive data': [str(pos_data), pos_correct_dt, pos_wrong_dt, pos_correct_entities,
                          pos_wrong_entities, pos_omitted_entities, pos_redundant_entities,
                          pos_precision, pos_recall, pos_f1, pos_metric],
        'negative data': [neg_data, neg_correct_dt, neg_wrong_dt, '-', '-', '-', neg_redundant_entities,
                          neg_precision, neg_recall, neg_f1, neg_metric],
        'all data ': [str(pos_data + neg_data), neg_correct_dt + pos_correct_dt, neg_wrong_dt + pos_wrong_dt,
                      pos_correct_entities, pos_wrong_entities, pos_omitted_entities,
                      pos_redundant_entities + neg_redundant_entities,
                      precision, recall, f1, sum_metric_micro],
        'weighted score': ['', '', '', '', '', '', '', '', '', '', sum_metric_weighted],
    }

    index = ['| data_num', '| correct_data', '| wrong_data', '| correct_entities', '| wrong_entities',
             '| omitted_entities', '| redundant_entities', '| precision', '| recall', '| f1', '| score']

    res_df = pd.DataFrame(r, index=index).T
    pd.set_option('precision', 4)
    pd.set_option('display.width', None)
    pd.set_option('display.max_columns', None)
    pd.set_option("colheader_justify", "center")
    print(res_df)

    print(
        f"正样本集得分为：{pos_correct_entities} / "
        f"({pos_correct_entities}+{pos_wrong_entities}+{pos_omitted_entities}+"
        f"{pos_redundant_entities}) = {round(pos_metric, 4)}，负样本集得分为：{neg_correct_dt} / ({neg_correct_dt} + "
        f"{neg_redundant_entities})={round(neg_metric, 4)}，",
        f"总体得分为： ({pos_correct_entities} + {neg_correct_dt}) / "
        f"({all_pos_entities}+{neg_correct_dt + neg_redundant_entities})={round(sum_metric_micro, 4)}",
        # f"准确率：{accuracy}",
    )
    print('\n')
    if self_metric:
        more_not_error_pos = (pos_correct_entities + pos_redundant_entities) / (
                pos_correct_entities + pos_wrong_entities + pos_omitted_entities + pos_redundant_entities)
        f"自定义-正样本集得分为：{pos_correct_entities + pos_redundant_entities} /"
        f" ({pos_correct_entities}+{pos_wrong_entities}+{pos_omitted_entities}+"
        f"{pos_redundant_entities}) = {round(more_not_error_pos, 4)}，负样本集得分为：{round(1, 4)}，"
        print('\n')
    return res_df

if __name__ == '__main__':
    y_true = [{'a','b'},{'j','d'},{'c','k'}]
    y_true.extend([set()]*27)
    y_pred = [{'a','b'},{'j','d'},{'c','f'}]
    y_pred.extend([set()] * 27)

    # y_true = [{'a','b','j','d','c','k'}]
    # y_pred = [{'a','b','j','d','c','f'}]


    r = entity_recognition_metrics(y_true,y_pred)
    # print(r.iloc[2,-3])
    print('1')