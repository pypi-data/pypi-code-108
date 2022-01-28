from django.urls import path

from clndr.views import calendar_shifts_days

urlpatterns = [

    path('Calendar_shifts_days/Fetch/', calendar_shifts_days.Calendar_shifts_days_Fetch),
    path('Calendar_shifts_days/Add', calendar_shifts_days.Calendar_shifts_days_Add),
    path('Calendar_shifts_days/Update', calendar_shifts_days.Calendar_shifts_days_Update),
    path('Calendar_shifts_days/Remove', calendar_shifts_days.Calendar_shifts_days_Remove),
    path('Calendar_shifts_days/Lookup/', calendar_shifts_days.Calendar_shifts_days_Lookup),
    path('Calendar_shifts_days/Info/', calendar_shifts_days.Calendar_shifts_days_Info),
    path('Calendar_shifts_days/Copy', calendar_shifts_days.Calendar_shifts_days_Copy),

]
