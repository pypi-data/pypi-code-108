
import colemen_string_utils as strUtils


def get_kwarg(key_name, default_val=False, value_type=None, **kwargs):
    kwargs = keys_to_lower(kwargs)
    if isinstance(key_name, list) is False:
        key_name = [key_name]

    for name in key_name:
        # generate basic variations of the name
        varis = strUtils.gen.variations(name)
        for v_name in varis:
            if v_name in kwargs:
                if value_type is not None:
                    if isinstance(kwargs[v_name], value_type) is True:
                        return kwargs[v_name]
                else:
                    return kwargs[v_name]
    return default_val


# def gen_variations(string):
#     string = str(string)
#     varis = []
#     lower = string.lower()
#     upper = string.upper()
#     snake_case = lower.replace(" ", "_")
#     screaming_snake_case = upper.replace(" ", "_")
#     varis.append(lower)
#     varis.append(upper)
#     varis.append(snake_case)
#     varis.append(screaming_snake_case)
#     return varis


def keys_to_lower(dictionary):
    '''
        Converts all keys in a dictionary to lowercase.
    '''
    return {k.lower(): v for k, v in dictionary.items()}
