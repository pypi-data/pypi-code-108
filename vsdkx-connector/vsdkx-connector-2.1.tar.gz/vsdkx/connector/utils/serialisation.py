import pickle


def unpickle_frame_from_message(frame_string):
    """
    Unpickle byte string of an image received from a message

    Args:
        frame_string (bytes): frame in a pickled form

    Returns:
        (np.array): numpy-array representation of the video frame
    """
    return pickle.loads(frame_string)


def serialize_inference_result(inference_result):
    """
    Serialize tuple resulted from running inference on a frame by pickling the
    object

    Args:
        inference_result (tuple):

    Returns:
        (bytes): pickled byte-string of inference results
    """
    return pickle.dumps(inference_result)
