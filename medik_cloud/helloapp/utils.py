# backend_django/backend_django/utils.py
import os
import fpdf
import psycopg2
from helloproject.settings import BASE_DIR

from helloproject import settings
from django.templatetags.static import static

db_params = {
    "dbname": "medicina",
    "user": "madmin",
    "password": "Skola2011xT",
    "host": "medicina.cp4mikq0waak.eu-north-1.rds.amazonaws.com",
    "port": "5432"
}

regular_font_path = "helloapp/static/DejaVuSansCondensed.ttf"
bold_font_path = "helloapp/static/DejaVuSansCondensed-Bold.ttf"


# Connect` to the database
def connect_db(params):
    return psycopg2.connect(**params)


# Fetch questions and answers
def fetch_questions_and_answers(conn, num_questions, start_question, end_question):
    print("test")
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


class PDF(fpdf.FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 10)
        self.cell(0, 10, f'Strana {self.page_no()}', 0, 0, 'C')

    pass


def create_pdf(question_answers, filename):
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
    print(bold_font_path)

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
