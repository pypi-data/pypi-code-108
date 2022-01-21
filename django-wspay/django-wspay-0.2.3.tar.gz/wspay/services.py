import calendar
from decimal import setcontext, Decimal, BasicContext
from datetime import datetime, date
from enum import Enum
import json
import hashlib
from typing import Tuple
import requests
import pytz

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse

from wspay.conf import settings, resolve
from wspay.forms import WSPaySignedForm, WSPayTransactionReportForm
from wspay.models import Transaction, WSPayRequest, TransactionHistory, WSPayRequestStatus
from wspay.signals import pay_request_created, pay_request_updated

EXP = Decimal('.01')
setcontext(BasicContext)


def render_wspay_form(form, request, additional_data=''):
    """
    Render the page that will submit signed data to wspay.

    Convert input data into WSPay format
    Generate wspay signature

    Return an HttpResponse that will submit the form data to wspay.
    """
    if not form.is_valid():
        raise ValidationError(form.errors)
    wspay_form = WSPaySignedForm(
        generate_wspay_form_data(form.cleaned_data.copy(), request, additional_data)
    )
    return render(
        request,
        'wspay/wspay_submit.html',
        {'form': wspay_form, 'submit_url': get_form_endpoint()}
    )


def generate_wspay_form_data(input_data, request, additional_data=''):
    """Process incoming data and prepare for POST to WSPay."""
    wspay_request = WSPayRequest.objects.create(
        cart_id=input_data['cart_id'],
        additional_data=additional_data,
    )
    # Send a signal
    pay_request_created.send_robust(WSPayRequest, instance=wspay_request)

    input_data['cart_id'] = str(wspay_request.request_uuid)

    price = input_data['price']
    assert price > 0, 'Price must be greater than 0'
    total_for_sign, total = build_price(price)

    shop_id = resolve(settings.WS_PAY_SHOP_ID)
    secret_key = resolve(settings.WS_PAY_SECRET_KEY)
    signature = generate_signature([
        shop_id,
        secret_key,
        input_data['cart_id'],
        secret_key,
        total_for_sign,
        secret_key,
    ])

    return_data = {
        'ShopID': shop_id,
        'ShoppingCartID': input_data['cart_id'],
        'Version': resolve(settings.WS_PAY_VERSION),
        'TotalAmount': total,
        'Signature': signature,
        'ReturnURL': request.build_absolute_uri(
            reverse('wspay:process-response', kwargs={'status': 'success'})
        ),
        'CancelURL': request.build_absolute_uri(
            reverse('wspay:process-response', kwargs={'status': 'cancel'})
        ),
        'ReturnErrorURL': request.build_absolute_uri(
            reverse('wspay:process-response', kwargs={'status': 'error'})
        ),
        'ReturnMethod': 'POST',
    }
    if input_data.get('first_name'):
        return_data['CustomerFirstName'] = input_data['first_name']
    if input_data.get('last_name'):
        return_data['CustomerLastName'] = input_data['last_name']
    if input_data.get('address'):
        return_data['CustomerAddress'] = input_data['address']
    if input_data.get('city'):
        return_data['CustomerCity'] = input_data['city']
    if input_data.get('zip_code'):
        return_data['CustomerZIP'] = input_data['zip_code']
    if input_data.get('country'):
        return_data['CustomerCountry'] = input_data['country']
    if input_data.get('email'):
        return_data['CustomerEmail'] = input_data['email']
    if input_data.get('phone'):
        return_data['CustomerPhone'] = input_data['phone']

    return return_data


def verify_response(form_class, data):
    """Verify validity and authenticity of wspay response."""
    form = form_class(data=data)
    if form.is_valid():
        signature = form.cleaned_data['Signature']
        shop_id = resolve(settings.WS_PAY_SHOP_ID)
        secret_key = resolve(settings.WS_PAY_SECRET_KEY)
        param_list = [
            shop_id,
            secret_key,
            data['ShoppingCartID'],
            secret_key,
            data['Success'],
            secret_key,
            data['ApprovalCode'],
            secret_key,
        ]
        expected_signature = generate_signature(param_list)
        if signature != expected_signature:
            raise ValidationError('Bad signature')

        return form.cleaned_data

    raise ValidationError('Form is not valid')


