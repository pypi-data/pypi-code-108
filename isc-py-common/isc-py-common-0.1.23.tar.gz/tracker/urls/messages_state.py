from django.urls import path

from tracker.views import messages_state

urlpatterns = [

    path('Messages_state/Fetch/', messages_state.Messages_state_Fetch),
    path('Messages_state/Add', messages_state.Messages_state_Add),
    path('Messages_state/Update', messages_state.Messages_state_Update),
    path('Messages_state/Remove', messages_state.Messages_state_Remove),
    path('Messages_state/Lookup/', messages_state.Messages_state_Lookup),
    path('Messages_state/Info/', messages_state.Messages_state_Info),

]
