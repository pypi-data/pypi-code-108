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

from django.contrib import admin

# Register your models here.
from social_layer.comments.models import Comment, CommentSection, LikeComment
from social_layer.notifications.models import Notification
from social_layer.profiles.models import SocialProfile, SocialProfilePhoto
from social_layer.posts.models import Post, PostMedia

admin.site.register(SocialProfile)
admin.site.register(SocialProfilePhoto)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(CommentSection)
admin.site.register(LikeComment)
admin.site.register(Post)
admin.site.register(PostMedia)
