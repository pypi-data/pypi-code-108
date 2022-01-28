from django.urls import path

from isc_common.views import deleted_progresses

urlpatterns = [

    path('Deleted_progresses/Fetch/', deleted_progresses.Deleted_progresses_Fetch),
    path('Deleted_progresses/Add', deleted_progresses.Deleted_progresses_Add),
    path('Deleted_progresses/Update', deleted_progresses.Deleted_progresses_Update),
    path('Deleted_progresses/Remove', deleted_progresses.Deleted_progresses_Remove),
    path('Deleted_progresses/Lookup/', deleted_progresses.Deleted_progresses_Lookup),
    path('Deleted_progresses/Info/', deleted_progresses.Deleted_progresses_Info),
    path('Deleted_progresses/Copy', deleted_progresses.Deleted_progresses_Copy),

]
