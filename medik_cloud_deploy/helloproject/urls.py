#helloproject urls.py

from django.urls import path, include

from helloapp.views import generate_pdf, get_test_questions
from django.contrib import admin

urlpatterns = [

    path('generate-pdf/', generate_pdf, name='generate-pdf'),
    path('api/get_test_questions/', get_test_questions, name='get_test_questions'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('helloapp.urls')),


]

