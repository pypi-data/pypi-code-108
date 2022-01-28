# This file is part of django-social-layer
#
#    django-social-layer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    django-social-layer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-social-layer. If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import include
from django.urls import path
from django.conf import settings
#from django.conf.urls.static import static


import social_layer

#from social_layer.views.comments import *

from social_layer.profiles.views import *
from social_layer.comments.views import *
from social_layer.notifications.views import *
from social_layer.posts.views import *

app_name = 'social_layer'

urlpatterns = [
    ##############
        # profile
        path('profile/', 
             social_layer.profiles.views.setup_profile, name='setup_profile'),
        path('profile/<int:pk>/',
             social_layer.profiles.views.view_profile, name='view_profile'),
        path('community/',
             social_layer.profiles.views.list_profiles, name='list_profiles'),
        path('social-login/',
             social_layer.profiles.views.social_login, name='social_login'),
        path('delete-profile-pic/',
             social_layer.profiles.views.delete_profile_photo,
             name='delete_profile_photo'),
        # comments
        path('comments/',
             social_layer.comments.views.comment_section, name='comment_section'),
        path('comments/<int:pk>/',
             social_layer.comments.views.comment_section, name='comment_section'),
        path('reply-comment/<int:pk>/',
             social_layer.comments.views.reply_comment, name='reply_comment'),
        path('del-comment/<int:pk>/',
             social_layer.comments.views.delete_comment, name='delete_comment'),
        # likes
        path('like-comment/<int:pk>/<slug:didlike>/',
             social_layer.comments.views.like_comment, name='like_comment'),
        path('like-post/<int:pk>/<slug:didlike>/',
             social_layer.comments.views.like_post, name='like_post'),
        # notifications
        path('notifications/',
             social_layer.notifications.views.view_notifications, name='view_notifications'),
        path('notifications/adm-send/<int:pk>/',
             social_layer.notifications.views.admin_send_notification, name='admin_send_notification'),
        #posts
        path('new-post/', social_layer.posts.views.new_post, name='new_post'),
        path('feed/', social_layer.posts.views.posts_feed, name='posts_feed'),
        path('more-posts/', social_layer.posts.views.more_posts, name='more_posts'),
        path('post/<int:pk>/', social_layer.posts.views.view_post, name='view_post'),
        path('delete-post/<int:pk>/', social_layer.posts.views.delete_post, name='delete_post'),
        ]

