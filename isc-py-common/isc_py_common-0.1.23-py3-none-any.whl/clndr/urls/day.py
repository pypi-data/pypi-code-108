from django.urls import path

from clndr.views import day

urlpatterns = [

    path('Day/Fetch/', day.Day_Fetch),
    path('Day/Add', day.Day_Add),
    path('Day/Update', day.Day_Update),
    path('Day/Remove', day.Day_Remove),
    path('Day/Lookup/', day.Day_Lookup),
    path('Day/Info/', day.Day_Info),
    path('Day/Copy', day.Day_Copy),

]
