import numpy as np


def calculate_sample_weights(cweights: np.ndarray, truth: np.ndarray) -> np.ndarray:
    # Calculate sample weights from class weights and a given truth with 2D or 3D shape
    # Supports one-hot encoded multi-class or binary truth/labels
    # Note returns sum of weighted truth over classes, thus should also work for multi-label ? TBD
    # Inputs:
    #   cweights num_classes x 1        weights for each class
    #   truth    frames x timesteps x num_classes or frames x num_classes
    # Returns:
    #   sweights frames x timesteps x 1 or frames x 1
    ts = truth.shape
    cs = cweights.shape

    if ts[-1] == 1 and cs[0] == 2:  # Binary truth needs 2nd "none" truth dimension
        truth = np.concatenate((truth, 1 - truth), axis=1)

    # broadcast num_classes x 1 over frames x num_classes or frames x timesteps x num_classes
    sweights = np.sum(cweights * truth, axis=-1)
    return sweights
