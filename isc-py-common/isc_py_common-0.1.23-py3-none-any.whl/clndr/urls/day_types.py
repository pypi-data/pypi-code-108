from django.urls import path

from clndr.views import day_types

urlpatterns = [

    path('Day_types/Fetch/', day_types.Day_types_Fetch),
    path('Day_types/Add', day_types.Day_types_Add),
    path('Day_types/Update', day_types.Day_types_Update),
    path('Day_types/Remove', day_types.Day_types_Remove),
    path('Day_types/Lookup/', day_types.Day_types_Lookup),
    path('Day_types/Info/', day_types.Day_types_Info),
    path('Day_types/Copy', day_types.Day_types_Copy),

]
