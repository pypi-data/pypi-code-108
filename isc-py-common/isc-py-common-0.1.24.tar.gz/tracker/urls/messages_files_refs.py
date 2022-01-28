from django.urls import path

from tracker.views import messages_files_refs

urlpatterns = [

    path('Messages_files_refs/Fetch/', messages_files_refs.Messages_files_refs_Fetch),
    path('Messages_files_refs/Add', messages_files_refs.Messages_files_refs_Add),
    path('Messages_files_refs/Update', messages_files_refs.Messages_files_refs_Update),
    path('Messages_files_refs/Remove', messages_files_refs.Messages_files_refs_Remove),
    path('Messages_files_refs/Lookup/', messages_files_refs.Messages_files_refs_Lookup),
    path('Messages_files_refs/Info/', messages_files_refs.Messages_files_refs_Info),
    path('Messages_files_refs/Copy', messages_files_refs.Messages_files_refs_Copy),

]
