from django.urls import path

from clndr.views import shifts

urlpatterns = [

    path('Shifts/Fetch/', shifts.Shifts_Fetch),
    path('Shifts/Add', shifts.Shifts_Add),
    path('Shifts/Update', shifts.Shifts_Update),
    path('Shifts/Remove', shifts.Shifts_Remove),
    path('Shifts/Lookup/', shifts.Shifts_Lookup),
    path('Shifts/Info/', shifts.Shifts_Info),
    path('Shifts/Copy', shifts.Shifts_Copy),

]
