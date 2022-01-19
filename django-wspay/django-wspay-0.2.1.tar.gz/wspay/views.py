from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, View
from django.http.response import HttpResponse

from wspay.conf import settings, resolve
from wspay.forms import (
    UnprocessedPaymentForm, WSPayErrorResponseForm, WSPaySuccessResponseForm,
    WSPayCancelResponseForm, WSPayTransactionReportForm,
)
from wspay.models import WSPayRequestStatus
from wspay.services import (
    process_response_data, process_transaction_report, render_wspay_form,
    verify_response, verify_transaction_report
)
from wspay.signals import process_response_pre_redirect


class ProcessView(FormView):
    """Receive payment data and prepare it for WSPay."""

    form_class = UnprocessedPaymentForm
    template_name = 'wspay/error.html'

    def form_valid(self, form):
        return render_wspay_form(form, self.request)


class PaymentStatus:
    SUCCESS = 'success'
    ERROR = 'error'
    CANCEL = 'cancel'


class ProcessResponseView(View):
    """Handle success, error and cancel."""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        form_class, request_status, redirect_url = self._unpack_response_status(kwargs['status'])

        data = request.POST if request.method == 'POST' else request.GET
        wspay_request = process_response_data(
            verify_response(form_class, data),
            request_status
        )

        process_response_pre_redirect.send_robust(
            self.__class__,
            wspay_request=wspay_request, http_request=request, redirect_url=redirect_url,
        )

        return redirect(redirect_url)

    def _unpack_response_status(self, status):
        assert status in [PaymentStatus.SUCCESS, PaymentStatus.ERROR, PaymentStatus.CANCEL]
        if status == PaymentStatus.SUCCESS:
            form_class = WSPaySuccessResponseForm
            request_status = WSPayRequestStatus.COMPLETED
            redirect_url = resolve(settings.WS_PAY_SUCCESS_URL)
        elif status == PaymentStatus.CANCEL:
            form_class = WSPayCancelResponseForm
            request_status = WSPayRequestStatus.CANCELLED
            redirect_url = resolve(settings.WS_PAY_CANCEL_URL)
        else:
            form_class = WSPayErrorResponseForm
            request_status = WSPayRequestStatus.FAILED
            redirect_url = resolve(settings.WS_PAY_ERROR_URL)

        return form_class, request_status, redirect_url


class TransactionReportView(View):
    """Transaction response - CallbackURL."""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('dispatch', request.method)
        data = request.POST if request.method == 'POST' else request.GET
        print(data)
        process_transaction_report(
            verify_transaction_report(WSPayTransactionReportForm, data)
        )
        return HttpResponse('OK')


class TestView(FormView):
    """Simple View to test the ProcessView."""

    template_name = 'wspay/test.html'
    form_class = UnprocessedPaymentForm
