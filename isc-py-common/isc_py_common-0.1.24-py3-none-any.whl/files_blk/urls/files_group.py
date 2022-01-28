from django.urls import path
from files_blk.views import files_group

urlpatterns = [

    path('Files_group/Fetch/', files_group.Files_group_Fetch),
    path('Files_group/Add', files_group.Files_group_Add),
    path('Files_group/Update', files_group.Files_group_Update),
    path('Files_group/Remove', files_group.Files_group_Remove),
    path('Files_group/Lookup/', files_group.Files_group_Lookup),
    path('Files_group/Info/', files_group.Files_group_Info),
    path('Files_group/Copy', files_group.Files_group_Copy),

]
