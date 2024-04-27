# helloapp views.py
import zipfile
import os
from datetime import timezone

from django.core.mail.backends import console
from rest_framework.decorators import api_view

from . import serializers
from .models import StudentTests, StudentAnswers, MedAnswers
from .serializers import RegisterSerializer
from .utils import fetch_questions_and_answers, create_pdf, connect_db, db_params, create_pdf_with_correct_answers
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import status as http_status, status
from rest_framework import response
from rest_framework import decorators as rest_decorators
from rest_framework import status as http_status
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions as rest_permissions


# Utility function for setting CORS headers
def cors_headers(view_func):
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        return set_cors_headers(response)

    return wrapper


def set_cors_headers(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


def homepage(request):
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render(request, 'homepage.html', context={
        "message": "It's running!",
        "Service": service,
        "Revision": revision,
    })


def aboutpage(request):
    return render(request, 'aboutpage.html', context={})


def get_request_params(request, param_defaults=None):
    if param_defaults is None:
        param_defaults = {
            'numQuestions': '100',
            'startQuestion': '1',
            'endQuestion': '200',
            'numAnswers': '4',  # Default number of answers
            'categories': ''  # Default empty category list
        }
    return {param: request.GET.get(param, default) for param, default in param_defaults.items()}


@cors_headers
def get_test_questions(request):
    params = get_request_params(request)
    categories = params['categories'].split(',') if params['categories'] else []
    conn = connect_db(db_params)
    # Adjust the below line as needed based on your actual function's parameters
    questions_and_answers = fetch_questions_and_answers(conn,
            params['numQuestions'],
            params['startQuestion'],
            params['endQuestion'],
            params['numAnswers'],
            categories)
    conn.close()
    return JsonResponse(questions_and_answers)


@cors_headers
def generate_pdf(request):
    try:
        params = get_request_params(request)
        conn = connect_db(db_params)
        categories = params['categories'].split(',') if params['categories'] else []
        question_answers = fetch_questions_and_answers(conn,
                                                            params['numQuestions'],
                                                            params['startQuestion'],
                                                            params['endQuestion'],
                                                            params['numAnswers'],
                                                            categories)

        conn.close()

        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_directory, exist_ok=True)

        # Filenames for the two PDFs
        filename_questions = 'questions.pdf'
        filename_questions_with_correct = 'questions_with_correct.pdf'

        # File paths for the two PDFs
        pdf_filepath_questions = os.path.join(pdf_directory, filename_questions)
        pdf_filepath_questions_with_correct = os.path.join(pdf_directory, filename_questions_with_correct)

        # Generate both PDFs
        create_pdf(question_answers, pdf_filepath_questions)
        create_pdf_with_correct_answers(question_answers, pdf_filepath_questions_with_correct)

        # Zip both PDFs
        zip_filename = "questions_package.zip"
        zip_filepath = os.path.join(pdf_directory, zip_filename)
        with zipfile.ZipFile(zip_filepath, 'w') as myzip:
            myzip.write(pdf_filepath_questions, filename_questions)
            myzip.write(pdf_filepath_questions_with_correct, filename_questions_with_correct)

        # Return the zip file
        with open(zip_filepath, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
            return response

    except Exception as e:
        return HttpResponse(content=f"An error occurred while generating the PDFs: {e}", status=500,
                            content_type="text/plain")


@rest_decorators.api_view(['POST'])
@rest_decorators.permission_classes([])
def register(request):
    serializer = serializers.RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return response.Response(
            {
                "user_id": user.id,
                "email": user.email,
                "username": user.username  # Assuming you want to return this as well
            },
            status=http_status.HTTP_201_CREATED
        )
    else:
        return response.Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


class AccountTokenObtainPairViewSerializer(jwt_serializers.TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token


class AccountTokenObtainPairView(jwt_views.TokenObtainPairView):
    serializer_class = AccountTokenObtainPairViewSerializer


@rest_decorators.api_view(['GET'])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def detail(request):
    serializer = serializers.AccountSerializer(request.user)
    return response.Response({"user": serializer.data})


@api_view(['POST'])
def submit_answers(request):
    student_test = StudentTests.objects.create(
        student_id=request.user.id,  # assuming the user is authenticated
        test_template_id=request.data['test_template_id'],
        test_date=timezone.now(),
        score=0,  # Initialize score, calculate after all answers are submitted
        total_possible_score=request.data['total_possible_score']
    )

    answers = request.data['answers']
    for answer in answers:
        StudentAnswers.objects.create(
            test=student_test,
            question_id=answer['question_id'],
            selected_answer_id=answer['answer_id'],
            is_correct=answer['is_correct']
        )

        # Optionally increment selection_count
        selected_answer = MedAnswers.objects.get(id=answer['answer_id'])
        selected_answer.selection_count += 1
        selected_answer.save()

    # Here, calculate the score based on correct answers if needed

    return response.Response(status=status.HTTP_201_CREATED)