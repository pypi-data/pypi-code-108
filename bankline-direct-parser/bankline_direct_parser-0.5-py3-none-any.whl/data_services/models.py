from . import fields
from .exceptions import ParseError
from .enums import BalanceType, TransactionCode


class DataServicesFile:
    def __init__(self, volume_header_label, accounts):
        self.volume_header_label = volume_header_label
        self.accounts = accounts

        self.validate()

    @property
    def account(self):
        return self.accounts[0] if self.accounts else None

    def is_valid(self):
        return False if self.errors else True

    def validate(self):
        errors = {}

        for i, account in enumerate(self.accounts):
            if not account.is_valid():
                errors['account %s' % i] = account.errors

        self.errors = errors


class Account:
    def __init__(self, file_header_label, user_header_label,
                 records, user_trailer_label):
        self.file_header_label = file_header_label
        self.user_header_label = user_header_label
        self.records = records
        self.user_trailer_label = user_trailer_label

        self.validate()

    def is_valid(self):
        return False if self.errors else True

    def validate(self):
        errors = []

        total_debit = 0
        total_credit = 0
        count_debit = 0
        count_credit = 0
        count_balance = 0

        for record in self.records:
            if record.is_debit():
                total_debit += record.amount
                count_debit += 1
            elif record.is_credit():
                total_credit += record.amount
                count_credit += 1
            elif record.is_balance():
                count_balance += 1

        utl = self.user_trailer_label
        if total_debit != utl.monetary_total_debit_items:
            errors.append(
                'Monetary total of debit items does not match expected: ' +
                'counted %s, expected %s' %
                (total_debit, utl.monetary_total_debit_items))
        if count_debit != utl.count_debit_items:
            errors.append(
                'Count of debit items does not match expected: ' +
                'counted %s, expected %s' %
                (count_debit, utl.count_debit_items))
        if total_credit != utl.monetary_total_credit_items:
            errors.append(
                'Monetary total of credit items does not match expected: ' +
                'counted %s, expected %s' %
                (total_credit, utl.monetary_total_credit_items))
        if count_credit != utl.count_credit_items:
            errors.append(
                'Count of credit items does not match expected: ' +
                'counted %s, expected %s' %
                (count_credit, utl.count_credit_items))
        if ((utl.count_balance_records is not None or count_balance > 0)
                and count_balance != utl.count_balance_records):
            errors.append(
                'Count of balance records does not match expected: ' +
                'counted %s, expected %s' %
                (count_balance, utl.count_balance_records))

        self.errors = errors


class Row:
    def __init__(self, row_content):
        for attr in dir(self):
            field = getattr(self, attr, None)
            if isinstance(field, fields.DataField):
                try:
                    output = field.parse(row_content)
                    setattr(self, attr, output)
                except ParseError as e:
                    raise ParseError('%s: %s' % (attr, e))

    def __str__(self):
        fields = []
        for attr in dir(self):
            if attr not in dir(type('o', (object,), {})):
                fields.append('%s: %s' % (attr, getattr(self, attr)))
        return '<' + self.__class__.__name__ + ' <' + ', '.join(fields) + '>>'


class VolumeHeaderLabel(Row):
    label_identifier = fields.StaticField(0, 4, 'VOL1')
    volume_serial_number = fields.TextField(4, 10)
    owner_identification = fields.StaticField(37, 47, '****830000')
    label_standard_level = fields.NumericField(79, 80)


class FileHeaderLabel(Row):
    label_identifier = fields.StaticField(0, 4, 'HDR1')
    file_identifier = fields.TextField(5, 13)
    file_sequence_number = fields.NumericField(13, 17)
    record_format = fields.StaticField(39, 40, 'F')
    creation_date = fields.DateField(47, 53)
    expiration_date = fields.DateField(66, 72)
    copy_indicator = fields.ZeroFilledField(72, 73)


class UserHeaderLabel(Row):
    label_identifier = fields.StaticField(0, 4, 'UHL1')
    processing_date = fields.DateField(4, 10)
    branch_sort_code = fields.TextField(10, 16)
    currency_code = fields.ZeroFilledField(20, 23)
    work_code = fields.TextField(28, 37)
    file_number = fields.ZeroFilledField(37, 40)
    customer_name = fields.TextField(54, 80, justification='l')


class UserTrailerLabel(Row):
    label_identifier = fields.StaticField(0, 4, 'UTL1')
    monetary_total_debit_items = fields.NumericField(4, 17)
    monetary_total_credit_items = fields.NumericField(17, 30)
    count_debit_items = fields.NumericField(30, 37)
    count_credit_items = fields.NumericField(37, 44)
    count_balance_records = fields.NumericField(44, 51)


class BaseRecord(Row):
    branch_sort_code = fields.TextField(0, 6)
    branch_account_number = fields.TextField(6, 14)
    type_of_account_code = fields.ZeroFilledField(14, 15)
    transaction_code = fields.EnumField(15, 17, TransactionCode)

    def is_credit(self):
        return self.transaction_code.name.startswith('credit')

    def is_debit(self):
        return self.transaction_code.name.startswith('debit')

    def is_balance(self):
        return self.transaction_code == TransactionCode.balance_record

    def is_total(self):
        return (self.transaction_code == TransactionCode.credit_total or
                self.transaction_code == TransactionCode.debit_total)


class DataRecord(BaseRecord):
    originators_sort_code = fields.TextField(17, 23, fill_char='0')
    originators_account_number = fields.TextField(23, 31, fill_char='0')
    originators_reference = fields.TextField(31, 35, fill_char='0')
    amount = fields.NumericField(35, 46)
    transaction_description = fields.TextField(46, 64)
    reference_number = fields.TextField(64, 82)
    date = fields.DateField(100, 106)


class BalanceRecord(BaseRecord):
    ledger_balance = fields.NumericField(36, 51)
    ledger_balance_type = fields.EnumField(51, 52, BalanceType)
    cleared_balance = fields.NumericField(52, 67)
    cleared_balance_type = fields.EnumField(67, 68, BalanceType)
    recorded_ledger_balance = fields.NumericField(68, 83)
    recorded_ledger_balance_type = fields.EnumField(83, 84, BalanceType)
    recorded_cleared_balance = fields.NumericField(84, 99)
    recorded_cleared_balance_type = fields.EnumField(99, 100, BalanceType)
    date = fields.DateField(100, 106)
