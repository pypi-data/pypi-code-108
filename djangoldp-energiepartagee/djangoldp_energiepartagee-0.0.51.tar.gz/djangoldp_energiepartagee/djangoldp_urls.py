"""djangoldp uploader URL Configuration"""

from django.conf import settings
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from djangoldp_energiepartagee.views import ExportContributions, GeneratePdfCall, GeneratePdfReceipt, ContributionsCallView, ContributionsReminderView, ContributionsVentilationView

urlpatterns = [
    url(r'^contributions/call/$', csrf_exempt(ContributionsCallView.as_view()), name='contributions-call'),
    url(r'^contributions/reminder/$', csrf_exempt(ContributionsReminderView.as_view()), name='contributions-reminder'),
    url(r'^contributions/ventilation/$', csrf_exempt(ContributionsVentilationView.as_view()), name='contributions-ventilation'),
    url(r'^contributions/call_pdf/(?P<pk>.+)/$', csrf_exempt(GeneratePdfCall.as_view()), name="generate_callpdf_fromhtml"),
    url(r'^contributions/receipt_pdf/(?P<pk>.+)/$', csrf_exempt(GeneratePdfReceipt.as_view()), name="generate_receiptpdf_fromhtml"),
    url(r'^contributions/csv/$', csrf_exempt(ExportContributions.as_view()), name='export_contributions'),
]