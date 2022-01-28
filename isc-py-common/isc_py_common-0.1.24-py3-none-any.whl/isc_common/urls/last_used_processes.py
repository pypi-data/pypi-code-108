from django.urls import path

from isc_common.views import last_used_processes

urlpatterns = [

    path('Last_used_processes/Fetch/', last_used_processes.Last_used_processes_Fetch),
    path('Last_used_processes/Add', last_used_processes.Last_used_processes_Add),
    path('Last_used_processes/Update', last_used_processes.Last_used_processes_Update),
    path('Last_used_processes/Remove', last_used_processes.Last_used_processes_Remove),
    path('Last_used_processes/Lookup/', last_used_processes.Last_used_processes_Lookup),
    path('Last_used_processes/Info/', last_used_processes.Last_used_processes_Info),
    path('Last_used_processes/Copy', last_used_processes.Last_used_processes_Copy),

]
