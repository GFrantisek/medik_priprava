#helloproject urls.py

from django.urls import path, include

from helloapp.views import fetch_questions, generate_pdf_method, generate_pdf_method_from_params, \
    generate_pdf_from_loaded_questions, store_user_answers, create_test_score, get_user_tests, \
    get_question_answers_for_history_test, test_questions_desperate
from helloapp.views import get_test_questions, TestHistoryView
from django.contrib import admin

urlpatterns = [

    path('generate_pdf_method_from_params/', generate_pdf_method_from_params, name='generate_pdf_method-pdf'),
    path('api/get_test_questions/', get_test_questions, name='get_test_questions'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('helloapp.urls')),
    path('test-history/', TestHistoryView.as_view(), name='test-history'),
    path('generate-pdf-new/', generate_pdf_method, name='generate_pdf_method'),
    path('generate_pdf_from_loaded_questions/', generate_pdf_from_loaded_questions,
         name='generate_pdf_from_loaded_questions'),
    path('api/store_answers/', store_user_answers, name='store_answers'),
    path('api/create_test_score/', create_test_score, name='create_test_score'),
    path('api/user/<int:user_id>/tests/', get_user_tests, name='get_user_tests'),
    path('api/user/<int:user_id>/test/<uuid:test_id>/answers/', get_question_answers_for_history_test, name='get_question_answers_for_history_test'),
    path('api/user/<int:user_id>/test/<uuid:test_id>/answers/new', test_questions_desperate, name='test_questions_desperate'),
]

