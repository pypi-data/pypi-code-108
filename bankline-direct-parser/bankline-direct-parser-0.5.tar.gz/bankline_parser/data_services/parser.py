from . import models
from .exceptions import ParseError
from .utils import IndexTrackingIterator


def _parse_account(lines_iter):
    # check for end of iteration on opening label of next account
    try:
        file_header_label = models.FileHeaderLabel(next(lines_iter))
    except StopIteration:
        return None

    user_header_label = models.UserHeaderLabel(next(lines_iter))

    # parse records until user_trailer_label
    records = []
    while True:
        current_row = next(lines_iter)
        try:
            # try and parse final row
            user_trailer_label = models.UserTrailerLabel(current_row)
            return models.Account(file_header_label, user_header_label,
                                  records, user_trailer_label)
        except ParseError:
            # if failed to parse final row, continue to parse records
            record = models.BaseRecord(current_row)
            if record.transaction_code is models.TransactionCode.balance_record:
                record = models.BalanceRecord(current_row)
            else:
                record = models.DataRecord(current_row)
            records.append(record)


def parse(iterable):
    lines_iter = IndexTrackingIterator(iterable)

    try:
        volume_header_label = models.VolumeHeaderLabel(next(lines_iter))

        accounts = []
        while True:
            account = _parse_account(lines_iter)
            if account:
                accounts.append(account)
            else:
                break

        if len(accounts) == 0:
            raise ParseError('No accounts found in data services file')

        return models.DataServicesFile(volume_header_label, accounts)
    except ParseError as e:
        raise ParseError('Line %s: %s' % (lines_iter.current_index, e))
    except StopIteration:
        raise ParseError('File ended unexpectedly')
