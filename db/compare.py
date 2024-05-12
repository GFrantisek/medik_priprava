import csv


def compare_csv_on_second_column(file1, file2):
    with open(file1, newline='', encoding='Windows-1250') as f1, open(file2, newline='', encoding='Windows-1250') as f2:
        reader1 = csv.reader(f1, delimiter=';')
        reader2 = csv.reader(f2, delimiter=';')

        rows1 = list(reader1)
        rows2 = list(reader2)

        # Assuming the files have headers, skip them
        header1 = rows1.pop(0)
        header2 = rows2.pop(0)

        differences = []

        max_rows = max(len(rows1), len(rows2))

        for i in range(max_rows):
            row1 = rows1[i] if i < len(rows1) else None
            row2 = rows2[i] if i < len(rows2) else None

            # Extract the second column for comparison
            answer_text1 = row1[1] if row1 and len(row1) > 1 else None
            answer_text2 = row2[1] if row2 and len(row2) > 1 else None

            if answer_text1 != answer_text2:
                differences.append((row1, row2))

        return header1, differences


def print_differences(header, differences):
    print("Differences found in the second column:")
    print("Header:", header)
    for row1, row2 in differences:
        print(f"CSV before: {row1}")
        print(f"CSV after: {row2}")
        print("----")


# Specify the paths to the CSV files
csv_before = 'questions.csv'
csv_after = 'med_questions_cleaned.csv'

# Compare the CSV files on the second column
header, differences = compare_csv_on_second_column(csv_before, csv_after)

# Print the differences
if differences:
    print_differences(header, differences)
else:
    print("No differences found in the second column.")
