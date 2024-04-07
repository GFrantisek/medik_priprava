#helloproject urls.py

from django.urls import path, include

from helloapp import views
from helloapp.views import generate_pdf, get_test_questions
from django.contrib import admin

urlpatterns = [

    path('', include('helloapp.urls')),
    path('generate-pdf/', generate_pdf, name='generate-pdf'),
    path('api/get_test_questions/', get_test_questions, name='get_test_questions'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
]
