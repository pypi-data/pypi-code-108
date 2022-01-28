from django.urls import path

from clndr.views import shift_day

urlpatterns = [

    path('Shift_day/Fetch/', shift_day.Shift_day_Fetch),
    path('Shift_day/Add', shift_day.Shift_day_Add),
    path('Shift_day/Update', shift_day.Shift_day_Update),
    path('Shift_day/Remove', shift_day.Shift_day_Remove),
    path('Shift_day/Lookup/', shift_day.Shift_day_Lookup),
    path('Shift_day/Info/', shift_day.Shift_day_Info),
    path('Shift_day/Copy', shift_day.Shift_day_Copy),

]
