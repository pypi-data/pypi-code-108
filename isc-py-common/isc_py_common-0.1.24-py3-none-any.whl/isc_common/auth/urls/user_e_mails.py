from django.urls import path

from isc_common.auth.views import user_e_mails

urlpatterns = [

    path('User_e_mails/Fetch/', user_e_mails.User_e_mails_Fetch),
    path('User_e_mails/Add', user_e_mails.User_e_mails_Add),
    path('User_e_mails/Update', user_e_mails.User_e_mails_Update),
    path('User_e_mails/Remove', user_e_mails.User_e_mails_Remove),
    path('User_e_mails/Lookup/', user_e_mails.User_e_mails_Lookup),
    path('User_e_mails/Info/', user_e_mails.User_e_mails_Info),
    path('User_e_mails/Copy', user_e_mails.User_e_mails_Copy),

]
