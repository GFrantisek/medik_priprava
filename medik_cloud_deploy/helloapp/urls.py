#helloapp urls.py

from django.urls import path
from helloapp import views
from django.urls import include, path
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.AccountTokenObtainPairView.as_view(), name='login'),
    path('user', views.detail, name='user'),
    path('refresh', jwt_views.TokenRefreshView.as_view(), name='refresh'),
    path('logout', jwt_views.TokenBlacklistView.as_view(), name='logout'),
]