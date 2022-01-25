from copy import copy

from stram.utils.exceptions import InvalidOrderException
from stram.utils.json_processing import dict2namespace
from stram.utils.hashing import get_image_hash, get_styling_config_hash


def variation_dict_to_styling_configs(variation_dict):
    """
    Parse the configuration for all styling variations and split them into
    individual styling config objects.

    Args:
        variation_dict (dict): grid configurations for styling variations
    Returns:
        styling_configs (list): contains all the individual styling configs
    """

    def split_config_on_attribute(config_dict, attribute):
        values = config_dict[attribute]
        config_children = [copy(config_dict) for _ in values]
        for i, value in enumerate(values):
            config_children[i][attribute] = value
        return config_children

    styling_configs = [variation_dict]
    values_to_vary = [k for k, v in variation_dict.items() if isinstance(v, list)]

    for attribute in values_to_vary:
        new_styling_configs = []

        for current_config in styling_configs:
            config_children = split_config_on_attribute(current_config, attribute)
            new_styling_configs.extend(config_children)

        styling_configs = new_styling_configs

    return [dict2namespace(sc) for sc in styling_configs]


def get_styling_configs_with_no_duplicates(styling_configs_list):
    """
    Parse a list of lists of styling configs and return a set of the unique ones
    in a dictionary that maps their hash to their content.

    Args:
        styling_configs_list (list): list of lists of styling configs
    Returns:
        styling_configs_dict (dict): maps styling config hash to styling config
    """
    styling_configs_dict = dict()

    for styling_configs_minilist in styling_configs_list:
        for styling_config in styling_configs_minilist:
            styling_configs_dict[get_styling_config_hash(styling_config)] = styling_config

    return styling_configs_dict


def get_orders(full_config, content_image, style_image, worklog=None):
    """
    Return a list of orders to be executed by avoiding duplicates and also taking into
    account the ones that have already been fulfilled. This is achieved by checking the
    hash of the images and the presence of individual styling config instances.

    Args:
        full_config (Bunch): configurations for all styling variations
        content_image (np.ndarray): the image to apply the style on
        style_image (np.ndarray): the image whose style to apply
        worklog (Worklog): keeps track of the work by storing the styling
                           configurations that have been done so far
    Returns:
        orders (dict): contains all the orders that have to be executed
                       maps styling config hash to styling config
    """
    styling_configs_list = [
        variation_dict_to_styling_configs(variation_dict)
        for variation_dict in full_config.configs
    ]
    styling_configs = get_styling_configs_with_no_duplicates(styling_configs_list)

    if worklog is None:
        return styling_configs

    content_hash = get_image_hash(content_image)
    style_hash = get_image_hash(style_image)

    if worklog.content_hash != content_hash or worklog.style_hash != style_hash:
        raise InvalidOrderException('Mismatch between the worklog and the pair of images')

    return {k: v for k, v in styling_configs.items() if k not in worklog.table}
