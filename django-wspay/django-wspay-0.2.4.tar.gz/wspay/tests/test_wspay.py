from datetime import date
from decimal import Decimal
from unittest.mock import patch
import pytest
import responses
import requests

from django.urls import reverse
from django.utils import timezone as tz
from django.test.client import RequestFactory, Client
from wspay.conf import settings, resolve

from wspay.forms import UnprocessedPaymentForm, WSPaySignedForm, WSPayTransactionReportForm
from wspay.models import Transaction, WSPayRequest
from wspay import services
from wspay.services import (
    generate_wspay_form_data, generate_signature, get_form_endpoint, get_services_endpoint,
    process_transaction_report, status_check, verify_transaction_report
)

from wspay.tests.utils import STATUS_CHECK_RESPONSE, TRANSACTION_REPORT, MockResponse


def test_incoming_data_form():
    """Test the form that receives cart and user details."""
    form = UnprocessedPaymentForm()
    assert form.is_valid() is False
    form = UnprocessedPaymentForm({'user_id': 1, 'cart_id': 1, 'price': 1})
    assert form.is_valid()


@pytest.mark.django_db
def test_wspay_encode():
    """Test the processing function which prepares the data for WSPay."""
    shop_id = resolve(settings.WS_PAY_SHOP_ID)
    secret_key = resolve(settings.WS_PAY_SECRET_KEY)
    assert shop_id == 'MojShop'
    assert secret_key == '3DfEO2B5Jjm4VC1Q3vEh'

    return_data = {
        'ShopID': shop_id,
        'Version': resolve(settings.WS_PAY_VERSION),
        'TotalAmount': '10,00',
        'ReturnURL': (
            'http://testserver' + reverse('wspay:process-response', kwargs={'status': 'success'})
        ),
        'CancelURL': (
            'http://testserver' + reverse('wspay:process-response', kwargs={'status': 'cancel'})
        ),
        'ReturnErrorURL': (
            'http://testserver' + reverse('wspay:process-response', kwargs={'status': 'error'})
        ),
        'ReturnMethod': 'POST',
    }

    incoming_form = UnprocessedPaymentForm({'cart_id': 1, 'price': 10})
    if (incoming_form.is_valid()):
        form_data = generate_wspay_form_data(
            incoming_form.cleaned_data.copy(), RequestFactory().get('/')
        )

    req = WSPayRequest.objects.get()
    return_data['ShoppingCartID'] = str(req.request_uuid)
    return_data['Signature'] = generate_signature([
        shop_id,
        secret_key,
        str(req.request_uuid),
        secret_key,
        '1000',
        secret_key,
    ])

    assert return_data == form_data


@pytest.mark.django_db
def test_wspay_form():
    """Test the form that is used to make a WSPay POST request."""
    form = WSPaySignedForm()
    assert form.is_valid() is False

    incoming_form = UnprocessedPaymentForm({'user_id': 1, 'cart_id': 1, 'price': 1})
    if (incoming_form.is_valid()):
        form_data = generate_wspay_form_data(
            incoming_form.cleaned_data.copy(),
            RequestFactory().get('/')
        )

    form = WSPaySignedForm(form_data)
    assert form.is_valid()
    form = form.cleaned_data

    responses.add(responses.POST, 'https://formtest.wspay.biz/authorization.aspx', status=200)
    response = requests.post('https://formtest.wspay.biz/authorization.aspx', form)
    assert response.status_code == 200


@pytest.mark.django_db
def test_transaction_update(settings):
    """Test wspay transaction update callback."""
    request = WSPayRequest.objects.create(cart_id=1)
    TRANSACTION_REPORT['ShoppingCartID'] = str(request.request_uuid)
    r = Client().post(
        reverse('wspay:transaction-report'),
        TRANSACTION_REPORT,
    )
    assert r.status_code == 200
    assert r.content == b'OK'

    request.refresh_from_db()
    assert request.transaction_id is not None

    tx = request.transaction
    assert tx.transaction_datetime == tz.datetime(2020, 4, 23, 8, 24, 57, tzinfo=tz.utc)
    assert tx.approval_code == '961792'
    assert tx.ws_pay_order_id == '96a5f58f-764c-4640-90ea-591280893bff'
    assert tx.stan == '38967'
    assert tx.amount == Decimal('78')
    assert tx.history.count() == 1
    assert tx.authorized is True
    assert tx.completed is False
    assert tx.refunded is False
    assert tx.voided is False
    assert tx.can_complete is True
    assert tx.can_void is True
    assert tx.can_refund is False
    assert tx.expiration_date == date(2020, 6, 30)


