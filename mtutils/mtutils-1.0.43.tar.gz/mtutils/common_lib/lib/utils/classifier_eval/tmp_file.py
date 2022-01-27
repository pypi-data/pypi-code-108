from eval_metrics import ClassifierEvalMultilabel
from utils import label_to_onehot
import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt

if __name__ == '__main__':

    split = 'set1_res101'

    print('Evaluate multilabel classification according to predicted scores...')
    label_file = './input_file/{:s}/multilabel_val_label.pkl'.format(split)
    pred_file = './input_file/{:s}/multilabel_val_prediction.pkl'.format(split)
    with open(label_file, 'rb') as f: # list
        labels = pkl.load(f)
    labels = label_to_onehot(labels, 6)# [[0], [1, 2], [0]] -> [[1, 0, 0], [0, 1, 1], [1, 0, 0]]
    with open(pred_file, 'rb') as f: # numpy
        predicts = pkl.load(f)
    ap_dict = ClassifierEvalMultilabel.compute_ap(labels, predicts)
    prec_dict = ClassifierEvalMultilabel.compute_p_at_r(labels, predicts, recall_thresh=0.995)
    ClassifierEvalMultilabel.draw_pr_curve(labels, predicts, output_dir='111')
    min_score, res_dict, fn_index_list, fp_index_list = ClassifierEvalMultilabel.compute_fnr_and_fpr(labels, predicts, ok_ind=0, fnr_thresh=0.005)
    print('AP res is: ', ap_dict)
    print('P at R res is: ', prec_dict)
    print('Loubao and wubao res is: ', res_dict)
    print('Min ng score is: ', min_score)


    print('Evaluate multilabel classification according to labels...')
    for i, pred in enumerate(predicts):
        for j, item in enumerate(pred[1:6]):
            predicts[i, j+1] = 1 if item >= min_score else 0
        if sum(pred[1:6]) >= 1:
            predicts[i, 0] = 0
        else:
            predicts[i, 0] = 1
            
    # cnt = 0
    # for i, pred in enumerate(predicts):
    #     if pred[0] == 1 and sum(pred) != 1:
    #         cnt += 1
    # print(cnt)

    ap_dict = ClassifierEvalMultilabel.compute_ap(labels, predicts)
    prec_dict = ClassifierEvalMultilabel.compute_p_at_r(labels, predicts, recall_thresh=0.995)
    ClassifierEvalMultilabel.draw_pr_curve(labels, predicts, output_dir='111')
    min_score, res_dict, fn_index_list, fp_index_list = ClassifierEvalMultilabel.compute_fnr_and_fpr(labels, predicts, ok_ind=0, fnr_thresh=0.005)
    print('AP res is: ', ap_dict)
    print('P at R res is: ', prec_dict)
    print('Loubao and wubao res is: ', res_dict)
    print('Min ng score is: ', min_score) # 此处min_score没有意义

    # 将从prediction score得到的label写入文件
    with open('./input_file/{:s}/multilabel_val_predict_label.pkl'.format(split), 'wb') as f:
        pkl.dump(predicts, f)
    

    # # 获取一张图片中有多个缺陷的图片
    # with open('./input_file/multilabel_val_path.pkl', 'rb') as f:
    #     img_paths = pkl.load(f)
    # for i, label in enumerate(labels):
    #     if sum(label) > 1:
    #         print(label)
    #         print(img_paths[i])