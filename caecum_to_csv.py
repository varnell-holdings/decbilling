import csv
from datetime import datetime
from tempfile import NamedTemporaryFile
import shutil

today = datetime.today()

caecumfile = "caecum.csv"


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


def caecum_to_csv(doctor, mrn, caecum_flag, reason):
    """Write whether scope got to caecum and reason."""
    doctor = doctor.split()[-1]
    today_str = today.strftime("%Y-%m-%d")
    caecum_data = (today_str, doctor, mrn, caecum_flag, reason)
    csvfile = caecumfile
    update_csv(csvfile, caecum_data, today_str, mrn)


if __name__ == "__main__":
    caecum_to_csv("Wettstein", "1126", "fail", "Poor Prep")
