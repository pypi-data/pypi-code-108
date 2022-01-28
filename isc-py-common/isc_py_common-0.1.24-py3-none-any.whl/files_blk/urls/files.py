from django.urls import path

from files_blk.views import files

urlpatterns = [

    path('Files/Fetch/', files.Files_Fetch),
    path('Files/Add', files.Files_Add),
    path('Files/Update', files.Files_Update),
    path('Files/Remove', files.Files_Remove),
    path('Files/Lookup/', files.Files_Lookup),
    path('Files/Info/', files.Files_Info),
    path('Files/Copy', files.Files_Copy),

]
