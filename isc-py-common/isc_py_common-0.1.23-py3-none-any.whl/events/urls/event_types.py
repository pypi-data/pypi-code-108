from django.urls import path

from events.views import event_types

urlpatterns = [

    path('Event_types/Fetch/', event_types.Event_types_Fetch),
    path('Event_types/Add', event_types.Event_types_Add),
    path('Event_types/Update', event_types.Event_types_Update),
    path('Event_types/Remove', event_types.Event_types_Remove),
    path('Event_types/Lookup/', event_types.Event_types_Lookup),
    path('Event_types/Info/', event_types.Event_types_Info),
    path('Event_types/Copy', event_types.Event_types_Copy),

]
