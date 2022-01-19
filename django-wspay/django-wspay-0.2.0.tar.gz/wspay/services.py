from decimal import setcontext, Decimal, BasicContext
import json
import hashlib

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse

from wspay.conf import settings, resolve
from wspay.forms import WSPaySignedForm
from wspay.models import WSPayRequest, WSPayTransaction
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
        {'form': wspay_form, 'submit_url': resolve(settings.WS_PAY_PAYMENT_ENDPOINT)}
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
    # TODO: Update status
    transaction = WSPayTransaction.objects.create(
        payload=json.dumps(response_data)
    )
    wspay_request.transactions.add(transaction)

    # TODO: Send a signal

    return transaction


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


def get_endpoint():
    """Return production or dev endpoint based on DEVELOPMENT setting."""
    development = resolve(settings.WS_PAY_DEVELOPMENT)
    if development:
        return 'https://formtest.wspay.biz/authorization.aspx'
    return 'https://form.wspay.biz/authorization.aspx'
