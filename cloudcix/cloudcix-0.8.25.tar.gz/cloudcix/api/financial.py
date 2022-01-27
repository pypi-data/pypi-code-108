from cloudcix.client import Client


class Financial:
    """
    The Financial Application exposes a suite of services that together implement a full accounting system based on
    double entry bookkeeping.
    """
    _application_name = 'financial'

    account_purchase_adjustment = Client(
        _application_name,
        'account_purchase_adjustment/',
    )
    account_purchase_adjustment_contra = Client(
        _application_name,
        'account_purchase_adjustment_contra/address/{source_id}/',
    )
    account_purchase_debit_note = Client(
        _application_name,
        'account_purchase_debit_note/',
    )
    account_purchase_debit_note_contra = Client(
        _application_name,
        'account_purchase_debit_note_contra/address/{source_id}/',
    )
    account_purchase_invoice = Client(
        _application_name,
        'account_purchase_invoice/',
    )
    account_purchase_invoice_contra = Client(
        _application_name,
        'account_purchase_invoice_contra/address/{source_id}/',
    )
    account_purchase_payment = Client(
        _application_name,
        'account_purchase_payment/',
    )
    account_purchase_payment_contra = Client(
        _application_name,
        'account_purchase_payment_contra/address/{source_id}/',
    )
    account_sale_adjustment = Client(
        _application_name,
        'account_sale_adjustment/',
    )
    account_sale_adjustment_contra = Client(
        _application_name,
        'account_sale_adjustment_contra/address/{source_id}/',
    )
    account_sale_credit_note = Client(
        _application_name,
        'account_sale_credit_note/',
    )
    account_sale_credit_note_contra = Client(
        _application_name,
        'account_sale_credit_note_contra/address/{source_id}/',
    )
    account_sale_invoice = Client(
        _application_name,
        'account_sale_invoice/',
    )
    account_sale_invoice_contra = Client(
        _application_name,
        'account_sale_invoice_contra/address/{source_id}/',
    )
    account_sale_payment = Client(
        _application_name,
        'account_sale_payment/',
    )
    account_sale_payment_contra = Client(
        _application_name,
        'account_sale_payment_contra/address/{source_id}/',
    )
    allocation = Client(
        _application_name,
        'allocation/',
    )
    balance_sheet = Client(
        _application_name,
        'balance_sheet/',
    )
    cash_purchase_debit_note = Client(
        _application_name,
        'cash_purchase_debit_note/',
    )
    cash_purchase_debit_note_contra = Client(
        _application_name,
        'cash_purchase_debit_note_contra/address/{source_id}/',
    )
    cash_purchase_invoice = Client(
        _application_name,
        'cash_purchase_invoice/',
    )
    cash_purchase_invoice_contra = Client(
        _application_name,
        'cash_purchase_invoice_contra/address/{source_id}/',
    )
    cash_purchase_receipt = Client(
        _application_name,
        'cash_purchase_receipt/',
    )
    cash_purchase_refund = Client(
        _application_name,
        'cash_purchase_refund/',
    )
    cash_sale_credit_note = Client(
        _application_name,
        'cash_sale_credit_note/',
    )
    cash_sale_credit_note_contra = Client(
        _application_name,
        'cash_sale_credit_note_contra/address/{source_id}/',
    )
    cash_sale_invoice = Client(
        _application_name,
        'cash_sale_invoice/',
    )
    cash_sale_invoice_contra = Client(
        _application_name,
        'cash_sale_invoice_contra/address/{source_id}/',
    )
    cash_sale_receipt = Client(
        _application_name,
        'cash_sale_receipt/',
    )
    cash_sale_refund = Client(
        _application_name,
        'cash_sale_refund/',
    )
    cloud_bill = Client(
        _application_name,
        'cloud_bill/{project_id}/',
    )
    credit_limit = Client(
        _application_name,
        'credit_limit/',
    )
    creditor_account_history = Client(
        _application_name,
        'creditor_account/{id}/history/',
    )
    creditor_account_statement = Client(
        _application_name,
        'creditor_account/{id}/statement/',
    )
    creditor_ledger = Client(
        _application_name,
        'creditor_ledger/',
    )
    creditor_ledger_aged = Client(
        _application_name,
        'creditor_ledger/aged/',
    )
    creditor_ledger_contra_transaction = Client(
        _application_name,
        'creditor_ledger/contra_transaction/',
    )
    creditor_ledger_transaction = Client(
        _application_name,
        'creditor_ledger/transaction/',
    )
    debtor_account_history = Client(
        _application_name,
        'debtor_account/{id}/history/',
    )
    debtor_account_statement = Client(
        _application_name,
        'debtor_account/{id}/statement/',
    )
    debtor_ledger = Client(
        _application_name,
        'debtor_ledger/',
    )
    debtor_ledger_aged = Client(
        _application_name,
        'debtor_ledger/aged/',
    )
    debtor_ledger_contra_transaction = Client(
        _application_name,
        'debtor_ledger/contra_transaction/',
    )
    debtor_ledger_transaction = Client(
        _application_name,
        'debtor_ledger/transaction/',
    )
    global_nominal_account = Client(
        _application_name,
        'global_nominal_account/',
    )
    journal_entry = Client(
        _application_name,
        'journal_entry/',
    )
    nominal_account_history = Client(
        _application_name,
        'nominal_account/{id}/history/',
    )
    nominal_account_type = Client(
        _application_name,
        'nominal_account_type/',
    )
    nominal_contra = Client(
        _application_name,
        'nominal_contra/',
    )
    payment_method = Client(
        _application_name,
        'payment_method/',
    )
    period_end = Client(
        _application_name,
        'period_end/',
    )
    profit_and_loss = Client(
        _application_name,
        'profit_and_loss/',
    )
    purchases_analysis = Client(
        _application_name,
        'purchases_analysis/',
    )
    purchases_by_country = Client(
        _application_name,
        'purchases_by_country/',
    )
    purchases_by_territory = Client(
        _application_name,
        'purchases_by_territory/{territory_id}/',
    )
    rtd = Client(
        _application_name,
        'rtd/',
    )
    sales_by_country = Client(
        _application_name,
        'sales_by_country/',
    )
    sales_analysis = Client(
        _application_name,
        'sales_analysis/',
    )
    sales_by_territory = Client(
        _application_name,
        'sales_by_territory/{territory_id}/',
    )
    statement = Client(
        _application_name,
        'statement/',
    )
    statement_log = Client(
        _application_name,
        'statement_log/',
    )
    statement_settings = Client(
        _application_name,
        'statement_settings/',
    )
    tax_rate = Client(
        _application_name,
        'tax_rate/',
    )
    trial_balance = Client(
        _application_name,
        'trial_balance/',
    )
    vat3 = Client(
        _application_name,
        'vat3/',
    )
    vies_purchases = Client(
        _application_name,
        'vies_purchases/',
    )
    vies_sales = Client(
        _application_name,
        'vies_sales/',
    )
    year_end = Client(
        _application_name,
        'YearEnd/',
    )
