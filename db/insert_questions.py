
import csv
import psycopg2


def connect_db():
    return psycopg2.connect(
        dbname="medicina_tests_final",
        user="postgres",
        password="Skola2011x@",
        host="localhost",
        port="5432"
    )


def insert_questions_from_csv(csv_filepath):
    questions_inserted = {}
    question_counter = 1  # Start a counter for the question_id
    try:
        conn = connect_db()
        cur = conn.cursor()
        with open(csv_filepath, mode='r', encoding='Windows-1250') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                if row["question_text"]:  # Check if the row actually has question text to avoid blank lines
                    cur.execute(
                        "INSERT INTO MedQuestions (question_text, question_image, question_category) VALUES (%s, %s, %s) RETURNING question_id;",
                        (row["question_text"], row.get("question_image"), row["question_category"]))
                    question_id = cur.fetchone()[0]
                    questions_inserted[question_counter] = question_id  # Use the counter as the key
                    question_counter += 1
        conn.commit()
        cur.close()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return questions_inserted


def insert_answers_from_csv(csv_filepath, questions_inserted):
    try:
        conn = connect_db()
        cur = conn.cursor()
        with open(csv_filepath, mode='r', encoding='Windows-1250') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                csv_question_id = row["csv_question_id"].strip()
                if csv_question_id.isdigit():  # Check if csv_question_id is numeric
                    question_id = questions_inserted.get(int(csv_question_id))
                    if question_id:
                        cur.execute(
                            "INSERT INTO MedAnswers (answer_text, answer_image, question_id, is_correct, explanation) VALUES (%s, %s, %s, %s, %s);",
                            (row["answer_text"], row.get("answer_image"), question_id,
                             row["is_correct"].lower() in ('true', '1', 't'), row["explanation"]))
        conn.commit()
        cur.close()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#notas path
answers_csv_path = r"C:\Users\frant\OneDrive\Počítač\medik_priprava\db\answers.csv"

questions_csv_path = r"C:\Users\frant\OneDrive\Počítač\medik_priprava\db\questions.csv"

#kancelrasky pc path
#answers_csv_path = r"C:\Users\frant\Documents\GitHub\medik_priprava\db\answers.csv"
#questions_csv_path = r"C:\Users\frant\Documents\GitHub\medik_priprava\db\questions.csv"

questions_inserted = insert_questions_from_csv(questions_csv_path)
insert_answers_from_csv(answers_csv_path, questions_inserted)