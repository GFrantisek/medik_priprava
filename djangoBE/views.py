from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Question


def generate_test_pdf(request, num_questions, start_id, end_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="test.pdf"'

    p = canvas.Canvas(response)

    # Example: Fetch questions based on user input (simplified for demo)
    questions = Question.objects.filter(id__gte=start_id, id__lte=end_id)[:num_questions]

    y_position = 800
    for question in questions:
        p.drawString(100, y_position, question.question_text)
        y_position -= 100

    p.showPage()
    p.save()
    return response
