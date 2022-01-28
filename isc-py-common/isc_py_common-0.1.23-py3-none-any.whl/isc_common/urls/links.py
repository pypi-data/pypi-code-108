from django.urls import path

from isc_common.views import links

urlpatterns = [

    path('Links/Fetch/', links.Links_Fetch),
    path('Links/Add', links.Links_Add),
    path('Links/Update', links.Links_Update),
    path('Links/Remove', links.Links_Remove),
    path('Links/Lookup/', links.Links_Lookup),
    path('Links/Info/', links.Links_Info),
    path('Links/Copy', links.Links_Copy),

]
