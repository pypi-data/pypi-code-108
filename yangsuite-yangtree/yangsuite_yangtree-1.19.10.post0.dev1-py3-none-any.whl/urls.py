# Copyright 2016 Cisco Systems, Inc
from django.conf.urls import url
from . import views


app_name = 'yangtree'
urlpatterns = [
    url(r'^explore/(?:(?P<yangset>[^/]+)/?(?P<modulenames>[^/]+)?)?',
        views.explore, name='explore'),
    url(r'^gettree/', views.get_tree, name='gettree'),
    url(r'^getrfc/', views.get_rfc, name='getrfc'),
]

taskurlpatterns = [
    url(r'^savetask/', views.save_task, name='savetask'),
    url(r'^edittask/', views.edit_task, name='edittask'),
    url(r'^gettask/', views.get_task, name='gettask'),
    url(r'^gettasklist/', views.get_task_list, name='gettasklist'),
    url(r'^getvariables/', views.get_replay_variables, name='getvariables'),
    url(r'^savetaskdata/', views.save_task_data, name='savetaskdata'),
    url(r'^deltask/', views.del_task, name='deltask'),
    url(r'^getcategories/', views.get_category_list, name='getcategories'),
    url(r'^delcategory/', views.delete_category, name='delcategory'),
    url(r'^changecategory/', views.change_category, name='changecategory'),
    url(r'^getreplaydir/', views.get_top_replay_dir, name='getreplaydir'),
    url(r'^saveyamlreplay/', views.save_yaml_replay, name='saveyamlreplay'),
    url(r'^setreplaydir/', views.set_top_replay_dir, name='setreplaydir'),
    url(r'^savereplayyaml/', views.save_replay_yaml, name='savereplayyaml'),
    url(r'^resetreplaydir/',
        views.reset_top_replay_dir,
        name='resetreplaydir'),
]

urlpatterns += taskurlpatterns
