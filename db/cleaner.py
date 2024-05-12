import csv
import re


# Function to process a single line of the CSV file
def process_line(line):
    if line.startswith('?'):
        # Remove leading question marks
        line = re.sub(r'^\?+', '', line)
    else:
        # Replace any sequence of one or more question marks with an underscore
        line = re.sub(r'\?+', '_', line)
    return line


# Read the input CSV file
input_file = 'med_answers.csv'
output_file = 'med_answers_cleaned.csv'

with open(input_file, newline='', encoding='Windows-1250') as infile, open(output_file, 'w', newline='',
                                                                    encoding='Windows-1250') as outfile:
    reader = csv.reader(infile, delimiter=';')
    writer = csv.writer(outfile, delimiter=';')

    # Write header unchanged
    header = next(reader)
    writer.writerow(header)

    # Process each line and write to output
    for row in reader:
        # Process only the 'question_text' field
        row[1] = process_line(row[1])
        writer.writerow(row)

print(f"Cleaned CSV saved to {output_file}")
