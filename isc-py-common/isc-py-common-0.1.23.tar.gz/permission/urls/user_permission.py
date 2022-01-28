from django.urls import path
from permission.views import user_permission

urlpatterns = [

    path('UserPermission/Fetch/', user_permission.User_permission_Fetch),
    path('UserPermission/Add', user_permission.User_permission_Add),
    path('UserPermission/Update', user_permission.User_permission_Update),
    path('UserPermission/Remove', user_permission.User_permission_Remove),
    path('UserPermission/Lookup', user_permission.User_permission_Lookup),

]
