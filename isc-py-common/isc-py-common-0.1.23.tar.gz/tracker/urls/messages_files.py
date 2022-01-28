from django.urls import path

from tracker.views import messages_files, messages

urlpatterns = [

    path('Messages_files/Fetch/', messages_files.Messages_files_Fetch),
    path('Messages_files/Add', messages_files.Messages_files_Add),
    path('Messages_files/Update', messages_files.Messages_files_Update),
    path('Messages_files/Remove', messages_files.Messages_files_Remove),
    path('Messages_files/Lookup/', messages_files.Messages_files_Lookup),
    path('Messages_files/Info/', messages_files.Messages_files_Info),
    path('Messages_files/Copy', messages_files.Messages_files_Copy),
    path('Messages_files/Upload', messages.Messages_UploadFile),
    path('Messages_files/Upload1', messages.Messages_UploadFile1),
    path('Messages_files/Confirm_reading', messages.Messages_Confirm_reading),
    path('Messages_files/Download/<int:id>/', messages.Message_DownloadFile),

]
