from django.urls import path

from one_c.views import files_1c

urlpatterns = [

    path('Files_1c/Fetch/', files_1c.Files_1c_Fetch),
    path('Files_1c/Add', files_1c.Files_1c_Add),
    path('Files_1c/Update', files_1c.Files_1c_Update),
    path('Files_1c/Remove', files_1c.Files_1c_Remove),
    path('Files_1c/Lookup/', files_1c.Files_1c_Lookup),
    path('Files_1c/Info/', files_1c.Files_1c_Info),

]
