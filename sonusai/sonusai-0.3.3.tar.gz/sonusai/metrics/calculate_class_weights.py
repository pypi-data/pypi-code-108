import numpy as np


def calculate_class_weights(truth: np.ndarray, oweight: int = -1, oweight_idx: int = -1) -> np.ndarray:
    # Calculate class weights with support for non-existent classes (a problem with sklearn)
    # where non-existent class gets a weight of 0 (instead of inf)
    # Includes optional weighting of an "other" class if specified
    # ref: cweights = class_weight.compute_class_weight(class_weight='balanced', classes=clabels, y=tlabels)
    # Inputs:
    #   truth    size frames x timesteps x num_classes or frames x num_classes truth data in one-hot format
    #   oweight  weight of the "other" class
    #            >1 will increase weighting/importance relative to the true count
    #            0>oweight<1 will decrease weighting/importance relative
    #            <0 disable, use true count (default = -1)
    #   oweight_idx index of other class in one-hot mode, default = num_classes-1 (the last)

    (frames, num_classes) = truth.shape

    if num_classes > 1:
        # clabels = list(range(0,num_classes))            # num_classes labels 0:num_classes-1
        tlabels = np.argmax(truth, axis=-1)  # framesx1 labels from one-hot, last dim
        cnt = np.bincount(tlabels, minlength=num_classes).astype(float)
    else:
        # clabels = list(range(0,2))        # [0,1] binary case
        num_classes = 2
        tlabels = np.int8(truth >= 0.5)[:, 0]  # quantize to binary and shape (frames,) for bincount
        cnt = np.bincount(tlabels, minlength=num_classes).astype(float)

    if oweight > 0:
        if oweight_idx < 0:
            oweight_idx = num_classes - 1  # default to last class
        cnt[oweight_idx] = cnt[oweight_idx] / oweight

    cweights = frames / (num_classes * cnt)  # avoid sklearn problem with absent classes
    cweights[cweights == np.inf] = 0  # just assign non-existent class weight of 0

    return cweights
