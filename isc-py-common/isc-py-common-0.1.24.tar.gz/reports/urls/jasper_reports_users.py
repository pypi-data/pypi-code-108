from django.urls import path

from reports.views import jasper_reports_users

urlpatterns = [

    path('Jasper_reports_users/Fetch/', jasper_reports_users.Jasper_reports_users_Fetch),
    path('Jasper_reports_users/Add', jasper_reports_users.Jasper_reports_users_Add),
    path('Jasper_reports_users/Update', jasper_reports_users.Jasper_reports_users_Update),
    path('Jasper_reports_users/Remove', jasper_reports_users.Jasper_reports_users_Remove),
    path('Jasper_reports_users/Lookup/', jasper_reports_users.Jasper_reports_users_Lookup),
    path('Jasper_reports_users/Info/', jasper_reports_users.Jasper_reports_users_Info),
    path('Jasper_reports_users/Copy', jasper_reports_users.Jasper_reports_users_Copy),

]
