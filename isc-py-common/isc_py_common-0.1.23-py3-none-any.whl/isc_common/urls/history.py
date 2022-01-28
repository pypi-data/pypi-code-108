from django.urls import path

from isc_common.views import history

urlpatterns = [

    path('History/Fetch/', history.History_Fetch),
    path('History/Add', history.History_Add),
    path('History/Update', history.History_Update),
    path('History/Remove', history.History_Remove),
    path('History/Lookup/', history.History_Lookup),
    path('History/Info/', history.History_Info),

]
