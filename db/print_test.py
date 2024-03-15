from fpdf import FPDF
import psycopg2
from reportlab.lib import pagesizes
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# Database connection parameters
db_params = {
    "dbname": "medicinapriprava",
    "user": "madmin",
    "password": "Skola2011x12tfv",
    "host": "medicinapriprava.cp4mikq0waak.eu-north-1.rds.amazonaws.com",
    "port": "5432"
}


# Connect to the database
def connect_db(params):
    return psycopg2.connect(**params)


# Fetch questions and answers
def fetch_questions_and_answers(conn):
    with conn.cursor() as cur:
        # Select 30 random questions with ID between 1 to 40
        cur.execute("""
            SELECT question_id, question_text
            FROM MedQuestions
            WHERE question_id BETWEEN 1 AND 217
            ORDER BY RANDOM()
            LIMIT 217;
        """)
        questions = cur.fetchall()

        # For each question, select 4 answers including answer_id
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


class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 10)
        self.cell(0, 10, f'Strana {self.page_no()}', 0, 0, 'C')


def create_pdf(question_answers, filename):
    pdf = PDF()
    pdf.add_page()
    # Assuming the paths to font files are correctly set for your environment
    # Load the DejaVu font family, including bold
    # MAKE PATH INTO PROJECT FOLDER
    # office path
    pdf.add_font('DejaVu', '', r'C:\Users\frant\Downloads\dejavu_sans\DejaVu_Sans\DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', r'C:\Users\frant\Downloads\dejavu_sans (1)\DejaVu_Sans\DejaVuSansCondensed-Bold.ttf',
                 uni=True)

    # notebook path
    # pdf.add_font('DejaVu', '', r'C:\Users\frant\Downloads\DejaVu_Sans\DejaVuSansCondensed.ttf', uni=True)
    # pdf.add_font('DejaVu', 'B', r'C:\Users\frant\Downloads\dejavu_sans (1)\DejaVu_Sans\DejaVuSansCondensed-Bold.ttf',
    #            uni=True)

    for i, (q_id, data) in enumerate(question_answers.items(), start=1):
        # Include question ID in the question text
        pdf.set_font('DejaVu', 'B', 10)  # Bold for question
        question_text_with_id = f"{i}. {data['text']} (ID:{q_id})"
        pdf.multi_cell(0, 8, question_text_with_id)  # Adjust line height for question

        pdf.set_font('DejaVu', '', 9)  # Regular font for answers
        for index, answer in enumerate(data['answers']):
            answer_id, answer_text, is_correct = answer
            label = ['A', 'B', 'C', 'D'][index % 4]  # Cycling through 'A', 'B', 'C', 'D'
            # Include answer ID in the answer text

            answer_final_id = answer_id % 8;
            if answer_final_id == 0: answer_final_id = 8;
            answer_text_with_label = f"{label}. {answer_text} ({answer_final_id})"
            pdf.multi_cell(0, 6, answer_text_with_label)  # Adjust line height for answers

    pdf.output(filename)


def create_pdf_table(output_filename):
    pdf = SimpleDocTemplate(output_filename, pagesize=pagesizes.letter)
    elements = []

    # Define the square size for uniformity across all cells
    square_size = 0.4 * inch
    # Set all columns to the square size, including the column for question numbers
    colWidths = [square_size for _ in range(5)]  # 1 for the question number + 4 for A, B, C, D

    # Header row with bold labels for ABCD. Removing question text implies removing 'Question' label
    data = [[' ', 'A', 'B', 'C', 'D']]  # Use space ' ' for the first column since question text is removed

    # Generate data rows with squares for answers
    for num in range(1, 11):  # Example for 10 "questions"
        row = [str(num)] + [' ' for _ in range(4)]  # Use spaces for answer squares to maintain uniformity
        data.append(row)

    table = Table(data, colWidths=colWidths)

    # Style adjustments for the table, emphasizing uniformity and square cells
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), square_size / 2),  # Adjust padding to match square size
        ('TOPPADDING', (0, 0), (-1, -1), square_size / 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(table_style)

    elements.append(table)
    pdf.build(elements)


# Main script
if __name__ == "__main__":
    conn = connect_db(db_params)
    question_answers = fetch_questions_and_answers(conn)
    pdf_filename = "prvych_100.pdf"
    create_pdf(question_answers, pdf_filename)
    output_filename = "table_like_pdf.pdf"
    create_pdf_table(output_filename)
    conn.close()
    print(f"PDF generated: {pdf_filename}")
