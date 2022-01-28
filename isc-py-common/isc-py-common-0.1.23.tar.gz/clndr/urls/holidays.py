from django.urls import path

from clndr.views import holidays

urlpatterns = [

    path('Holidays/Fetch/', holidays.Holidays_Fetch),
    path('Holidays/Add', holidays.Holidays_Add),
    path('Holidays/Update', holidays.Holidays_Update),
    path('Holidays/Remove', holidays.Holidays_Remove),
    path('Holidays/Lookup/', holidays.Holidays_Lookup),
    path('Holidays/Info/', holidays.Holidays_Info),
    path('Holidays/Copy', holidays.Holidays_Copy),

]
