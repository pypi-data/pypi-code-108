from django.urls import path

import twits
from twits.views.chats import Chats_Fetch, Chats_Add, Chats_Update, Chats_Remove, Chats_Lookup, Chats_Info, Chats_Copy

urlpatterns = [

    path('Chats/Fetch/', Chats_Fetch),
    path('Chats/Add', Chats_Add),
    path('Chats/Update', Chats_Update),
    path('Chats/Remove', Chats_Remove),
    path('Chats/Lookup/', Chats_Lookup),
    path('Chats/Info/', Chats_Info),
    path('Chats/Copy', Chats_Copy),

]
