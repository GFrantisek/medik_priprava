# views.py

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import os

from .utils import fetch_questions_and_answers, create_pdf, connect_db, db_params


# Utility function for fetching request parameters with defaults
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
        # Adjust the below line as needed based on your actual function's parameters
        question_answers = fetch_questions_and_answers(conn, params['numQuestions'], params['startQuestion'],
                                                       params['endQuestion'])
        conn.close()

        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_directory, exist_ok=True)

        filename = 'questions.pdf'
        pdf_filepath = os.path.join(pdf_directory, filename)

        create_pdf(question_answers, pdf_filepath)

        with open(pdf_filepath, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    except Exception as e:
        return HttpResponse(content=f"An error occurred while generating the PDF: {e}", status=500,
                            content_type="text/plain")
