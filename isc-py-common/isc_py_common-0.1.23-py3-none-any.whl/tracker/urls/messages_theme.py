from django.urls import path

from tracker.views import messages_theme

urlpatterns = [

    path('Messages_theme/Fetch/', messages_theme.Messages_theme_Fetch),
    path('Messages_theme/FetchAdmin/', messages_theme.Messages_theme_FetchAdmin),
    path('Messages_theme/Add', messages_theme.Messages_theme_Add),
    path('Messages_theme/Update', messages_theme.Messages_theme_Update),
    path('Messages_theme/Remove', messages_theme.Messages_theme_Remove),
    path('Messages_theme/Lookup/', messages_theme.Messages_theme_Lookup),
    path('Messages_theme/Info/', messages_theme.Messages_theme_Info),

]
