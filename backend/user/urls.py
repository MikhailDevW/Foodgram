from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet)

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
