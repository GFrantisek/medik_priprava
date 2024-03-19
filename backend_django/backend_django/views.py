from django.http import FileResponse, HttpResponse

from . import settings
from .utils import fetch_questions_and_answers, create_pdf, connect_db, db_params
import os


def generate_pdf(request):
    try:
        # Retrieve query parameters or use default values
        num_questions = request.GET.get('numQuestions', '100')  # Default to 100 if not provided
        start_question = request.GET.get('startQuestion', '1')  # Default to 1 if not provided
        end_question = request.GET.get('endQuestion', '200')  # Default to 200 if not provided

        # Convert query parameters to integers
        num_questions = int(num_questions)
        start_question = int(start_question)
        end_question = int(end_question)

        # Connect to the database and fetch data
        conn = connect_db(db_params)
        question_answers = fetch_questions_and_answers(conn, num_questions, start_question, end_question)
        conn.close()

        # Assume you are storing the PDF in a directory called 'pdfs' within the base directory
        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
        os.makedirs(pdf_directory, exist_ok=True)  # Ensure the directory exists

        # The filename for the PDF
        filename = 'questions.pdf'
        pdf_filepath = os.path.join(pdf_directory, filename)

        # Generate the PDF
        create_pdf(question_answers, pdf_filepath)

        # Open the PDF file and create the response
        with open(pdf_filepath, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Add CORS headers to the response
            response["Access-Control-Allow-Origin"] = "*"  # Allows access from any origin - use only for development
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

            return response

    except Exception as e:
        # If anything goes wrong, return an error response
        return HttpResponse(
            content=f"An error occurred while generating the PDF: {e}",
            status=500,
            content_type="text/plain"
        )