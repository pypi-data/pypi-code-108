from django.urls import path

from tracker.views import messages_view

urlpatterns = [

    path('Messages_view/Fetch/', messages_view.Messages_view_Fetch),
    path('Messages_view/FetchAdmin/', messages_view.Messages_view_FetchAdmin),
    path('Messages_view/Add', messages_view.Messages_view_Add),
    path('Messages_view/Update', messages_view.Messages_view_Update),
    path('Messages_view/Remove', messages_view.Messages_view_Remove),
    path('Messages_view/Lookup/', messages_view.Messages_view_Lookup),
    path('Messages_view/Info/', messages_view.Messages_view_Info),

]
