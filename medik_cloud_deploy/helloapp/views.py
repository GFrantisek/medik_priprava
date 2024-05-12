# helloapp views.py
import logging
import zipfile
import os
from datetime import timezone
from io import BytesIO

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .models import StudentTests, StudentAnswers, MedAnswers, UserQuestionAnswers, TestScores, MedQuestions
from .serializers import StudentTestsSerializer
from django.shortcuts import render
from rest_framework import response
from rest_framework import decorators as rest_decorators
from rest_framework import status as http_status
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions as rest_permissions
from rest_framework.response import Response
from rest_framework import views, status
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import json


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


class TestHistoryView(views.APIView):
    def get(self, request):
        user_id = request.user.id  # Assumes user authentication is managed
        tests = StudentTests.objects.filter(student_id=user_id)
        serializer = StudentTestsSerializer(tests, many=True)
        return Response(serializer.data)


from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_test_questions(request):
    num_questions = int(request.GET.get('numQuestions', 100))
    start_question = int(request.GET.get('startQuestion', 1))
    end_question = int(request.GET.get('endQuestion', 1500))  # Adjust to 1500 based on your data
    num_answers = int(request.GET.get('numAnswers', 4))
    categories = request.GET.get('categories', '').split(',') if request.GET.get('categories') else []

    if len(categories) != 0:
        start_question = 1
        end_question = 1500

    with connection.cursor() as cursor:
        sql_query = """
        WITH RandomQuestions AS (
            SELECT question_id, question_text
            FROM MedQuestions
            WHERE question_id BETWEEN %s AND %s
        """
        params = [start_question, end_question]

        if categories:
            # Include parameter placeholders for each category
            sql_query += " AND question_category IN ({})".format(','.join(['%s'] * len(categories)))
            params += categories

        sql_query += """
            ORDER BY RANDOM()
            LIMIT %s
        ), RankedAnswers AS (
            SELECT 
                answer_id, 
                answer_text, 
                is_correct, 
                question_id,
                ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY RANDOM()) as rn
            FROM MedAnswers
            WHERE question_id IN (SELECT question_id FROM RandomQuestions)
        )
        SELECT 
            q.question_id, 
            q.question_text, 
            a.answer_id, 
            a.answer_text, 
            a.is_correct
        FROM RandomQuestions q
        JOIN RankedAnswers a ON q.question_id = a.question_id
        WHERE a.rn <= %s
        """
        params += [num_questions, num_answers]

        cursor.execute(sql_query, params)
        rows = cursor.fetchall()

    # Process the fetched data into a structured dictionary
    questions = {}
    for row in rows:
        question_id, question_text, answer_id, answer_text, is_correct = row
        if question_id not in questions:
            questions[question_id] = {
                'question_id': question_id,
                'question_text': question_text,
                'answers': []
            }
        questions[question_id]['answers'].append({
            'answer_id': answer_id,
            'answer_text': answer_text,
            'is_correct': is_correct
        })

    return JsonResponse({'questions': list(questions.values())})


# Register the fonts
regular_font_path = "helloapp/static/DejaVuSansCondensed.ttf"
bold_font_path = "helloapp/static/DejaVuSansCondensed-Bold.ttf"
pdfmetrics.registerFont(TTFont('DejaVu', regular_font_path))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', bold_font_path))


