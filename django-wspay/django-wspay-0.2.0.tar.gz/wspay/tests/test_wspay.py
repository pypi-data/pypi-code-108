import pytest
import responses
import requests

from django.urls import reverse
from django.test.client import RequestFactory, Client
from wspay.conf import settings, resolve

from wspay.forms import UnprocessedPaymentForm, WSPaySignedForm
from wspay.models import WSPayRequest
from wspay.services import generate_wspay_form_data, generate_signature, get_endpoint

from wspay.tests.utils import TRANSACTION_REPORT


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
    assert secret_key == 'MojSecret'

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
    settings.WS_PAY_SHOP_ID = 'MYSHOP'
    settings.WS_PAY_SECRET_KEY = '3DfEO2B5Jjm4VC1Q3vEh'
    TRANSACTION_REPORT['ShoppingCartID'] = str(request.request_uuid)
    r = Client().post(
        reverse('wspay:transaction-report'),
        TRANSACTION_REPORT,
    )
    assert r.status_code == 200
    assert r.content == b'OK'
    assert request.transactions.count() == 1


def test_conf_resolver():
    """Test conf resolver when settings are callables or dotted path to a callable."""
    assert resolve(settings.WS_PAY_SHOP_ID) == 'MojShop'
    assert resolve(settings.WS_PAY_SECRET_KEY) == 'MojSecret'


def test_get_endpoint(settings):
    """Test get_endpoint setting."""
    assert settings.WS_PAY_DEVELOPMENT is True
    assert get_endpoint() == 'https://formtest.wspay.biz/authorization.aspx'

    settings.WS_PAY_DEVELOPMENT = False
    assert get_endpoint() == 'https://form.wspay.biz/authorization.aspx'