def verify_transaction_report(form_class, data):
    """Verify validity and authenticity of wspay transaction report."""
    form = form_class(data=data)
    if form.is_valid():
        signature = form.cleaned_data['Signature']
        shop_id = resolve(settings.WS_PAY_SHOP_ID)
        secret_key = resolve(settings.WS_PAY_SECRET_KEY)
        param_list = [
            shop_id,
            secret_key,
            form.cleaned_data['ActionSuccess'],
            form.cleaned_data['ApprovalCode'],
            secret_key,
            shop_id,
            form.cleaned_data['ApprovalCode'],
            form.cleaned_data['WsPayOrderId'],
        ]
        expected_signature = generate_signature(param_list)
        if signature != expected_signature:
            raise ValidationError('Bad signature')

        return form.cleaned_data

    raise ValidationError('Form is not valid')


def process_response_data(response_data, request_status):
    """Update corresponding WSPayRequest object with response data."""
    wspay_request = WSPayRequest.objects.get(
        request_uuid=response_data['ShoppingCartID'],
    )
    wspay_request.status = request_status.name
    wspay_request.response = json.dumps(response_data)
    wspay_request.save()

    if wspay_request.status == WSPayRequestStatus.COMPLETED.name:
        status_check(wspay_request.request_uuid)

    # Send a signal
    pay_request_updated.send_robust(
        WSPayRequest,
        instance=wspay_request,
        status=request_status
    )

    return wspay_request


def process_transaction_report(response_data):
    """Create a transaction and append to relevant wspay request."""
    request_uuid = response_data['ShoppingCartID']
    wspay_request = WSPayRequest.objects.get(
        request_uuid=request_uuid,
    )

    transaction_datetime = pytz.timezone(
        'Europe/Zagreb'
    ).localize(
        datetime.strptime(response_data['TransactionDateTime'], '%Y%m%d%H%M%S')
    )

    expires = datetime.strptime(response_data['ExpirationDate'], '%y%m').date()
    (_, day) = calendar.monthrange(expires.year, expires.month)
    expires = date(expires.year, expires.month, day)

    transaction, created = Transaction.objects.update_or_create(
        request_uuid=request_uuid,
        defaults={
            'stan': response_data['STAN'],
            'amount': Decimal(response_data['Amount']),
            'approval_code': response_data['ApprovalCode'],
            'ws_pay_order_id': response_data['WsPayOrderId'],
            'transaction_datetime': transaction_datetime,
            'authorized': bool(response_data['Authorized']),
            'completed': bool(response_data['Completed']),
            'voided': bool(response_data['Voided']),
            'refunded': bool(response_data['Refunded']),
            'can_complete': bool(response_data['CanBeCompleted']),
            'can_void': bool(response_data['CanBeVoided']),
            'can_refund': bool(response_data['CanBeRefunded']),
            'expiration_date': expires
        }
    )
    if created:
        wspay_request.transaction = transaction
        wspay_request.save()

    # TODO: Update status
    transaction_history = TransactionHistory.objects.create(
        payload=json.dumps(response_data)
    )
    transaction.history.add(transaction_history)

    # TODO: Send a signal

    return transaction


def status_check(request_uuid):
    """Check status of a transaction."""
    version = '2.0'
    shop_id = resolve(settings.WS_PAY_SHOP_ID)
    secret_key = resolve(settings.WS_PAY_SECRET_KEY)
    shopping_cart_id = str(request_uuid)
    signature = generate_signature([
        shop_id,
        secret_key,
        shopping_cart_id,
        secret_key,
        shop_id,
        shopping_cart_id
    ])

    data = {
        'Version': version,
        'ShopId': shop_id,
        'ShoppingCartId': shopping_cart_id,
        'Signature': signature
    }

    r = requests.post(
        f'{get_services_endpoint()}/statusCheck',
        data=data
    )
    return process_transaction_report(
        verify_transaction_report(WSPayTransactionReportForm, r.json())
    )


