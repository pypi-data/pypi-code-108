from django.urls import path, include
from .api_router import router
from .views import index, about, loginPage, signup, logoutPage

urlpatterns = [
    path('', index.as_view(), name="index"),
    path('about/', about.as_view(), name="about"),
    path('login/', loginPage.as_view(), name="loginPage"),
    path('signup/', signup.as_view(), name="signup"),
    path('logout/', logoutPage.as_view(), name="logout"),
    path('api/', include(router.urls)),
]