@csrf_exempt
@require_http_methods(["GET", "POST"])  # Allow only POST requests
def generate_pdf_method(request):
    # Fetch the questions JSON from the existing `get_test_questions` view or a similar method
    print(request)
    response = get_test_questions(request)
    data = json.loads(response.content)
    questions = data.get('questions', [])

    # Prepare the custom styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DejaVu-Heading', fontName='DejaVu-Bold', fontSize=12, leading=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='DejaVu-Body', fontName='DejaVu', fontSize=9, leading=10, spaceAfter=6))
    styles.add(ParagraphStyle(name='DejaVu-Body-Bold', fontName='DejaVu-Bold', fontSize=9, leading=10, spaceAfter=6))

    # Create memory buffer for PDFs
    buffer1 = BytesIO()
    buffer2 = BytesIO()

    # Create the PDF documents
    doc1 = SimpleDocTemplate(buffer1, pagesize=A4)
    doc2 = SimpleDocTemplate(buffer2, pagesize=A4)
    Story1 = []
    Story2 = []

    # Generate content for both PDFs
    for index, question in enumerate(questions, start=1):
        question_text = f"{index}. {question['question_text']}"
        para1 = Paragraph(question_text, styles['DejaVu-Heading'])
        para2 = Paragraph(question_text, styles['DejaVu-Heading'])
        Story1.append(para1)
        Story2.append(para2)
        Story1.append(Spacer(1, 0.05 * inch))
        Story2.append(Spacer(1, 0.05 * inch))

        for answer_index, answer in enumerate(question['answers']):
            answer_letter = chr(97 + answer_index)
            answer_text = f"{answer_letter}) {answer['answer_text']}"
            if answer['is_correct']:
                para2 = Paragraph(answer_text, styles['DejaVu-Body-Bold'])
            else:
                para2 = Paragraph(answer_text, styles['DejaVu-Body'])
            para1 = Paragraph(answer_text, styles['DejaVu-Body'])

            Story1.append(para1)
            Story1.append(Spacer(1, 0.01 * inch))
            Story2.append(para2)
            Story2.append(Spacer(1, 0.01 * inch))

        Story1.append(Spacer(1, 0.1 * inch))
        Story2.append(Spacer(1, 0.1 * inch))

    # Build both PDFs
    doc1.build(Story1)
    doc2.build(Story2)

    # Create a ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('test_questions.pdf', buffer1.getvalue())
        zip_file.writestr('test_with_correct_answers.pdf', buffer2.getvalue())

    # Set up the HTTP response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'inline; filename="test_pdfs.zip"'  # Use inline to attempt displaying names
    return response


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_id(request):
    """
    Endpoint to retrieve the authenticated user's ID.
    Only accessible to authenticated users.
    """
    user_id = request.user.id  # Accessing user ID from the request object
    return JsonResponse({'user_id': user_id}, status=200)


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


@csrf_exempt
@require_http_methods(["POST"])  # Now this function only accepts POST requests
def generate_pdf_method_from_params(request):
    # Extract parameters from POST data
    post_data = json.loads(request.body)
    num_questions = int(post_data.get('numQuestions', 100))
    start_question = int(post_data.get('startQuestion', 1))
    end_question = int(post_data.get('endQuestion', 1500))  # Adjust based on your data
    num_answers = int(post_data.get('numAnswers', 4))
    categories = post_data.get('categories', '').split(',') if post_data.get('categories') else []

    if len(categories) != 0:
        start_question = 1
        end_question = 1500

    # Fetch the questions using the extracted parameters
    questions = fetch_questions(num_questions, start_question, end_question, num_answers, categories)

    # Prepare the custom styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DejaVu-Heading', fontName='DejaVu-Bold', fontSize=12, leading=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='DejaVu-Body', fontName='DejaVu', fontSize=9, leading=10, spaceAfter=6))
    styles.add(ParagraphStyle(name='DejaVu-Body-Bold', fontName='DejaVu-Bold', fontSize=9, leading=10, spaceAfter=6))

    # Create memory buffers for PDFs
    buffer1 = BytesIO()
    buffer2 = BytesIO()

    # Create the PDF documents
    doc1 = SimpleDocTemplate(buffer1, pagesize=A4)
    doc2 = SimpleDocTemplate(buffer2, pagesize=A4)
    Story1 = []
    Story2 = []

    # Generate content for both PDFs
    for index, question in enumerate(questions, start=1):
        question_text = f"{index}. {question['question_text']}"
        para1 = Paragraph(question_text, styles['DejaVu-Heading'])
        para2 = Paragraph(question_text, styles['DejaVu-Heading'])
        Story1.append(para1)
        Story2.append(para2)
        Story1.append(Spacer(1, 0.05 * inch))
        Story2.append(Spacer(1, 0.05 * inch))

        for answer_index, answer in enumerate(question['answers']):
            answer_letter = chr(97 + answer_index)
            answer_text = f"{answer_letter}) {answer['answer_text']}"
            if answer['is_correct']:
                para2 = Paragraph(answer_text, styles['DejaVu-Body-Bold'])
            else:
                para2 = Paragraph(answer_text, styles['DejaVu-Body'])
            para1 = Paragraph(answer_text, styles['DejaVu-Body'])

            Story1.append(para1)
            Story1.append(Spacer(1, 0.01 * inch))
            Story2.append(para2)
            Story2.append(Spacer(1, 0.01 * inch))

        Story1.append(Spacer(1, 0.1 * inch))
        Story2.append(Spacer(1, 0.1 * inch))

    # Build both PDFs
    doc1.build(Story1)
    doc2.build(Story2)

    # Create a ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('test_questions.pdf', buffer1.getvalue())
        zip_file.writestr('test_with_correct_answers.pdf', buffer2.getvalue())

    # Set up the HTTP response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'inline; filename="test_pdfs.zip"'  # Use inline to attempt displaying names
    return response


