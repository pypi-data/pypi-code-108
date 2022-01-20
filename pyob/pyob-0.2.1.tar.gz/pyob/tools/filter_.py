# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.exceptions import MultipleObjectsError


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ FILTER AND
# └─────────────────────────────────────────────────────────────────────────────────────


def filter_and(pyobs, **kwargs):
    """Filters a series of PyObs based on a series of keyword arguments (AND)"""

    # Return filtered PyObs
    return [
        pyob
        for pyob in pyobs
        if all([getattr(pyob, key) == val for key, val in kwargs.items()])
    ]


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ FILTER BY KEY
# └─────────────────────────────────────────────────────────────────────────────────────


def filter_by_key(pyob_dict, keys, value, ob_label_plural=None):
    """Filters a series of PyObs by a single key value"""

    # Initialize keys
    keys = keys or []

    # Filter PyObs by key
    pyob_dict = filter_or(pyob_dict, **{key: value for key in keys})

    # Get distinct PyOb count
    pyob_count = len(set(pyob_dict))

    # Check if PyOb count is greater than 1
    if pyob_count > 1:

        # Lowercase plural label
        ob_label_plural = (ob_label_plural or "Objects").lower()

        # Raise MultipleObjectsError
        raise MultipleObjectsError(
            f"{pyob_count} {ob_label_plural} share a unique key: "
            + ", ".join([str(pyob) for pyob in pyob_dict])
        )

        # NOTE: This should be guarded from happening to begin with but we
        # throw an error here in the event that it does happen

    # Return filtered PyObs
    return pyob_dict


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ FILTER BY KEYS
# └─────────────────────────────────────────────────────────────────────────────────────


def filter_by_keys(pyob_dict, keys, values, ob_label_plural=None):
    """Filters a series of PyObs by multiple key values"""

    # Return filtered PyObs
    return sum(
        [
            filter_by_key(
                pyob_dict=pyob_dict,
                keys=keys,
                value=value,
                ob_label_plural=ob_label_plural,
            )
            for value in values
        ],
        [],
    )


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ FILTER OR
# └─────────────────────────────────────────────────────────────────────────────────────


def filter_or(pyobs, **kwargs):
    """Filters a series of PyObs based on a series of keyword arguments (OR)"""

    # Return filtered PyObs
    return [
        pyob
        for pyob in pyobs
        if any([getattr(pyob, key) == val for key, val in kwargs.items()])
    ]
