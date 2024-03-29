# backend_django/backend_django/utils.py
import os
from fpdf import FPDF
import psycopg2
from reportlab.lib import pagesizes
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from backend_django import settings

db_params = {
    "dbname": "medicina",
    "user": "madmin",
    "password": "Skola2011xT",
    "host": "medicina.cp4mikq0waak.eu-north-1.rds.amazonaws.com",
    "port": "5432"
}


# Connect to the database
def connect_db(params):
    return psycopg2.connect(**params)


# Fetch questions and answers
def fetch_questions_and_answers(conn, num_questions, start_question, end_question):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT question_id, question_text
                    FROM MedQuestions
                    WHERE question_id BETWEEN %s AND %s
                    ORDER BY RANDOM()
                    LIMIT %s;
                """, (start_question, end_question, num_questions))
        questions = cur.fetchall()

        question_answers = {}
        for question_id, question_text in questions:
            cur.execute("""
                SELECT answer_id, answer_text, is_correct
                FROM MedAnswers
                WHERE question_id = %s
                ORDER BY RANDOM()
                LIMIT 4;
            """, (question_id,))
            answers = cur.fetchall()
            question_answers[question_id] = {
                'text': question_text,
                'answers': answers
            }
    return question_answers
    pass


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 10)
        self.cell(0, 10, f'Strana {self.page_no()}', 0, 0, 'C')
    pass



def create_pdf(question_answers, filename):
    regular_font_path = os.path.join(settings.BASE_DIR, 'static', 'DejaVu_Sans', 'DejaVuSansCondensed.ttf')
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'dejavu_sans (1)', 'DejaVu_Sans',
                                  'DejaVuSansCondensed-Bold.ttf')

    pdf = PDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', regular_font_path, uni=True)
    pdf.add_font('DejaVu', 'B', bold_font_path, uni=True)

    for i, (q_id, data) in enumerate(question_answers.items(), start=1):
        pdf.set_font('DejaVu', 'B', 12)  # Larger font size for questions
        question_text_with_id = f"{i}. {data['text']}"
        pdf.multi_cell(0, 7, question_text_with_id)  # Adjusted line height

        pdf.set_font('DejaVu', '', 9)  # Regular font for answers
        for index, answer in enumerate(data['answers']):
            answer_id, answer_text, _ = answer
            finalid = answer_id % 8
            if finalid == 0:
                finalid = 8

            label = ['A', 'B', 'C', 'D'][index % 4]
            answer_text_with_label = f"{label}. {answer_text}"
            pdf.multi_cell(0, 6, answer_text_with_label)

        # Add some space after the block of answers, before the next question
        pdf.ln(10)  # Adjust the parameter to increase or decrease the space

    pdf.output(filename)


def create_pdf_with_correct_answers(question_answers, filename):

    regular_font_path = os.path.join(settings.BASE_DIR, 'static', 'DejaVu_Sans', 'DejaVuSansCondensed.ttf')
    bold_font_path = os.path.join(settings.BASE_DIR, 'static', 'dejavu_2', 'DejaVu_Sans',
                                  'DejaVuSansCondensed-Bold.ttf')
    pdf = PDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', regular_font_path, uni=True)
    pdf.add_font('DejaVu', 'B', bold_font_path, uni=True)

    for i, (q_id, data) in enumerate(question_answers.items(), start=1):
        pdf.set_font('DejaVu', 'B', 12)  # Larger font size for questions
        question_text_with_id = f"{i}. {data['text']} (ID: {q_id})"
        pdf.multi_cell(0, 7, question_text_with_id)  # Adjusted line height

        for index, answer in enumerate(data['answers']):
            answer_id, answer_text, is_correct = answer
            label = ['A', 'B', 'C', 'D'][index % 4]
            answer_text_with_label = f"{label}. {answer_text} (ID: {answer_id})"
            if is_correct:
                pdf.set_font('DejaVu', 'B', 9)  # Bold for correct answer
            else:
                pdf.set_font('DejaVu', '', 9)  # Regular font for other answers
            pdf.multi_cell(0, 6, answer_text_with_label)

        # Add some space after the block of answers, before the next question
        pdf.ln(10)  # Adjust the parameter to increase or decrease the space

    pdf.output(filename)



def create_pdf_table(output_filename):
    pdf = SimpleDocTemplate(output_filename, pagesize=pagesizes.letter)
    elements = []

    square_size = 0.4 * inch
    colWidths = [square_size for _ in range(5)]

    data = [[' ', 'A', 'B', 'C', 'D']]

    for num in range(1, 11):
        row = [str(num)] + [' ' for _ in range(4)]
        data.append(row)

    table = Table(data, colWidths=colWidths)

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), square_size / 2),
        ('TOPPADDING', (0, 0), (-1, -1), square_size / 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(table_style)

    elements.append(table)
    pdf.build(elements)
    pass
