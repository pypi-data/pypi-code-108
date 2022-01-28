from eval_metrics import ClassifierEvalBinary, ClassifierEvalMulticlass, ClassifierEvalMultilabel
from utils import label_to_onehot
import pickle as pkl


if __name__ == '__main__':

    # . Eval binary classification
    print('Evaluate binary classification...')
    label_file = './input/binary/binary_test_label.pkl'
    pred_file = './input/binary/binary_test_ep14_prediction.pkl'
    path_file = './input/binary/binary_test_path.pkl'
    with open(label_file, 'rb') as f:  # list
        labels = pkl.load(f)
    labels = [lab[0] for lab in labels]  # [[0], [1], [0]] -> [0, 1, 0]
    with open(pred_file, 'rb') as f:  # numpy
        predicts = pkl.load(f)
    with open(path_file, 'rb') as f:
        paths = pkl.load(f)
    ap_dict = ClassifierEvalBinary.compute_ap(labels, predicts)
    prec_dict = ClassifierEvalBinary.compute_p_at_r(
        labels, predicts, recall_thresh=0.995)
    ClassifierEvalBinary.draw_pr_curve(labels, predicts, output_path='./pr_curve/binary/pr.png')
    min_score, res_dict, fn_index_list, fp_index_list = ClassifierEvalBinary.compute_fnr_and_fpr(
        labels, predicts, fnr_thresh=0.005, fail_study=True)
    print('AP res is: ', ap_dict)
    print('P at R res is: ', prec_dict)
    print('Loubao and wubao res is: ', res_dict)
    print('Min ng score is: ', min_score)
    cls_dict = {0:'OK', 1:'NG'}
    ClassifierEvalBinary.draw_failure_cases(
        paths, labels, predicts, min_score, fn_index_list, fp_index_list, cls_dict, res_dir='./failure_case/binary')


    # . Eval multiclass classification
    print('Evaluate multiclass classification...')
    label_file = './input/multiclass/multiclass_test_label.pkl'
    pred_file = './input/multiclass/ep12_test_multiclass_prediction.pkl'
    path_file = './input/multiclass/multiclass_test_path.pkl'
    with open(label_file, 'rb') as f:  # list
        labels = pkl.load(f)
    labels = [lab[0] for lab in labels]  # [[0], [1], [2]] -> [0, 1, 2]
    with open(pred_file, 'rb') as f:  # numpy
        predicts = pkl.load(f)
    with open(path_file, 'rb') as f:
        paths = pkl.load(f)
    ap_dict = ClassifierEvalMulticlass.compute_ap(labels, predicts)
    prec_dict = ClassifierEvalMulticlass.compute_p_at_r(
        labels, predicts, recall_thresh=0.995)
    ClassifierEvalMulticlass.draw_pr_curve(labels, predicts, output_dir='./pr_curve/multiclass')
    min_score, res_dict, fn_index_list, fp_index_list = ClassifierEvalMulticlass.compute_fnr_and_fpr(
        labels, predicts, ok_ind=0, fnr_thresh=0.005, fail_study=True)
    print('AP res is: ', ap_dict)
    print('P at R res is: ', prec_dict)
    print('Loubao and wubao res is: ', res_dict)
    print('Min ng score is: ', min_score)
    cls_dict = {0:'ok', 1:'0', 2:'1', 3:'2', 4:'3', 5:'8'}
    ClassifierEvalMulticlass.draw_failure_cases(
        0, paths, labels, predicts, min_score, fn_index_list, fp_index_list, cls_dict, res_dir='./failure_case/multiclass')


    # . Eval multilabel classification
    print('Evaluate multilabel classification...')
    label_file = './input/multilabel/multilabel_test_label.pkl'
    pred_file = './input/multilabel/multilabel_test_ep15_prediction.pkl'
    path_file = './input/multilabel/multilabel_test_path.pkl'
    with open(label_file, 'rb') as f:  # list
        labels = pkl.load(f)
    # [[0], [1, 2], [0]] -> [[1, 0, 0], [0, 1, 1], [1, 0, 0]]
    labels = label_to_onehot(labels, 6)
    with open(pred_file, 'rb') as f:  # numpy
        predicts = pkl.load(f)
    with open(path_file, 'rb') as f:
        paths = pkl.load(f)
    ap_dict = ClassifierEvalMultilabel.compute_ap(labels, predicts)
    prec_dict = ClassifierEvalMultilabel.compute_p_at_r(
        labels, predicts, recall_thresh=0.995)
    ClassifierEvalMultilabel.draw_pr_curve(labels, predicts, output_dir='./pr_curve/multilabel')
    min_score, res_dict, fn_index_list, fp_index_list = ClassifierEvalMultilabel.compute_fnr_and_fpr(
        labels, predicts, ok_ind=0, fnr_thresh=0.005, fail_study=True)
    print('AP res is: ', ap_dict)
    print('P at R res is: ', prec_dict)
    print('Loubao and wubao res is: ', res_dict)
    print('Min ng score is: ', min_score)
    cls_dict = {0:'ok', 1:'0', 2:'1', 3:'2', 4:'3', 5:'8'}
    ClassifierEvalMultilabel.draw_failure_cases(
        0, paths, labels, predicts, min_score, fn_index_list, fp_index_list, cls_dict, res_dir='./failure_case/multilabel')
