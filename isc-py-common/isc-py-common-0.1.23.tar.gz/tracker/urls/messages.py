from django.urls import path

from tracker.views import messages

urlpatterns = [

    path('Messages/Fetch/', messages.Messages_Fetch),
    path('Messages/Fetch4Chat/', messages.Messages_Fetch4Chat),
    path('Messages/Add', messages.Messages_Add),
    path('Messages/Add_AutoError', messages.Messages_Add_Auto_Error),
    path('Messages/Update', messages.Messages_Update),
    path('Messages/Lookup/', messages.Messages_Lookup),
    path('Messages/Remove', messages.Messages_Remove),
    path('Messages/Info/', messages.Messages_Info),

]