class TransactionAction(Enum):
    Complete = 'completion'
    Refund = 'refund'
    Void = 'void'


def complete(transaction: Transaction, amount: Decimal = None) -> Tuple[bool, str]:
    """Complete preauthorized transaction."""
    assert transaction.can_complete
    assert amount is None or amount <= transaction.amount
    return _transaction_action(
        transaction,
        int((amount or transaction.amount) * 100),
        TransactionAction.Complete
    )


def refund(transaction: Transaction, amount: Decimal = None) -> Tuple[bool, str]:
    """Refund refundable transaction."""
    assert transaction.can_refund
    assert amount is None or amount <= transaction.amount
    return _transaction_action(
        transaction,
        int((amount or transaction.amount) * 100),
        TransactionAction.Refund
    )


def void(transaction: Transaction) -> Tuple[bool, str]:
    """Void voidable transaction."""
    assert transaction.can_void
    return _transaction_action(
        transaction,
        int(transaction.amount * 100),
        TransactionAction.Void
    )


def _transaction_action(
    transaction: Transaction, amount: int, action: TransactionAction
) -> Tuple[bool, str]:
    version = '2.0'
    shop_id = resolve(settings.WS_PAY_SHOP_ID)
    secret_key = resolve(settings.WS_PAY_SECRET_KEY)

    signature = generate_signature([
        shop_id,
        transaction.ws_pay_order_id,
        secret_key,
        transaction.stan,
        secret_key,
        transaction.approval_code,
        secret_key,
        str(amount),
        secret_key,
        transaction.ws_pay_order_id
    ])

    data = {
        'Version': version,
        'WsPayOrderId': transaction.ws_pay_order_id,
        'ShopID': shop_id,
        'ApprovalCode': transaction.approval_code,
        'STAN': transaction.stan,
        'Amount': amount,
        'Signature': signature
    }
    r = requests.post(
        f'{get_services_endpoint()}/{action.value}',
        data=data
    )
    response_data = r.json()

    expected_signature = generate_signature([
        shop_id,
        secret_key,
        response_data['STAN'],
        response_data['ActionSuccess'],
        secret_key,
        response_data['ApprovalCode'],
        response_data['WsPayOrderId'],
    ])

    if response_data['Signature'] != expected_signature:
        raise ValidationError('Bad signature')

    # Per WSPay docs update approval_code in case it was changed
    new_approval_code = response_data['ApprovalCode']
    if transaction.approval_code != new_approval_code:
        transaction.approval_code = new_approval_code
        transaction.save()

    success = bool(int(response_data['ActionSuccess']))
    error_message = response_data.get('ErrorMessage', '')
    return success, error_message


def generate_signature(param_list):
    """Compute the signature."""
    result = []
    for x in param_list:
        result.append(str(x))
    return compute_hash(''.join(result))


def compute_hash(signature):
    """Compute the hash out of the given values."""
    return hashlib.sha512(signature.encode()).hexdigest()


def build_price(price):
    """
    Round to two decimals and return the tuple containing two variations of price.

    First element of the tuple is an int repr of price as as str 123.45 => '12345'
    Second element is a str that is a properly formatted price 00123.451 => '123,45'
    """
    rounded = price.quantize(EXP)
    _, digits, exp = rounded.as_tuple()

    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop

    for i in range(2):
        build(next() if digits else '0')
    build(',')
    if not digits:
        build('0')

    while digits:
        build(next())

    return str(int(rounded * 100)), ''.join(reversed(result))


def get_form_endpoint():
    """Return production or dev endpoint based on DEVELOPMENT setting."""
    development = resolve(settings.WS_PAY_DEVELOPMENT)
    if development:
        return 'https://formtest.wspay.biz/authorization.aspx'
    return 'https://form.wspay.biz/authorization.aspx'


def get_services_endpoint():
    """Return production or dev services endpoint based on DEVELOPMENT setting."""
    development = resolve(settings.WS_PAY_DEVELOPMENT)
    if development:
        return 'https://test.wspay.biz/api/services'
    return 'https://secure.wspay.biz/api/services'
