import csv
import psycopg2


def connect_db():
    return psycopg2.connect(
        dbname="medicina",
        user="madmin",
        password="Skola2011xT",
        host="medicina.cp4mikq0waak.eu-north-1.rds.amazonaws.com",
        port="5432"
    )


def clear_tables():
    conn = None
    cur = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        # Truncating the tables to delete all data and reset primary key sequences
        cur.execute("TRUNCATE TABLE MedAnswers, MedQuestions RESTART IDENTITY CASCADE;")
        conn.commit()
        print("Tables have been truncated and IDs reset.")
    except Exception as error:
        print("Error clearing tables:", error)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_questions_from_csv(csv_filepath):
    questions_inserted = {}
    conn = None
    cur = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        with open(csv_filepath, mode='r', encoding='Windows-1250') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for idx, row in enumerate(csv_reader, 1):
                cur.execute(
                    "INSERT INTO MedQuestions (question_text, question_image, question_category) VALUES (%s, %s, %s) RETURNING question_id;",
                    (row["question_text"], row.get("question_image", None), row["question_category"]))
                question_id = cur.fetchone()[0]
                questions_inserted[idx] = question_id
        conn.commit()
    except Exception as error:
        print("Error inserting questions:", error)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return questions_inserted


def insert_answers_from_csv(csv_filepath, questions_inserted):
    conn = None
    cur = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        with open(csv_filepath, mode='r', encoding='Windows-1250') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            for row in csv_reader:
                question_id = questions_inserted.get(int(row["csvquestionid"]))
                if question_id:
                    cur.execute(
                        "INSERT INTO MedAnswers (answer_text, answer_image, question_id, is_correct, explanation) VALUES (%s, %s, %s, %s, %s);",
                        (row["answertext"], row.get("answerimage", None), question_id,
                         row["iscorrect"].strip().lower() in ('true', '1', 't'), row.get("explanation", '')))
        conn.commit()
    except Exception as error:
        print("Error inserting answers:", error)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def main():
    answers_csv_path = "med_answers_cleaned_without_NS.csv"
    questions_csv_path = "med_questions_cleaned_without_first_ROW.csv"

    # Clear existing data and reset IDs
    clear_tables()

    # Insert new data
    questions_inserted = insert_questions_from_csv(questions_csv_path)
    insert_answers_from_csv(answers_csv_path, questions_inserted)


if __name__ == '__main__':
    main()
