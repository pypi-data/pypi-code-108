from django.contrib import admin

# Register your models here.
from social_layer.profiles.models import *

admin.site.register(SocialProfile)
