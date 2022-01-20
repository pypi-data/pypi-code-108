# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

import pyob.pyob as pyob


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ LOCALIZE
# └─────────────────────────────────────────────────────────────────────────────────────


def localize(*classes):
    """Localizes and returns an interable of PyOb class instances"""

    # Initialize cache
    cache = {}

    # Define localize helper function
    def _localize(Class):

        # Return if class is not a PyOb subclass
        if Class is pyob.PyOb or not issubclass(Class, pyob.PyOb):
            return Class

        # Return if class in cache
        if Class in cache:
            return cache[Class]

        # Localize bases
        bases = tuple([_localize(base) for base in Class.__bases__])

        # Get and set localized class
        cache[Class] = type(Class.__name__, bases, dict(Class.__dict__))

        # Set localized from attribute
        # This will ensure that isinstance() still works with localized PyOb classes
        cache[Class].PyObMeta.localized_from = Class

        # Return the localized class
        return cache[Class]

    # Localize classes
    classes = [_localize(Class) for Class in classes]

    # Return localized classes
    return classes[0] if len(classes) == 1 else tuple(classes)

    # DECISION: Should pyob.Ob be localized as well?
