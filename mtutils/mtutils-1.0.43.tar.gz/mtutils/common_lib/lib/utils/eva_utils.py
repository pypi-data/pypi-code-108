from functools import reduce
import numpy as np

def get_TFPN(ann_array, pred_array):
    ann_array = np.array(ann_array).astype('float32')
    pred_array = np.array(pred_array).astype('float32')
    
    ann_array.shape == pred_array.shape
    
    # TP
    TP = np.sum((ann_array > 0.5) * (pred_array >= 0.5))
    
    # FP
    FP = np.sum((ann_array < 0.5) * (pred_array >= 0.5))
    FP_index = np.nonzero((ann_array < 0.5) * (pred_array >= 0.5))[0].tolist()
    
    # TN
    TN = np.sum((ann_array < 0.5) * (pred_array <= 0.5))
    
    # FN
    FN = np.sum((ann_array > 0.5) * (pred_array <= 0.5))
    FN_index = np.nonzero((ann_array > 0.5) * (pred_array <= 0.5))[0].tolist()
    
    total = reduce(lambda x, y: x * y, list(ann_array.shape) + [1])
    
    assert TP + FP + TN + FN == total
    
    reduce(lambda x, y: x *y, list(ann_array.shape) +[1])
    
    acc = (TP + TN) / max(1, total)
    miss = FN / max(1, total)
    fa = FP / max(1, total)
    
    recall = TP / max(1, TP + FN)
    precision = TP / max(1, TP + FP)
    
    F1_score = 2 * recall * precision / (recall + precision + 1e-8)
    
    info_dict = dict(
        TP=TP,
        FP=FP,
        TN=TN,
        FN=FN,
        total=total,
        FP_index=FP_index,
        FN_index=FN_index,
        acc=acc,
        miss=miss,
        fa=fa,
        recall=recall,
        precision=precision,
        F1_score=F1_score
    )
    
    return info_dict