from django.urls import path

from isc_common.auth.views import user_phones

urlpatterns = [

    path('User_phones/Fetch/', user_phones.User_phones_Fetch),
    path('User_phones/Add', user_phones.User_phones_Add),
    path('User_phones/Update', user_phones.User_phones_Update),
    path('User_phones/Remove', user_phones.User_phones_Remove),
    path('User_phones/Lookup/', user_phones.User_phones_Lookup),
    path('User_phones/Info/', user_phones.User_phones_Info),
    path('User_phones/Copy', user_phones.User_phones_Copy),

]
