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

from django.db import models
from django.utils import timezone

class LikableObject(models.Model):
    """ An object that people might hit a like button on
    Used by Comment and CommentSection
    """
    count_replies = models.PositiveIntegerField(default=0)
    count_likes = models.PositiveIntegerField(default=0)
    count_dislikes = models.PositiveIntegerField(default=0)

    class Meta():
        abstract = True


class Like(models.Model):
    """ an object that records when someone hits the Like button. It also
    represents the Dislike action.
    """
    user = models.ForeignKey('auth.User',
                             related_name='likecomment_user_%(class)ss',
                             on_delete=models.CASCADE)
    like = models.BooleanField(default=True)
    date_time = models.DateTimeField(default=timezone.localtime)

    class Meta():
        abstract = True
