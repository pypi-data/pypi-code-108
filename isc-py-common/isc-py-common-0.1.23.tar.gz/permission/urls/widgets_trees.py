from django.urls import path
from permission.views import widgets_trees

urlpatterns = [

    path( 'Widgets_trees/Fetch/' , widgets_trees.Widgets_trees_Fetch ) ,
    path( 'Widgets_trees/Add' , widgets_trees.Widgets_trees_Add ) ,
    path( 'Widgets_trees/Update' , widgets_trees.Widgets_trees_Update ) ,
    path( 'Widgets_trees/Remove' , widgets_trees.Widgets_trees_Remove ) ,
    path( 'Widgets_trees/Lookup/' , widgets_trees.Widgets_trees_Lookup ) ,
    path( 'Widgets_trees/Info/' , widgets_trees.Widgets_trees_Info ) ,

]
