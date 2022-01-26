from enum import Enum


class TransactionCode(Enum):
    credit_automated_settlement_credit = '86'
    credit_dividend_interest_with_tax_voucher = '90'
    credit_sundry_credit = '93'
    credit_bacs_credit = '99'
    credit_building_society_interest = 'Z4'
    credit_dividend_interest_without_tax_voucher = 'Z5'
    credit_bacs_credit_returned_unapplied = 'RA'
    debit_direct_debit_first_payment = '01'
    debit_sundry_debit = '03'
    debit_cheque = '11'
    debit_direct_debit = '17'
    debit_direct_debit_representation = '18'
    debit_direct_debit_final_payment = '19'
    debit_unpaid_direct_debit_first_payment = 'U1'
    debit_unpaid_direct_debit = 'U7'
    debit_unpaid_direct_debit_representation = 'U8'
    debit_unpaid_direct_debit_final_payment = 'U9'
    balance_record = 'Y1'
    debit_total = '44'
    credit_total = '54'


class BalanceType(Enum):
    debit = 'D'
    credit = 'C'
