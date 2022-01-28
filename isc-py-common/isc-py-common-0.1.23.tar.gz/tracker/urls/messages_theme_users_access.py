from django.urls import path

from tracker.views import messages_theme_users_access

urlpatterns = [

    path('MessagesThemeUsersAccess/Fetch/', messages_theme_users_access.MessagesThemeUsersAccess_Fetch),
    path('MessagesThemeUsersAccess/Add', messages_theme_users_access.MessagesThemeUsersAccess_Add),
    path('MessagesThemeUsersAccess/Update', messages_theme_users_access.MessagesThemeUsersAccess_Update),
    path('MessagesThemeUsersAccess/Remove', messages_theme_users_access.MessagesThemeUsersAccess_Remove),
    path('MessagesThemeUsersAccess/Lookup/', messages_theme_users_access.MessagesThemeUsersAccess_Lookup),
    path('MessagesThemeUsersAccess/Info/', messages_theme_users_access.MessagesThemeUsersAccess_Info),
    path('MessagesThemeUsersAccess/Copy', messages_theme_users_access.MessagesThemeUsersAccess_Copy),

]
