# helloapp views.py
from django.shortcuts import render
import os
import requests

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import zipfile
import os

from .utils import fetch_questions_and_answers, create_pdf, connect_db, db_params, create_pdf_with_correct_answers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


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
        param_defaults = {'numQuestions': '100', 'startQuestion': '1', 'endQuestion': '200'}
    return {param: int(request.GET.get(param, default)) for param, default in param_defaults.items()}


# Utility function for setting CORS headers
def set_cors_headers(response):
    if settings.DEBUG:
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


# Decorator for CORS headers
def cors_headers(view_func):
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        return set_cors_headers(response)

    return wrapper


@cors_headers
def get_test_questions(request):
    params = get_request_params(request)
    conn = connect_db(db_params)
    # Adjust the below line as needed based on your actual function's parameters
    questions_and_answers = fetch_questions_and_answers(conn, params['numQuestions'], params['startQuestion'],
                                                        params['endQuestion'])
    conn.close()
    return JsonResponse(questions_and_answers)


@cors_headers
def generate_pdf(request):
    try:
        params = get_request_params(request)
        conn = connect_db(db_params)
        question_answers = fetch_questions_and_answers(conn, params['numQuestions'], params['startQuestion'],
                                                       params['endQuestion'])
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


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        User.objects.create_user(username=username, email=email, password=password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')