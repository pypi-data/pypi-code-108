def equal_to(trial_datum, value) -> bool:
    """Returns True if the trial_datum is equal to a given value."""
    return trial_datum == value


def not_equal_to(trial_datum, value) -> bool:
    return trial_datum != value


def less_than(trial_datum, value) -> bool:
    return trial_datum < value


def greater_than(trial_datum, value) -> bool:
    return trial_datum > value


def less_than_or_equal_to(trial_datum, value) -> bool:
    return trial_datum <= value


def greater_than_or_equal_to(trial_datum, value) -> bool:
    return trial_datum >= value


def in_(trial_datum, value) -> bool:
    return trial_datum in value


def not_in(trial_datum, value) -> bool:
    return trial_datum not in value


def in_range(trial_datum, lower, upper) -> bool:
    return trial_datum in range(lower, upper)


def not_in_range(trial_datum, lower, upper):
    return trial_datum not in range(lower, upper)


def factor_of(trial_datum, value) -> bool:
    return value % trial_datum == 0


def has_factor(trial_datum, value) -> bool:
    return trial_datum % value == 0


def keys_contain(trial_dict, key):
    return key in trial_dict.keys()


def keys_contain_any_of(trial_dict, *keys):
    return any(k in trial_dict.keys() for k in keys)


def keys_contain_all_of(trial_dict, *keys):
    return all(k in trial_dict.keys() for k in keys)


def keys_contain_N_of(trial_dict, N, keys):
    return sum(k in trial_dict.keys() for k in keys) == N


def keys_contain_at_least_N_of(trial_dict, N, keys):
    return sum(k in trial_dict.keys() for k in keys) >= N


def keys_contain_at_most_N_of(trial_dict, N, keys):
    return sum(k in trial_dict.keys() for k in keys) <= N


def keys_contain_one_of(trial_dict, *keys):
    return keys_contain_N_of(trial_dict, 1, keys)


def keys_contain_at_least_one_of(trial_dict, keys):
    return keys_contain_at_least_N_of(trial_dict, 1, keys)


def keys_contain_at_most_one_of(trial_dict, keys):
    return keys_contain_at_most_N_of(trial_dict, 1, keys)


def keys_equal_to(trial_dict, *keys):
    return set(trial_dict.keys()) == set(keys)


def items_contain(trial_dict, **items):
    for k, v in items.items():
        try:
            if trial_dict[k] != v:
                return False
        except KeyError:
            return False
    return True


def allowed_keys(trial_dict, *keys):
    return not (set(trial_dict.keys()) - set(keys))


def required_keys(trial_dict, *keys):
    return not (set(keys) - set(trial_dict.keys()))


def forbidden_keys(trial_dict, *keys):
    return not (set(keys) & set(trial_dict.keys()))


def equal_to_approx(trial_datum, value, tolerance):
    return abs(trial_datum - value) < tolerance


def truthy(trial_datum):
    return not not trial_datum


def falsy(trial_datum):
    return not trial_datum


def null(trial_data):
    return True
