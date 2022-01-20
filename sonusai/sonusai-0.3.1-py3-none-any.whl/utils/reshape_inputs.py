import numpy as np

import sonusai as sai
from sonusai import logger


def reshape_inputs(feature: np.ndarray, truth: np.ndarray, batch_size: int, timesteps: int = 0, flatten: bool = False,
                   add1ch: bool = False) -> (np.ndarray, np.ndarray, tuple, int, np.ndarray, str):
    # Check sonusai feature and truth data and reshape feature of size frames x strides x bands into
    # one of several options:
    # If timesteps > 0: (i.e. for recurrent NNs):
    #   no-flatten, no-channel:   sequences x timesteps x strides       x bands     (4-dim)
    #   flatten, no-channel:      sequences x timesteps x strides*bands             (3-dim)
    #   no-flatten, add-1channel: sequences x timesteps x strides       x bands x 1 (5-dim)
    #   flatten, add-1channel:    sequences x timesteps x strides*bands         x 1 (4-dim)
    #
    # If timesteps == 0, then do not add timesteps dimension
    #
    # The number of samples is trimmed to be a multiple of batch_size (Keras requirement) for
    # both feature and truth.
    # Channel is added to last/outer dimension for channel_last support in Keras/TF
    #
    # Returns:
    #   f, t,       reshaped feature and truth
    #   in_shape    input shape for model (timesteps x feature)
    #   num_classes number of classes in truth = output length of nn model
    #   cweights    weights of each class in truth, per sklearn compute_weights()
    #   msg         string with report with info on data and operations done

    f = feature
    t = truth

    (frames, strides, bands) = f.shape
    (truth_frames, num_classes) = t.shape
    if frames != truth_frames:  # Double-check correctness of inputs
        logger.error('Frames in feature and truth do not match')
        exit()

    msg = 'Training/truth shape: {}x{}x{}, nclass/outlen = {}\n'.format(frames, strides, bands, num_classes)
    msg += 'Reshape request: timesteps {}, batchsize {}, flatten={}, add1ch={}\n'.format(
        timesteps, batch_size, flatten, add1ch)

    # Compute class weights by hand as sklearn does not handle non-existent classes
    cweights = sai.metrics.calculate_class_weights(t)

    # calc new input shape only and return
    if batch_size == -1:
        if flatten:
            in_shape = [strides * bands]
        else:
            in_shape = [strides, bands]

        if timesteps > 0:
            in_shape = np.concatenate(([timesteps], in_shape[0:]), axis=0)

        if add1ch:
            in_shape = np.concatenate((in_shape[0:], [1]), axis=0)

        return f, t, in_shape, num_classes, cweights, msg  # quick

    if flatten:
        msg += 'Flattening {}x{} feature to {}\n'.format(strides, bands, strides * bands)
        f = np.reshape(f, (frames, strides * bands))

    # Reshape for Keras/TF recurrent models that require timesteps/sequence length dimension
    if timesteps > 0:
        sequences = frames // timesteps

        # Remove frames if remainder, not fitting into a multiple of new number of sequences
        frem = frames % timesteps
        brem = (frames // timesteps) % batch_size
        bfrem = brem * timesteps
        sequences = sequences - brem
        fr2drop = frem + bfrem
        if fr2drop:
            msg += 'Dropping {} frames for new number of sequences to fit in multiple of batch_size\n'.format(fr2drop)
            if f.ndim == 2:
                f = f[0:-fr2drop, :]  # Flattened input
            elif f.ndim == 3:
                f = f[0:-fr2drop, :, :]  # Un-flattened input

            t = t[0:-fr2drop, :]

        # Do the reshape
        msg += 'Reshape for timesteps = {}, new number of sequences (batches) = {}\n'.format(timesteps, sequences)
        if f.ndim == 2:  # Flattened input
            # str=str+'Reshaping 2 dim\n'
            f = np.reshape(f, (sequences, timesteps, strides * bands))  # was frames x bands*timesteps
            t = np.reshape(t, (sequences, timesteps, num_classes))  # was frames x num_classes
        elif f.ndim == 3:  # Unflattened input
            # str=str+'Reshaping 3 dim\n'
            f = np.reshape(f, (sequences, timesteps, strides, bands))  # was frames x bands x timesteps
            t = np.reshape(t, (sequences, timesteps, num_classes))  # was frames x num_classes
    else:
        # Drop frames if remainder, not fitting into a multiple of new # sequences (Keras req)
        fr2drop = f.shape[0] % batch_size
        if fr2drop > 0:
            msg += 'Dropping {} frames for total to be a multiple of batch_size\n'.format(fr2drop)
            f = f[0:-fr2drop, ]
            t = t[0:-fr2drop, ]

    # Add channel dimension if required for input to model (i.e. for cnn type input)
    if add1ch:
        msg += 'Adding channel dimension to feature\n'
        f = np.expand_dims(f, axis=f.ndim)  # add as last/outermost dim

    in_shape = f.shape
    in_shape = in_shape[1:]  # remove frame dim size

    msg += 'Feature final shape: {}\n'.format(f.shape)
    msg += 'Input shape final (includes timesteps): {}\n'.format(in_shape)
    msg += 'Truth final shape: {}\n'.format(t.shape)

    return f, t, in_shape, num_classes, cweights, msg
