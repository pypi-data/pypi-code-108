from django.urls import path

from reports.views import jasper_reports

urlpatterns = [

    path('Jasper_reports/Fetch/', jasper_reports.Jasper_reports_Fetch),
    path('Jasper_reports/Add', jasper_reports.Jasper_reports_Add),
    path('Jasper_reports/Update', jasper_reports.Jasper_reports_Update),
    path('Jasper_reports/Remove', jasper_reports.Jasper_reports_Remove),
    path('Jasper_reports/Lookup/', jasper_reports.Jasper_reports_Lookup),
    path('Jasper_reports/Info/', jasper_reports.Jasper_reports_Info),
    path('Jasper_reports/Copy', jasper_reports.Jasper_reports_Copy),

]
