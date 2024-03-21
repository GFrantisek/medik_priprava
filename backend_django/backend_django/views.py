from random import random

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render

from . import settings
from .utils import fetch_questions_and_answers, create_pdf, connect_db, db_params
import os


def get_test_questions(request):
    conn = connect_db(db_params)

    # add response take from frontend
    questions_and_answers = fetch_questions_and_answers(conn, 30, 1, 40)

    conn.close()

    response = JsonResponse(questions_and_answers)

    if settings.DEBUG:  #
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


def generate_pdf(request):
    try:
        num_questions = request.GET.get('numQuestions', '100')
        start_question = request.GET.get('startQuestion', '1')
        end_question = request.GET.get('endQuestion', '200')

        num_questions = int(num_questions)
        start_question = int(start_question)
        end_question = int(end_question)

        conn = connect_db(db_params)
        question_answers = fetch_questions_and_answers(conn, num_questions, start_question, end_question)
        conn.close()

        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_directory, exist_ok=True)

        filename = 'questions.pdf'
        pdf_filepath = os.path.join(pdf_directory, filename)

        create_pdf(question_answers, pdf_filepath)

        with open(pdf_filepath, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

            return response

    except Exception as e:
        return HttpResponse(
            content=f"An error occurred while generating the PDF: {e}",
            status=500,
            content_type="text/plain"
        )
