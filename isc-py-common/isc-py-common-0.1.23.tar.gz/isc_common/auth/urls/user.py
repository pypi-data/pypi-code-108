from django.urls import path

from isc_common.auth.views import user
from isc_common.auth.views.user import User_Add, User_Lookup, User_Info, User_Remove, User_Update
from isc_common.auth.views.user_download_photo import user_download_photo

urlpatterns = [

    path('User/Fetch/', user.User_Fetch),
    path('User/FetchExclBots/', user.User_FetchExclBots),
    path('logic/User/Fetch_User_DS4/', user.User_Fetch_User_DS4),
    path('User/Add', User_Add),
    path('User/Update', User_Update),
    path('User/Remove', User_Remove),
    path('User/Lookup/', User_Lookup),
    path('User/Info/', User_Info),
    path('User/DownloadPhoto/', user_download_photo),
]
