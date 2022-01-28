from django.urls import path

from events.views import event_type_users

urlpatterns = [

    path('Event_type_users/Fetch/', event_type_users.Event_type_users_Fetch),
    path('Event_type_users/Add', event_type_users.Event_type_users_Add),
    path('Event_type_users/Update', event_type_users.Event_type_users_Update),
    path('Event_type_users/Remove', event_type_users.Event_type_users_Remove),
    path('Event_type_users/Lookup/', event_type_users.Event_type_users_Lookup),
    path('Event_type_users/Info/', event_type_users.Event_type_users_Info),
    path('Event_type_users/Copy', event_type_users.Event_type_users_Copy),

]