def fetch_questions(num_questions, start_question, end_question, num_answers, categories):
    """
    Utility function that executes the query to fetch questions and their answers.
    """
    with connection.cursor() as cursor:
        sql_query = """
        WITH RandomQuestions AS (
            SELECT question_id, question_text
            FROM MedQuestions
            WHERE question_id BETWEEN %s AND %s
        """
        params = [start_question, end_question]

        if categories:
            # Include parameter placeholders for each category
            sql_query += " AND question_category IN ({})".format(','.join(['%s'] * len(categories)))
            params += categories

        sql_query += """
            ORDER BY RANDOM()
            LIMIT %s
        ), RankedAnswers AS (
            SELECT 
                answer_id, 
                answer_text, 
                is_correct, 
                question_id,
                ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY RANDOM()) as rn
            FROM MedAnswers
            WHERE question_id IN (SELECT question_id FROM RandomQuestions)
        )
        SELECT 
            q.question_id, 
            q.question_text, 
            a.answer_id, 
            a.answer_text, 
            a.is_correct
        FROM RandomQuestions q
        JOIN RankedAnswers a ON q.question_id = a.question_id
        WHERE a.rn <= %s
        """
        params += [num_questions, num_answers]

        cursor.execute(sql_query, params)
        rows = cursor.fetchall()

    # Process the fetched data into a structured dictionary
    questions = {}
    for row in rows:
        question_id, question_text, answer_id, answer_text, is_correct = row
        if question_id not in questions:
            questions[question_id] = {
                'question_id': question_id,
                'question_text': question_text,
                'answers': []
            }
        questions[question_id]['answers'].append({
            'answer_id': answer_id,
            'answer_text': answer_text,
            'is_correct': is_correct
        })

    return list(questions.values())


