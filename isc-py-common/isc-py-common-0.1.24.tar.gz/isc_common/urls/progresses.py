from django.urls import path

from isc_common.views import progresses

urlpatterns = [

    path('Progresses/Fetch/', progresses.Progresses_Fetch),
    path('Progresses/Add', progresses.Progresses_Add),
    path('Progresses/Update', progresses.Progresses_Update),
    path('Progresses/Remove', progresses.Progresses_Remove),
    path('Progresses/Lookup/', progresses.Progresses_Lookup),
    path('Progresses/Info/', progresses.Progresses_Info),
    path('Progresses/Copy', progresses.Progresses_Copy),
    path('Progresses/Resore/', progresses.Progresses_Resore),

]
