from django.urls import path

from isc_common.auth.views.auth import changepassword, link2group, unlinkFromgroup, copyPermission, logout
from isc_common.auth.views.get_permission import get_permission_view
from isc_common.auth.views.permission import permission_view

urlpatterns = [
    path('logout', logout),
    path('changepassword', changepassword),
    path('link2group', link2group),
    path('unlinkFromgroup', unlinkFromgroup),
    path('copyPermission', copyPermission),
    path('permission', permission_view),
    path('get_permission', get_permission_view),
]
