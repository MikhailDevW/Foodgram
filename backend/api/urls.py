from django.urls import include, path

urlpatterns = [
    path('api/', include('recipes.urls')),
    path('api/', include('user.urls')),
]
