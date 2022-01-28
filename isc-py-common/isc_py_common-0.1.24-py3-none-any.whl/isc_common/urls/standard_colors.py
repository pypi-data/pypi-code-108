from django.urls import path

from isc_common.views import standard_colors

urlpatterns = [

    path('Standard_colors/Fetch/', standard_colors.Standard_colors_Fetch),
    path('Standard_colors/Add', standard_colors.Standard_colors_Add),
    path('Standard_colors/Update', standard_colors.Standard_colors_Update),
    path('Standard_colors/Remove', standard_colors.Standard_colors_Remove),
    path('Standard_colors/Lookup/', standard_colors.Standard_colors_Lookup),
    path('Standard_colors/Info/', standard_colors.Standard_colors_Info),
    path('Standard_colors/Copy', standard_colors.Standard_colors_Copy),

]
