from django.urls import path
from isc_common.auth.views.user_group import UserGroup_Fetch, UserGroup_Add, UserGroup_Update, UserGroup_Remove, UserGroup_Info, UserGroup_Lookup

urlpatterns = [

    path('UserGroups/Fetch/', UserGroup_Fetch),
    path('UserGroups/Add', UserGroup_Add),
    path('UserGroups/Update', UserGroup_Update),
    path('UserGroups/Remove', UserGroup_Remove),
    path('UserGroups/Lookup/', UserGroup_Lookup),
    path('UserGroups/Info/', UserGroup_Info),

]
