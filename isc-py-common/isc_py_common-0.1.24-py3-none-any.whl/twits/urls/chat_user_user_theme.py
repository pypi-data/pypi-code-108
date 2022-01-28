from django.urls import path

from twits.views import chat_user_user_theme

urlpatterns = [

    path('Chat_user_user_theme/Fetch/', chat_user_user_theme.Chat_user_user_theme_Fetch),
    path('Chat_user_user_theme/Add', chat_user_user_theme.Chat_user_user_theme_Add),
    path('Chat_user_user_theme/Update', chat_user_user_theme.Chat_user_user_theme_Update),
    path('Chat_user_user_theme/Remove', chat_user_user_theme.Chat_user_user_theme_Remove),
    path('Chat_user_user_theme/Lookup/', chat_user_user_theme.Chat_user_user_theme_Lookup),
    path('Chat_user_user_theme/Info/', chat_user_user_theme.Chat_user_user_theme_Info),
    path('Chat_user_user_theme/Copy', chat_user_user_theme.Chat_user_user_theme_Copy),

]
