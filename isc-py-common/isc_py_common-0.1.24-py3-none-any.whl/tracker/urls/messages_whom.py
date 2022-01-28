from django.urls import path

from tracker.views import messages_whom

urlpatterns = [

    path('Messages_whom/Fetch/', messages_whom.Messages_whom_Fetch),
    path('Messages_whom/Add', messages_whom.Messages_whom_Add),
    path('Messages_whom/Update', messages_whom.Messages_whom_Update),
    path('Messages_whom/Remove', messages_whom.Messages_whom_Remove),
    path('Messages_whom/Lookup/', messages_whom.Messages_whom_Lookup),
    path('Messages_whom/Info/', messages_whom.Messages_whom_Info),

]
