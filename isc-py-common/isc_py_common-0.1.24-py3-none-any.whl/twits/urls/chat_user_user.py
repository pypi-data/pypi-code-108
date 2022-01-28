from django.urls import path

from twits.views import chat_user_user

urlpatterns = [

    path('Chat_user_user/Fetch/', chat_user_user.Chat_user_user_Fetch),
    path('Chat_user_user/Add', chat_user_user.Chat_user_user_Add),
    path('Chat_user_user/Update', chat_user_user.Chat_user_user_Update),
    path('Chat_user_user/Remove', chat_user_user.Chat_user_user_Remove),
    path('Chat_user_user/Lookup/', chat_user_user.Chat_user_user_Lookup),
    path('Chat_user_user/Info/', chat_user_user.Chat_user_user_Info),
    path('Chat_user_user/Copy', chat_user_user.Chat_user_user_Copy),

]
