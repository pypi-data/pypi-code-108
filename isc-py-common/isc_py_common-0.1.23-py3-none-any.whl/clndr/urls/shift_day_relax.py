from django.urls import path

from clndr.views import shift_day_relax

urlpatterns = [

    path('Shift_day_relax/Fetch/', shift_day_relax.Shift_day_relax_Fetch),
    path('Shift_day_relax/Add', shift_day_relax.Shift_day_relax_Add),
    path('Shift_day_relax/Update', shift_day_relax.Shift_day_relax_Update),
    path('Shift_day_relax/Remove', shift_day_relax.Shift_day_relax_Remove),
    path('Shift_day_relax/Lookup/', shift_day_relax.Shift_day_relax_Lookup),
    path('Shift_day_relax/Info/', shift_day_relax.Shift_day_relax_Info),
    path('Shift_day_relax/Copy', shift_day_relax.Shift_day_relax_Copy),

]
