import csv


def remove_n_s_from_letter_column(input_file, output_file):
    with open(input_file, newline='', encoding='Windows-1250') as infile, open(output_file, 'w', newline='',
                                                                        encoding='Windows-1250') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        # Write header unchanged
        header = next(reader)
        writer.writerow(header)

        # Process each row and modify the 'Letter' column if necessary
        for row in reader:
            # Check that the 'Letter' column exists
            if len(row) > 5 and row[5] in ['N', 'S']:
                # Clear the 'Letter' column value
                row[5] = ''

            # Write the modified row to the output CSV
            writer.writerow(row)


# Specify input and output file paths
input_csv = 'med_answers_cleaned.csv'
output_csv = 'med_answers_cleaned_without_NS.csv'

# Call the function to process the CSV
remove_n_s_from_letter_column(input_csv, output_csv)

print(f"Processed CSV saved to {output_csv}")
