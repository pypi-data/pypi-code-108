# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

import inspect

from typing import get_type_hints

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.pyob_store import PyObStore

from pyob.mixins import PyObMetaLabelMixin
from pyob.tools import is_iterable, remove_duplicates


# ┌─────────────────────────────────────────────────────────────────────────────────
# │ PYOB META BASE
# └─────────────────────────────────────────────────────────────────────────────────


class PyObMetaBase:
    """A Base PyOb Meta Class"""

    # ┌─────────────────────────────────────────────────────────────────────────────
    # │ STORE SETTINGS
    # └─────────────────────────────────────────────────────────────────────────────

    # Initialize keys to None
    keys = None

    # Initialize unique fields to None
    unique = None

    # ┌─────────────────────────────────────────────────────────────────────────────
    # │ APPEARANCE SETTINGS
    # └─────────────────────────────────────────────────────────────────────────────

    # Initialize display field to None
    display = None

    # Initialize labels to None
    label_singular = None
    label_plural = None

    # ┌─────────────────────────────────────────────────────────────────────────────
    # │ RUNTIME SETTINGS
    # └─────────────────────────────────────────────────────────────────────────────

    # Initialize disable type checking to False
    disable_type_checking = False

    # ┌─────────────────────────────────────────────────────────────────────────────
    # │ POPULATE STORE
    # └─────────────────────────────────────────────────────────────────────────────

    def populate_store(Class):
        """Populates the PyOb store of a PyOb class"""

        # Return None
        return None


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB META
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObMeta(type, PyObMetaLabelMixin):
    """A metaclass for the PyOb base class"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ INIT
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(cls, *args, **kwargs):
        """Init Method"""

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ PARENTS
        # └─────────────────────────────────────────────────────────────────────────────

        # Initialize parents
        parents = []

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ PYOB META
        # └─────────────────────────────────────────────────────────────────────────────

        # Get dicionary of default PyObMeta settings
        pyob_meta_dict = dict(PyObMetaBase.__dict__)

        # Iterate over bases
        for base in cls.__bases__:

            # Get PyObMeta of base
            BasePyObMeta = getattr(base, "PyObMeta", None)

            # Update PyObMeta dictionary
            BasePyObMeta and pyob_meta_dict.update(dict(base.PyObMeta.__dict__))

        # Update PyObMeta dictionary
        pyob_meta_dict.update(dict(cls.PyObMeta.__dict__))

        # Create a new reference for PyObMeta so each PyOb class has its own PyObMeta
        # Otherwise we will end up reassigning the mutable store on related PyOb classes
        cls.PyObMeta = type("PyObMeta", cls.PyObMeta.__bases__, pyob_meta_dict)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ STORE
        # └─────────────────────────────────────────────────────────────────────────────

        # Initialize store
        cls.PyObMeta.store = PyObStore(PyObClass=cls)

        # Iterate over bases
        for base in cls.__bases__:

            # Get PyObMeta of base
            BasePyObMeta = getattr(base, "PyObMeta", None)

            # Get store of base
            base_store = BasePyObMeta and BasePyObMeta.store

            # Continue if store is not a PyOb store
            if not isinstance(base_store, PyObStore):
                continue

            # Add parent to child store
            cls.PyObMeta.store._parents.append(base_store)

            # Add child to parent store
            base_store._children.append(cls.PyObMeta.store)

            # Add parent to parents
            parents.append(base_store._PyObClass)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ KEYS
        # └─────────────────────────────────────────────────────────────────────────────

        # Get keys
        keys = cls.PyObMeta.keys or ()

        # Handle case of string value as keys
        keys = keys and ((keys,) if type(keys) is str else tuple(keys))

        # Merge with parent keys
        keys = sum([p.PyObMeta.keys for p in parents] + [keys], ())

        # Ensure that keys definition is a unique tuple
        cls.PyObMeta.keys = remove_duplicates(keys)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ UNIQUE FIELDS
        # └─────────────────────────────────────────────────────────────────────────────

        # Get unique fields
        unique = cls.PyObMeta.unique or ()

        # Handle if unique fields is a single string
        unique = (unique,) if type(unique) is str else unique

        # Ensure that unique together fields are tuples
        unique = tuple(tuple(f) if is_iterable(f) else f for f in unique)

        # Merge with parent unique fields
        unique = sum([p.PyObMeta.unique for p in parents] + [unique], ())

        # Ensure that unique definition is a unique tuple
        cls.PyObMeta.unique = remove_duplicates(unique, recursive=True)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ PREPOST HOOKS
        # └─────────────────────────────────────────────────────────────────────────────

        # Get all methods
        methods = inspect.getmembers(cls.PyObMeta, predicate=inspect.isfunction)

        # Define pre- and post- constants
        PRE_ = "pre_"
        POST_ = "post_"

        # Define get hook cache helper
        def get_prepost(hook):
            return {k.replace(hook, "", 1): v for k, v in methods if k.startswith(hook)}

        # Initialize pre-setter cache
        cls.PyObMeta.pre = get_prepost(PRE_)

        # Initialize post-setter cache
        cls.PyObMeta.post = get_prepost(POST_)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ TYPE HINTS
        # └─────────────────────────────────────────────────────────────────────────────

        # Initialize type hints
        type_hints = {}

        # Update type hints by init type hints
        type_hints.update(get_type_hints(cls.__init__) or {})

        # Update type hints by class-level type hints
        type_hints.update(get_type_hints(cls) or {})

        # Set type hints
        cls.PyObMeta.type_hints = type_hints

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ LOCALIZATION
        # └─────────────────────────────────────────────────────────────────────────────

        # Set localized from attribute
        cls.PyObMeta.localized_from = None

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ PARENT
        # └─────────────────────────────────────────────────────────────────────────────

        # Call and return parent init method
        return super().__init__(*args, **kwargs)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CALL
    # └─────────────────────────────────────────────────────────────────────────────────

    def __call__(cls, *args, **kwargs):
        """Call Method"""

        # Get PyOb store
        store = cls.PyObMeta.store

        # Get store PyOb dict
        store_pyob_dict = store._pyob_dict

        # Initialize try-except block
        try:
            # Get instance
            instance = super().__call__(*args, **kwargs)

        # Handle any exception encountered during initialization
        except Exception:

            # Clean up key index as if instance never existed
            store._obs_by_key = {
                key: ob
                for key, ob in store._obs_by_key.items()
                if ob in store_pyob_dict
            }

            # Iterate over PyObs by unique field
            for field in store._obs_by_unique_field:

                # Clean up unique value index as if instance never created
                store._obs_by_unique_field[field] = {
                    val: ob
                    for val, ob in store._obs_by_unique_field[field].items()
                    if ob in store_pyob_dict
                }

            # Re-raise exception
            raise

            # NOTE: Exceptions can happen when setting individual attributes
            # The above except block ensures that PyOb initialization is atomic

        # Add instance to store
        cls.PyObMeta.store._pyob_dict[instance] = 1

        # Return instance
        return instance

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __GETATTR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __getattr__(cls, name):
        """Get Attr Method"""

        # Attempt to return PyOb by key
        return cls.PyObMeta.store.__getattr__(name)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __INSTANCECHECK__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __instancecheck__(cls, instance):
        """Instance Check Method"""

        # Get PyOb Meta
        pyob_meta = getattr(instance.__class__, "PyObMeta", None)

        # Check if PyOb Meta is not None
        if pyob_meta is not None:

            # Get localized from
            localized_from = getattr(pyob_meta, "localized_from", None)

            # Check if localized from current class
            if localized_from and issubclass(localized_from, cls):

                # Return True
                return True

        # Return default instance check
        return super().__instancecheck__(instance)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __POW__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __pow__(cls, other):
        """Pow Method"""

        # Return rshift of PyOb store
        return cls.PyObMeta.store >> other

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __RSHIFT__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __rshift__(cls, other):
        """Rshift Method"""

        # Return rshift of PyOb store
        return cls.PyObMeta.store >> other

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ OBS
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def obs(cls):
        """Returns the PyOb class's PyOb store"""

        # Return PyOb store
        return cls.PyObMeta.store
