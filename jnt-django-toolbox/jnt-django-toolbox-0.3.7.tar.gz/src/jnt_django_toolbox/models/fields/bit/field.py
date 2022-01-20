from contextlib import suppress

import six
from django.db.models.fields import BigIntegerField, Field

from jnt_django_toolbox.forms.fields import BitFieldFormField
from jnt_django_toolbox.models.fields.bit.query import BitQueryLookupWrapper
from jnt_django_toolbox.models.fields.bit.types import Bit, BitHandler

# Count binary capacity. Truncate "0b" prefix from binary form.
# Twice faster than bin(i)[2:] or math.floor(math.log(i))
MAX_FLAG_COUNT = int(len(bin(BigIntegerField.MAX_BIGINT)) - 2)


class BitFieldFlags:
    """Bit field flags wrapper."""

    def __init__(self, flags):
        """Initializing."""
        if len(flags) > MAX_FLAG_COUNT:
            raise ValueError("Too many flags")

        self._flags = flags

    def items(self):
        """Items."""
        return [(flag, Bit(self._flags.index(flag))) for flag in self._flags]

    def keys(self):
        """Items."""
        return self._flags

    def values(self):
        """Values."""
        return [Bit(self._flags.index(flag)) for flag in self._flags]

    def __getattr__(self, key):
        if key not in self._flags:
            raise AttributeError("flag {0} is not registered".format(key))

        return Bit(self._flags.index(key))

    def __repr__(self):
        return repr(self._flags)

    def __iter__(self):
        yield from self._flags


class BitFieldCreator:
    """
    A placeholder class that provides a way to set the attribute on the model.

    Descriptor for BitFields.  Checks to make sure that all flags of the
    instance match the class.  This is to handle the case when caching
    an older version of the instance and a newer version of the class is
    available (usually during deploys).
    """

    def __init__(self, field):
        """Initializing."""
        self.field = field

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.field.to_python(value)

    def __get__(self, instance, type=None):
        if instance is None:
            return BitFieldFlags(self.field.flags)
        retval = instance.__dict__[self.field.name]
        if self.field.__class__ is BitField:
            # Update flags from class in case they've changed.
            retval._keys = self.field.flags
        return retval


class BitField(BigIntegerField):
    """Bit model field."""

    def __init__(self, flags, default=None, *args, **kwargs):
        """Initializing."""
        if isinstance(flags, dict):
            # Get only integer keys in correct range
            valid_keys = [
                flag_key
                for flag_key in flags.keys()
                if isinstance(flag_key, int)
                and (0 <= flag_key < MAX_FLAG_COUNT)
            ]
            if not valid_keys:
                raise ValueError("Wrong keys or empty dictionary")
            # Fill list with values from dict or with empty values
            flags = [flags.get(i, "") for i in range(max(valid_keys) + 1)]

        if len(flags) > MAX_FLAG_COUNT:
            raise ValueError("Too many flags")

        self._arg_flags = flags
        flags = list(flags)
        labels = []
        for num, flag in enumerate(flags):
            if isinstance(flag, (tuple, list)):
                flags[num] = flag[0]
                labels.append(flag[1])
            else:
                labels.append(flag)

        if isinstance(default, (list, tuple, set, frozenset)):
            new_value = 0
            for flag in default:
                new_value |= Bit(flags.index(flag))
            default = new_value

        BigIntegerField.__init__(self, default=default, *args, **kwargs)
        self.flags = flags
        self.labels = labels

    def contribute_to_class(self, cls, name, **kwargs):  # noqa: WPS117
        """Contribute to class."""
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, self.name, BitFieldCreator(self))

    def formfield(self, form_class=BitFieldFormField, **kwargs):
        """Get form field."""
        choices = [(k, self.labels[self.flags.index(k)]) for k in self.flags]
        return Field.formfield(self, form_class, choices=choices, **kwargs)

    def pre_save(self, instance, add):
        """Before save."""
        return getattr(instance, self.attname)

    def get_prep_value(self, value):
        """Get prepared value."""
        if value is None:
            return None
        if isinstance(value, (BitHandler, Bit)):
            value = value.mask
        return int(value)

    def get_db_prep_lookup(
        self,
        lookup_type,
        value,
        connection,
        prepared=False,
    ):
        """Get db prepared lookup."""
        if isinstance(getattr(value, "expression", None), Bit):
            value = value.expression
        if isinstance(value, (BitHandler, Bit)):
            return [value.mask]
        return BigIntegerField.get_db_prep_lookup(
            self,
            lookup_type=lookup_type,
            value=value,
            connection=connection,
            prepared=prepared,
        )

    def get_prep_lookup(self, lookup_type, value):
        """Get prepared lookup."""
        if isinstance(getattr(value, "expression", None), Bit):
            value = value.expression
        if isinstance(value, Bit):
            if lookup_type == "exact":
                return value
            raise TypeError(
                "Lookup type {0!r} not supported with `Bit` type.".format(
                    lookup_type,
                ),
            )
        return BigIntegerField.get_prep_lookup(self, lookup_type, value)

    def to_python(self, value):
        """Provide raw value."""
        if isinstance(value, Bit):
            value = value.mask
        if not isinstance(value, BitHandler):
            # Regression for #1425: fix bad data that was created resulting
            # in negative values for flags.  Compute the value that would
            # have been visible ot the application to preserve compatibility.
            if isinstance(value, six.integer_types) and value < 0:
                new_value = 0
                for bit_number, _ in enumerate(self.flags):
                    new_value |= value & (2 ** bit_number)
                value = new_value

            value = BitHandler(value, self.flags, self.labels)
        else:
            # Ensure flags are consistent for unpickling
            value._keys = self.flags
        return value

    def deconstruct(self):
        """Deconstruct."""
        name, path, args, kwargs = super().deconstruct()
        args.insert(0, self._arg_flags)
        return name, path, args, kwargs


with suppress(AttributeError):
    BitField.register_lookup(BitQueryLookupWrapper)
