# TODO: Must be better implementation than this shitt here.
from typing import Callable, Union
from uuid import UUID
from django.db.models import Model

from .const import UUID4_REGEXP
from .models import Upload


# FIXME: Must be some kind of behavior here to not store images
# after withdrawal.
# Maybe files that hasn't been withdrawn should e deleted after some time.
# TODO: Maybe every behavior like this should be separated into own
# worker, dunno...
# def withdraw(id: UUID) -> Upload:
#     return Upload.objects.get(id)


# TODO: There could be situation when there will be multiple links to
# the same file. So i think there should be possibility to use the same
# file instance in multiple places.
# TODO: Maybe there is no sense in `withdraw` at all... Should think of it.
# TODO: Files that hasn't been borrowed should e deleted after some time.
# def borrow(id: UUID)  -> Upload:


def take(id: UUID) -> Upload:
    """Just takes by id and doing nothing after."""
    return Upload.objects.get(id=id)


def set(
    instance: Model,
    field_name: str,
    value: str,
    behavior: Callable = take
) -> None:
    """Updates model's field value if passed string is an id of Upload.
    If not - either cleans if value id falsey or does nothing assuming
    no change happened.

    Args:
        instance (Model): Model instance.
        field_name (str): Instance's field name where file is stored.
        value (str): Value returned from some frontend.
        behavior (Callable, optional): Object resolvement behavior.
            Defaults to `take` behavior.
    """
    # Assuming that cleanup is happening.
    if not value:
        return setattr(instance, field_name, None)

    if UUID4_REGEXP.findall(value) is not None:
        return setattr(instance, field_name, behavior(value).file.file)

    # If the value is not empty and it's not the file identifier - then
    # there was no change and just do nothing.
