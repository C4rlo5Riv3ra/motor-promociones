from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('promotion/', include('promotion.urls')),   # API REST
    path('', include('promotion.urls')),       # Frontend
    path('accounts/', include('allauth.urls')),  # Web login/logout/registro
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
