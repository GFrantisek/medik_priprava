from fpdf import FPDF
import psycopg2

db_params = {
    "dbname": "medicina_tests_final",
    "user": "postgres",
    "password": "Skola2011x@",
    "host": "localhost",
    "port": "5432"
}

def connect_db(params):
    return psycopg2.connect(**params)

def fetch_questions_and_answers(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT question_id, question_text
            FROM MedQuestions
            WHERE question_id BETWEEN 1 AND 100
            ORDER BY RANDOM()
            LIMIT 30;
        """)
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
    pdf.add_font('DejaVu', '', r'C:\Users\frant\Downloads\DejaVu_Sans\DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', r'C:\Users\frant\Downloads\dejavu_sans (1)\DejaVu_Sans\DejaVuSansCondensed-Bold.ttf', uni=True)

    answer_labels = ['a', 'b', 'c', 'd']

    for i, (q_id, data) in enumerate(question_answers.items(), start=1):
        pdf.set_font('DejaVu', 'B', 10)  
        question_text_with_id = f"{i}. {data['text']} (ID:{q_id})"
        pdf.multi_cell(0, 8, question_text_with_id)  

        pdf.set_font('DejaVu', '', 9)  
        for index, answer in enumerate(data['answers']):
            answer_id, answer_text, is_correct = answer
            label = answer_labels[index % len(answer_labels)] 
            prefix = ""
            answer_specific_number = ( answer_id % 8 )+ 1
            answer_text_with_label_and_number = f"{label}. {prefix}{answer_text} ({answer_specific_number})"
            pdf.multi_cell(0, 6, answer_text_with_label_and_number) 

    pdf.output(filename)


if __name__ == "__main__":
    conn = connect_db(db_params)
    question_answers = fetch_questions_and_answers(conn)
    pdf_filename = "prvych_100.pdf"
    create_pdf(question_answers, pdf_filename)
    conn.close()
    print(f"PDF generated: {pdf_filename}")
