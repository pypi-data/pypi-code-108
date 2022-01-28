from django.urls import path

from history.views import visitor

urlpatterns = [

    path('Visitor/Fetch/', visitor.Visitor_Fetch),
    path('Visitor/Add', visitor.Visitor_Add),
    path('Visitor/Update', visitor.Visitor_Update),
    path('Visitor/Remove', visitor.Visitor_Remove),
    path('Visitor/Lookup/', visitor.Visitor_Lookup),
    path('Visitor/Info/', visitor.Visitor_Info),
    path('Visitor/Copy', visitor.Visitor_Copy),

]
