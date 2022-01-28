from django.contrib import admin

# Register your models here.
from social_layer.comments.models import *


admin.site.register(Comment)
admin.site.register(CommentSection)
admin.site.register(LikeComment)
