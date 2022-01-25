# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.exceptions import UserWarning
from trytond.model.exceptions import ValidationError


class DepositError(ValidationError):
    pass


class DepositWarning(UserWarning):
    pass
