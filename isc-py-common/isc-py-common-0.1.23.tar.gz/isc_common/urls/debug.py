from django.urls import path

from isc_common.views import debug

urlpatterns = [

    path('Debug/Fetch/', debug.Debug_Fetch),
    path('Debug/Add', debug.Debug_Add),
    path('Debug/Update', debug.Debug_Update),
    path('Debug/Remove', debug.Debug_Remove),
    path('Debug/Lookup/', debug.Debug_Lookup),
    path('Debug/Info/', debug.Debug_Info),
    path('Debug/Copy', debug.Debug_Copy),

]
