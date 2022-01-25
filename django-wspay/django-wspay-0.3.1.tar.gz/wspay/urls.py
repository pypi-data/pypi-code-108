from django.conf import settings
from django.urls import path, re_path

from wspay.views import ProcessView, ProcessResponseView, TestView, TransactionReportView

app_name = 'wspay'

urlpatterns = [
    path(
        'process/',
        ProcessView.as_view(),
        name='process'
    ),
    re_path(
        r'^response/(?P<status>success|error|cancel)/$',
        ProcessResponseView.as_view(),
        name='process-response'
    ),
    path(
        'transaction-report/',
        TransactionReportView.as_view(),
        name='transaction-report'
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            'test/',
            TestView.as_view(),
            name='test'
        ),
    ]
