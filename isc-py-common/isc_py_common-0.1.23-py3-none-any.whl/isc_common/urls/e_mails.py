from django.urls import path

from isc_common.views import e_mails

urlpatterns = [

    path('E_mails/Fetch/', e_mails.E_mails_Fetch),
    path('E_mails/Add', e_mails.E_mails_Add),
    path('E_mails/Update', e_mails.E_mails_Update),
    path('E_mails/Remove', e_mails.E_mails_Remove),
    path('E_mails/Lookup/', e_mails.E_mails_Lookup),
    path('E_mails/Info/', e_mails.E_mails_Info),
    path('E_mails/Copy', e_mails.E_mails_Copy),

]