@pytest.mark.django_db
def test_status_check():
    """Test WSPay status check method."""
    request = WSPayRequest.objects.create(cart_id=1)

    STATUS_CHECK_RESPONSE.update({'ShoppingCartID': str(request.request_uuid)})

    response = MockResponse(status_code=200, json_data=STATUS_CHECK_RESPONSE)
    with patch.object(requests, 'post', return_value=response):
        status_check(request.request_uuid)

    request.refresh_from_db()
    assert request.transaction_id is not None

    tx = request.transaction
    assert tx.transaction_datetime == tz.datetime(2022, 1, 19, 20, 16, 35, tzinfo=tz.utc)
    assert tx.approval_code == '307006'
    assert tx.ws_pay_order_id == '4ae43ae9-af8f-4ddd-8a21-7864f9fe81fb'
    assert tx.stan == '128729'
    assert tx.amount == Decimal('80.55')
    assert tx.history.count() == 1
    assert tx.authorized is True
    assert tx.completed is False
    assert tx.refunded is False
    assert tx.voided is False
    assert tx.can_complete is True
    assert tx.can_void is True
    assert tx.can_refund is False
    assert tx.expiration_date == date(2022, 12, 31)


def test_conf_resolver():
    """Test conf resolver when settings are callables or dotted path to a callable."""
    assert resolve(settings.WS_PAY_SHOP_ID) == 'MojShop'
    assert resolve(settings.WS_PAY_SECRET_KEY) == '3DfEO2B5Jjm4VC1Q3vEh'


def test_get_form_endpoint(settings):
    """Test get_form_endpoint function."""
    assert settings.WS_PAY_DEVELOPMENT is True
    assert get_form_endpoint() == 'https://formtest.wspay.biz/authorization.aspx'

    settings.WS_PAY_DEVELOPMENT = False
    assert get_form_endpoint() == 'https://form.wspay.biz/authorization.aspx'


def test_get_services_endpoint(settings):
    """Test get_services_endpoint setting."""
    assert settings.WS_PAY_DEVELOPMENT is True
    assert get_services_endpoint() == 'https://test.wspay.biz/api/services'

    settings.WS_PAY_DEVELOPMENT = False
    assert get_services_endpoint() == 'https://secure.wspay.biz/api/services'


@pytest.mark.django_db
@pytest.mark.parametrize(['action', 'allow_attr'], [
    ('complete', 'can_complete'),
    ('refund', 'can_refund'),
    ('void', 'can_void')
])
def test_transaction_actions(action, allow_attr):
    """Test `complete`, `refund` and `void` function."""
    request = WSPayRequest.objects.create(
        cart_id=1,
    )
    TRANSACTION_REPORT['ShoppingCartID'] = str(request.request_uuid)
    transaction = process_transaction_report(
        verify_transaction_report(WSPayTransactionReportForm, TRANSACTION_REPORT)
    )
    assert Transaction.objects.count() == 1

    action_func = getattr(services, action)

    if action != 'void':
        with pytest.raises(AssertionError):
            action_func(transaction, Decimal(100))

    setattr(transaction, allow_attr, False)
    transaction.save()
    with pytest.raises(AssertionError):
        action_func(transaction)

    setattr(transaction, allow_attr, True)
    transaction.save()
    json_data = {
        'WsPayOrderId': "c1c7ad40-6293-417e-9dff-8390822efcb6",
        "ShopID": "MYSHOP",
        "ApprovalCode": "559974",
        "STAN": "38400",
        "ErrorMessage": "",
        "ActionSuccess": "1",
        "Signature": ''.join([
            '9f3c7e03bfe3937a1dd82fec8de8719c12ce01679fcf0f96070436b094f7192dab0ff1c8bef',
            '64d65f167049c9df4ca46a12efa1de2a52cba83b20c9cda88ff2f',
        ])
    }
    response = MockResponse(status_code=200, json_data=json_data)
    with patch.object(requests, 'post', return_value=response):
        action_func(transaction)
