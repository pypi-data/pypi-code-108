# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.urls import reverse

from aparnik.settings import aparnik_settings
from .models import Payment, PaymentBank
from azbankgateways import bankfactories, default_settings as bank_settings


# Create your views here.
def payment(request, uuid):
    payments_obj = get_list_or_404(Payment.objects.all(), uuid=uuid)
    pay_obj = payments_obj[0]

    if pay_obj.order_obj.status == Payment.STATUS_WAITING and pay_obj.status == Payment.STATUS_WAITING:

        if aparnik_settings.BANK_ACTIVE:
            order = pay_obj.order_obj
            amount = order.get_total_cost()
            user_mobile_number = order.user.username
            factory = bankfactories.BankFactory()
            bank = factory.create()
            bank.set_request(request)
            bank.set_amount(amount)
            # bank.set_client_callback_url(reverse('callback-gateway'))
            bank.set_client_callback_url(reverse('aparnik:shops:payments:call-back'))
            bank.set_mobile_number(user_mobile_number)
            bank_record = bank.ready()
            PaymentBank.objects.create(
                bank_record=bank_record,
                payment=pay_obj
            )
            return bank.redirect_gateway()
        else:
            pay_obj.success()

    context = {
        'obj': pay_obj,
        'app_url': request.build_absolute_uri(pay_obj.get_api_uri()),
    }

    if pay_obj.is_success():
        return render(request=request, template_name='suit/paysuc.html', status=200, context=context)

    return render(request=request, template_name='suit/payunsuc.html', status=400, context=context)


def callback_view(request):
    tracking_code = request.GET.get(bank_settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        raise Http404

    payment_bank = get_object_or_404(
        PaymentBank,
        bank_record__tracking_code=tracking_code
    )
    if payment_bank.bank_record.is_success:
        if payment_bank.payment.status == Payment.STATUS_WAITING:
            payment_bank.payment.success()
    else:
        payment_bank.payment.cancel()
    return redirect(request.build_absolute_uri(payment_bank.payment.get_url()))
