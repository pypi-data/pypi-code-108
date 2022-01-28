from django.urls import path

from twits.views import chat_users

urlpatterns = [

    path('Chat_users/Fetch/', chat_users.Chat_users_Fetch),
    path('Chat_users/Add', chat_users.Chat_users_Add),
    path('Chat_users/Update', chat_users.Chat_users_Update),
    path('Chat_users/Remove', chat_users.Chat_users_Remove),
    path('Chat_users/Lookup/', chat_users.Chat_users_Lookup),
    path('Chat_users/Info/', chat_users.Chat_users_Info),
    path('Chat_users/Copy', chat_users.Chat_users_Copy),

]
