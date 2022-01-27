# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.exceptions import UserError, UserWarning


class ImportMethodError(UserError):
    pass


class SanityCheckError(UserError):
    pass


class BalanceCheckWarning(UserWarning):
    pass


class MissingJournalError(UserError):
    pass


class UnpostedLinesError(UserError):
    pass
