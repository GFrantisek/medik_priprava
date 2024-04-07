#helloapp urls.py

from django.urls import path
from helloapp import views
from django.contrib import admin


urlpatterns = [
    path('about/', views.aboutpage, name='about'),
    path('', views.homepage, name='home'),

]