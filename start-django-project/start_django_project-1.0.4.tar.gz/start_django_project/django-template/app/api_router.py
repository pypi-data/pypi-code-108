from rest_framework import routers

from .api_views import MyUserViewSet

router = routers.DefaultRouter()
router.register(r'users', MyUserViewSet)