@csrf_exempt
@require_http_methods(["POST"])
def generate_pdf_from_loaded_questions(request):
    try:
        data = json.loads(request.body)
        questions = data.get('questions', [])

        # Define styles for the PDF
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(name='DejaVu-Heading', fontName='DejaVu-Bold', fontSize=12, leading=14, spaceAfter=12))
        styles.add(ParagraphStyle(name='DejaVu-Body', fontName='DejaVu', fontSize=9, leading=10, spaceAfter=6))
        styles.add(
            ParagraphStyle(name='DejaVu-Body-Bold', fontName='DejaVu-Bold', fontSize=9, leading=10, spaceAfter=6))

        # Create memory buffers for the PDFs
        buffer1 = BytesIO()
        buffer2 = BytesIO()

        # Setup PDF documents
        doc1 = SimpleDocTemplate(buffer1, pagesize=A4)
        doc2 = SimpleDocTemplate(buffer2, pagesize=A4)
        Story1 = []
        Story2 = []

        # Populate content for both PDFs
        for index, question in enumerate(questions, start=1):
            heading1 = Paragraph(f"{index}. {question['question_text']}", styles['DejaVu-Heading'])
            heading2 = Paragraph(f"{index}. {question['question_text']}", styles['DejaVu-Heading'])

            Story1.append(heading1)
            Story2.append(heading2)
            Story1.append(Spacer(1, 0.05 * inch))
            Story2.append(Spacer(1, 0.05 * inch))

            for answer in question['answers']:
                answer_text = f"{chr(97 + question['answers'].index(answer))}) {answer['answer_text']}"
                if answer['is_correct']:
                    para2 = Paragraph(answer_text, styles['DejaVu-Body-Bold'])
                else:
                    para2 = Paragraph(answer_text, styles['DejaVu-Body'])

                para1 = Paragraph(answer_text, styles['DejaVu-Body'])

                Story1.append(para1)
                Story1.append(Spacer(1, 0.01 * inch))
                Story2.append(para2)
                Story2.append(Spacer(1, 0.01 * inch))

            Story1.append(Spacer(1, 0.1 * inch))
            Story2.append(Spacer(1, 0.1 * inch))

        # Build both PDFs
        doc1.build(Story1)
        doc2.build(Story2)

        # Create a ZIP file to store both PDFs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('test_questions.pdf', buffer1.getvalue())
            zip_file.writestr('test_with_correct_answers.pdf', buffer2.getvalue())

        # Set up the HTTP response
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="test_pdfs.zip"'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def store_user_answers(request):
    """
    Store user answers to the database, including tracking incorrect answers directly from the payload.
    """
    try:
        data = request.data
        user_id = data['userId']
        test_id = data['testId']
        answers = data['answers']

        # Process each answer
        for answer in answers:
            question_id = answer['questionId']
            all_answer_ids = [ans['answer_id'] for ans in answer['allAnswers']]
            selected_answers = {ans['answer_id']: ans['is_correct'] for ans in answer['selectedAnswers']}
            incorrect_answers_ids = answer['incorrectAnswerIds']  # Use directly from payload

            # Serialize the data
            user_answers_json = json.dumps(selected_answers)
            incorrect_answers_json = json.dumps(incorrect_answers_ids)

            # Create the UserQuestionAnswers entry including incorrect answers
            UserQuestionAnswers.objects.create(
                user_id=user_id,
                test_id=test_id,
                question_id=question_id,
                answer_ids=json.dumps(all_answer_ids),
                user_answers=user_answers_json,
                incorrect_answers_ids=incorrect_answers_json
            )

        return Response({'message': 'Answers submitted successfully.'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_test_score(request):
    """
    Store test scores directly without using a serializer.
    """
    try:
        # Extracting data directly from the request body
        data = request.data
        user_id = data.get('user_id')  # Changed from 'userId' to 'user_id'
        test_id = data.get('test_id')  # Ensure this is extracting correctly as well
        score = data.get('score')
        max_score = data.get('max_score')
        duration = data.get('duration', None)  # Optional field

        # Create the TestScore entry
        test_score = TestScores(
            user_id=user_id,
            test_id=test_id,
            score=score,
            max_score=max_score,
            duration=duration
        )
        test_score.save()

        # Returning a success response
        return Response({'message': 'Test score created successfully.'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # Returning an error response if something goes wrong
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_user_tests(request, user_id):
    tests = TestScores.objects.filter(user_id=user_id)
    tests_data = [{
        'id': test.id,
        'test_id': str(test.test_id),
        'score': test.score,
        'max_score': test.max_score,
        'test_date': test.test_date.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': str(test.duration)
    } for test in tests]

    return JsonResponse(tests_data, safe=False)


@api_view(['GET'])
def get_question_answers_for_history_test(request, user_id, test_id):
    try:
        # SQL query to fetch relevant data
        sql = """
        SELECT
            mq.question_id,
            mq.question_text,
            ma.answer_id,
            ma.answer_text,
            ma.is_correct,
            uqa.answer_ids,
            uqa.user_answers,
            uqa.incorrect_answers_ids
        FROM
            medquestions mq
        JOIN
            medanswers ma ON mq.question_id = ma.question_id
        JOIN
            user_question_answers uqa ON mq.question_id = uqa.question_id
        WHERE
            uqa.user_id = %s
            AND uqa.test_id = %s
        ORDER BY
            mq.question_id,
            ma.answer_id;
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id, test_id])
            result_set = cursor.fetchall()

        # Initialize the results list
        results = []
        current_question = {}

        for row in result_set:
            question_id, question_text, answer_id, answer_text, is_correct, answer_ids_json, user_answers_json, incorrect_answers_ids_json = row

            # Utility function to safely parse JSON
            def safe_parse_json(json_str):
                try:
                    return json.loads(json_str)
                except (json.JSONDecodeError, TypeError, ValueError):
                    return []

            # Parse the JSON fields into lists
            answer_ids = safe_parse_json(answer_ids_json)
            user_answers = safe_parse_json(user_answers_json)
            incorrect_answers_ids = safe_parse_json(incorrect_answers_ids_json)

            # Ensure answer IDs are integers for the comparison to work correctly
            try:
                answer_ids = [int(id) for id in answer_ids]
            except (TypeError, ValueError):
                answer_ids = []

            # Check if the current answer is in the selected answers
            selected = answer_id in answer_ids

            # If a new question starts, append the previous question to the results
            if not current_question or current_question['question_id'] != question_id:
                if current_question:
                    results.append(current_question)
                current_question = {
                    'question_id': question_id,
                    'question_text': question_text,
                    'answers': [],
                    'user_answers': user_answers,
                    'incorrect_answers_ids': incorrect_answers_ids
                }

            # Append the answer details to the current question
            current_question['answers'].append({
                'answer_id': answer_id,
                'answer_text': answer_text,
                'is_correct': is_correct,
                'selected': selected
            })

        # Add the last question to the results, if available
        if current_question:
            results.append(current_question)

        # Return a JSON response containing the results
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['GET'])
def test_questions_desperate(request, user_id, test_id):
    try:
        # SQL query to fetch question details and aggregate answer information into JSON objects
        sql = """
        SELECT 
            uqa.question_id, 
            mq.question_text, 
            json_agg(
                json_build_object(
                    'answer_id', ma.answer_id,
                    'answer_text', ma.answer_text,
                    'is_correct', ma.is_correct
                )
            ) AS answers_info,
            uqa.answer_ids, 
            uqa.user_answers, 
            uqa.incorrect_answers_ids
        FROM 
            user_question_answers uqa
        JOIN 
            medquestions mq ON uqa.question_id = mq.question_id
        JOIN 
            medanswers ma ON mq.question_id = ma.question_id
        WHERE 
            uqa.user_id = %s AND uqa.test_id = %s
        GROUP BY 
            uqa.question_id, mq.question_text, uqa.answer_ids, uqa.user_answers, uqa.incorrect_answers_ids
        ORDER BY 
            uqa.question_id;
        """

        # Execute the query using a database cursor
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id, test_id])
            result_set = cursor.fetchall()

        # Convert the query result to a list of dictionaries for easy JSON serialization
        results = [
            {
                'question_id': row[0],
                'question_text': row[1],
                'answers_info': row[2],
                'answer_ids': json.loads(row[3]),
                'user_answers': json.loads(row[4]),
                'incorrect_answers_ids': json.loads(row[5])
            }
            for row in result_set
        ]

        # Return the compiled JSON response
        return JsonResponse(results, safe=False)

    except Exception as e:
        # Log the error or handle it in a way that suits your project
        return JsonResponse({'error': str(e)}, status=400)
