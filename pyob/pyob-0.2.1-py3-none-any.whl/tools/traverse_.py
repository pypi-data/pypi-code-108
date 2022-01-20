# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TRAVERSE PYOB RELATIONS
# └─────────────────────────────────────────────────────────────────────────────────────


def traverse_pyob_relations(
    PyObClass, callback, inclusive=False, ancestors=False, descendants=False, seen=None
):
    """Traverses a PyOb class's relations and applies a callback to each"""

    # Return if we hit ob.Ob
    if not PyObClass.PyObMeta.store._parents:
        return

    # Initialize seen
    seen = seen or {id(PyObClass)}

    # Check if inclusive
    if inclusive:

        # Apply callback to class
        callback(PyObClass)

    # Get root store
    root_store = PyObClass.PyObMeta.store

    # Iterate over relative types
    for (stores, should_traverse) in (
        (root_store._parents, ancestors),
        (root_store._children, descendants),
    ):

        # Continue of not should traverse
        if not should_traverse:
            continue

        # Iterate over stores
        for store in stores:

            # Get class
            PyObClass = store._PyObClass

            # Get class ID
            class_id = id(PyObClass)

            # Continue seen
            if class_id in seen:
                continue

            # Add class ID to seen
            seen.add(class_id)

            # Traverse PyOb relations
            traverse_pyob_relations(
                PyObClass=PyObClass,
                callback=callback,
                inclusive=True,
                ancestors=ancestors,
                descendants=descendants,
                seen=seen,
            )


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TRAVERSE PYOB ANCESTORS
# └─────────────────────────────────────────────────────────────────────────────────────


def traverse_pyob_ancestors(PyObClass, callback, inclusive=False):
    """Traverses a PyOb class's ancestors and applies a callback to each"""

    # Traverse PyOb ancestors
    traverse_pyob_relations(
        PyObClass=PyObClass,
        callback=callback,
        inclusive=inclusive,
        ancestors=True,
        descendents=False,
    )


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TRAVERSE PYOB DESCENDANTS
# └─────────────────────────────────────────────────────────────────────────────────────


def traverse_pyob_descendants(PyObClass, callback, inclusive=False):
    """Traverses a PyOb class's descendants and applies a callback to each"""

    # Traverse PyOb ancestors
    traverse_pyob_relations(
        PyObClass=PyObClass,
        callback=callback,
        inclusive=inclusive,
        ancestors=False,
        descendants=True,
    )


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ TRAVERSE PYOB RELATIVES
# └─────────────────────────────────────────────────────────────────────────────────────


def traverse_pyob_relatives(PyObClass, callback, inclusive=False):
    """Traverses a PyOb class's relatives and applies a callback to each"""

    # Traverse PyOb relatives
    traverse_pyob_relations(
        PyObClass=PyObClass,
        callback=callback,
        inclusive=inclusive,
        ancestors=True,
        descendants=True,
    )
