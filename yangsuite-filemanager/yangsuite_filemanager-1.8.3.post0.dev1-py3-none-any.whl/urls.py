# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
from django.conf.urls import url
from . import views

app_name = 'filemanager'
urlpatterns = [
    url(r'^upload/to_repository/', views.upload_files_to_repo,
        name="upload_files_to_repo"),
    url(r'^git/to_repository/', views.git_files_to_repo,
        name="git_files_to_repo"),
    url(r'^scp/to_repository/', views.scp_files_to_repo,
        name="scp_files_to_repo"),
    url(r'^repository/list/', views.get_repos, name='get_repos'),
    url(r'^repository/get/', views.get_repo_contents,
        name='get_repo_contents'),
    url(r'^repository/create/', views.create_repo, name='create_repo'),
    url(r'^repository/delete/$', views.delete_repo, name='delete_repo'),
    url(r'^repository/deletemodules/$', views.delete_modules_from_repo,
        name='delete_modules_from_repo'),
    url(r'^repository/check/$', views.check_repo, name='check_repo'),
    url(r'^repository/manage/(?P<repository>[^/]+)?', views.manage_repos,
        name='manage_repos'),
    url(r'^repository/show/(?P<repository>[^/]+)/module/(?P<module>[^/]+)',
        views.show_repo_module, name='show_repo_module'),
    url(r'^yangsets/list/', views.get_yangsets, name="get_yangsets"),
    url(r'^yangsets/get/', views.get_yangset_contents,
        name="get_yangset_contents"),
    url(r'^yangsets/getrelated/', views.get_related_modules,
        name="get_related_modules"),
    url(r'^yangsets/create/', views.create_yangset, name="create_yangset"),
    url(r'^yangsets/update/$', views.update_yangset, name="update_yangset"),
    url(r'^yangsets/delete/', views.delete_yangset, name="delete_yangset"),
    url(r'^yangsets/validate/', views.validate_yangset,
        name="validate_yangset"),
    url(r'^yangsets/manage/(?P<yangset>[^/]+)?', views.manage_yangsets,
        name="manage_yangsets"),
    url(r'^yangsets/show/(?P<yangset>[^/]+)/module/(?P<module>[^/]+)',
        views.show_yangset_module, name="show_yangset_module"),
]
