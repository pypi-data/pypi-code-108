from django.urls import path

from tracker.views import message_user_2_user

urlpatterns = [

    path('Message_user_2_user/Fetch/', message_user_2_user.Message_user_2_user_Fetch),
    path('Message_user_2_user/Add', message_user_2_user.Message_user_2_user_Add),
    path('Message_user_2_user/Update', message_user_2_user.Message_user_2_user_Update),
    path('Message_user_2_user/Remove', message_user_2_user.Message_user_2_user_Remove),
    path('Message_user_2_user/Lookup/', message_user_2_user.Message_user_2_user_Lookup),
    path('Message_user_2_user/Info/', message_user_2_user.Message_user_2_user_Info),
    path('Message_user_2_user/Copy', message_user_2_user.Message_user_2_user_Copy),

]
