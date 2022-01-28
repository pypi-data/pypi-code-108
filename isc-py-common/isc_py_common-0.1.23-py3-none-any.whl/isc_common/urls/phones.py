from django.urls import path

from isc_common.views import phones

urlpatterns = [

    path('Phones/Fetch/', phones.Phones_Fetch),
    path('Phones/Add', phones.Phones_Add),
    path('Phones/Update', phones.Phones_Update),
    path('Phones/Remove', phones.Phones_Remove),
    path('Phones/Lookup/', phones.Phones_Lookup),
    path('Phones/Info/', phones.Phones_Info),
    path('Phones/Copy', phones.Phones_Copy),

]
