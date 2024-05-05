#helloproject urls.py

from django.urls import path, include

from helloapp.views import fetch_questions_and_answers, fetch_questions_and_answers_faster_version
from helloapp.views import generate_pdf, get_test_questions, TestHistoryView
from django.contrib import admin

urlpatterns = [

    path('generate-pdf/', generate_pdf, name='generate-pdf'),
    path('api/get_test_questions/', get_test_questions, name='get_test_questions'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('helloapp.urls')),
    path('test-history/', TestHistoryView.as_view(), name='test-history'),
    path('questions/', fetch_questions_and_answers_faster_version, name='fetch_questions')

]

