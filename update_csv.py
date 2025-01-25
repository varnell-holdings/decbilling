import csv
from tempfile import NamedTemporaryFile
import shutil


def update_csv(filename, new_row, date, event_id):
    # Create temporary file
    temp_file = NamedTemporaryFile(mode="w", delete=False, newline="")

    found = False
    with open(filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, dialect="excel", lineterminator="\n")
        writer = csv.writer(temp_file)
        # Check each row
        for row in reader:
            if row[0] == date and row[2] == event_id:
                # Replace matching row with new data
                writer.writerow(new_row)
                found = True

            else:
                writer.writerow(row)

        # Add new row if no match was found
        if not found:
            writer.writerow(new_row)
    # Replace original file with updated temp file
    shutil.move(temp_file.name, filename)
