import re

from cnvrgv2.config import error_messages
from cnvrgv2.modules.users.user import ROLES
from cnvrgv2.errors import CnvrgArgumentsError


def validate_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


def validate_email(email):
    regex = r'^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,5}$'
    return re.search(regex, email) is not None


def validate_user_role(role):
    return role in ROLES.ALL_ROLES


def validate_username(username):
    regex = r'^[A-Za-z0-9]+$'
    return re.search(regex, username) is not None


def validate_types_in_list(input_list, input_type):
    """
    Validates that the input is a list of objects from the given type
    @param input_list: The input (should be a list of input_type objects)
    @param input_type: The type of the objects in input_list
    @return: Whenever input_list is a list of input_types
    """
    if not isinstance(input_list, list):
        return False
    for obj in input_list:
        if not isinstance(obj, input_type):
            return False
    return True


def attributes_validator(
        available_attributes,
        attributes,
        required_values=None,
):
    """
    @param available_attributes: Attributes available to the object that is being validated
    @param attributes: Attributes to validate
    @param required_values: Attributes that must be presented in the action
    @return: void, will raise errors on failed validations
    """

    required_values = required_values or []

    # Validates all the required attributes were received (and are not None or equivalent)
    for key in required_values:
        if key not in attributes.keys() or not attributes[key]:
            raise CnvrgArgumentsError(error_messages.MISSING_REQUIRED_VALUE.format(key))

    for key, value in attributes.items():
        # Validates that only allowed attributes were received
        if key == 'slug' or key not in available_attributes.keys():
            raise CnvrgArgumentsError(error_messages.FAULTY_KEY.format(key))
        # Validate received attribute types
        if value and not isinstance(value, available_attributes[key]):
            raise CnvrgArgumentsError(error_messages.FAULTY_VALUE.format(key))


# COMPUTES
def validate_gpu(gpu_obj):
    AVAILABLE_MIG_TYPES = [
        None,
        'mig-1g.5g',
        'mig-2g.20g',
        'mig-3g.25g'
    ]

    gpu = gpu_obj["count"]
    mig_device = gpu_obj["mig_device"]
    if mig_device not in AVAILABLE_MIG_TYPES:
        raise CnvrgArgumentsError(error_messages.TEMPLATE_FAULTY_MIG_VALUE)
    if gpu and not isinstance(gpu, float):
        raise CnvrgArgumentsError(error_messages.TEMPLATE_FAULTY_GPU.format(gpu))
    if mig_device and not isinstance(mig_device, str):
        raise CnvrgArgumentsError(error_messages.TEMPLATE_FAULTY_MIG.format(mig_device))


def validate_template_type(template_type):
    AVAILABLE_TEMPLATE_TYPES = [
        'regular',
        'mpi',
        'kubernetes',
        'pytorch',
        'spark_on_kubernetes'
    ]

    if template_type and template_type not in AVAILABLE_TEMPLATE_TYPES:
        raise CnvrgArgumentsError(error_messages.TEMPLATE_FAULTY_TYPE)
