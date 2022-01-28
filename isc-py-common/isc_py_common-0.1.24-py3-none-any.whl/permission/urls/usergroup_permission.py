from django.urls import path
from permission.views import usergroup_permission

urlpatterns = [

    path('Usergroup_permission/Fetch/', usergroup_permission.Usergroup_permission_Fetch),
    path('Usergroup_permission/Add', usergroup_permission.Usergroup_permission_Add),
    path('Usergroup_permission/Update', usergroup_permission.Usergroup_permission_Update),
    path('Usergroup_permission/Remove', usergroup_permission.Usergroup_permission_Remove),
    path('Usergroup_permission/Lookup', usergroup_permission.Usergroup_permission_Lookup),

]
