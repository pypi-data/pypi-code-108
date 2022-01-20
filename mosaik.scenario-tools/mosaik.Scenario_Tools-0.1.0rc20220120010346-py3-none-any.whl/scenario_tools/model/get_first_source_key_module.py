def get_first_source_key(inputs: dict, attribute: str) -> str:
    """
    Get the key of the first source for the given attribute in the given inputs.

    :param inputs:
    :param attribute:
    :return:
    """
    # print('inputs', inputs)
    first_source_key: str = list(inputs[attribute].keys())[0]

    return first_source_key
