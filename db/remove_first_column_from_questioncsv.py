import csv


def remove_csv_question_id_column(input_file, output_file):
    with open(input_file, newline='', encoding='Windows-1250') as infile, open(output_file, 'w', newline='',
                                                                        encoding='Windows-1250') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        # Get the header row
        header = next(reader)

        # Identify the index of 'csv_question_id' column
        try:
            csv_question_id_index = header.index('csv_question_id')
        except ValueError:
            print("The 'csv_question_id' column was not found in the CSV file.")
            return

        # Remove the 'csv_question_id' column from the header
        header.pop(csv_question_id_index)

        # Write the new header
        writer.writerow(header)

        # Process each row and remove the 'csv_question_id' column
        for row in reader:
            # Check if the row has enough columns to remove the specified index
            if len(row) > csv_question_id_index:
                row.pop(csv_question_id_index)

            # Write the modified row to the output CSV
            writer.writerow(row)


# Specify input and output file paths
input_csv = 'med_questions_cleaned.csv'
output_csv = 'med_questions_cleaned_without_first_ROW.csv'

# Call the function to remove the 'csv_question_id' column
remove_csv_question_id_column(input_csv, output_csv)

print(f"CSV file with 'csv_question_id' column removed saved to {output_csv}")
