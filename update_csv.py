import csv
from tempfile import NamedTemporaryFile
import shutil


def update_csv(filename, new_row, date, event_id):
    # Create temporary file
    temp_file = NamedTemporaryFile(mode="w", delete=False, newline="")

    found = False
    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        writer = csv.DictWriter(temp_file, fieldnames=reader.fieldnames)
        writer.writeheader()

        # Check each row
        for row in reader:
            if row["date"] == date and row["id"] == event_id:
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


# Example usage:
new_event = {"date": "2024-01-18", "id": "12345", "description": "Updated event"}

update_csv("events.csv", new_event, new_event["date"], new_event["id"])
