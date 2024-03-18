from django.http import HttpResponse
from io import BytesIO
# Import your PDF generation classes and methods here
from .pdf_generation import PDF, create_pdf, connect_db, fetch_questions_and_answers, create_pdf_table
from django.conf import settings
import os


def generate_pdf(request):
    # Database connection
    conn = connect_db(db_params)
    question_answers = fetch_questions_and_answers(conn)

    # Generate PDF
    buffer = BytesIO()
    create_pdf(question_answers, buffer)
    # Alternatively, if using create_pdf_table:
    # create_pdf_table(buffer)

    conn.close()

    # Prepare response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="questions_and_answers.pdf"'
    return response
