import csv
import datetime
from pathlib import Path

from tempfile import NamedTemporaryFile
import shutil


today = datetime.datetime.today()


def update_day_surgery_csv(filename, new_row):
    # Create temporary file,
    temp_file = NamedTemporaryFile(mode="w", delete=False, newline="")

    found = False

    date = new_row[0]
    mrn = new_row[1]
    with open(filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, dialect="excel", lineterminator="\n")
        writer = csv.writer(temp_file)
        # Check each row
        for row in reader:
            if row[0] == date and row[1] == mrn:
                # Replace matching row with new data
                writer.writerow(new_row)
                found = True

            else:
                writer.writerow(row)

        # Add new row if no match was found
        if not found:
            writer.writerow(new_row)
    # Replace original file with updated temp file
    temp_file.close()
    shutil.move(temp_file.name, filename)


today_str_for_ds = today.strftime("%d-%m-%Y")
data_for_day_surgery = [
    today_str_for_ds,
    mrn,
    in_theatre,
    out_theatre,
    anaesthetist,
    endoscopist,
    asa,
    upper,
    colon,
    banding,
    nurse,
    clips,
    glp1,
    message,
]


# csv_address = Path(".") / "day_surgery_new.csv"
# ds_csv_address = epdata_path / "day_surgery_new.csv"

# update_day_surgery_csv(ds_csv_address, data_for_day_surgery)


if __name__ == "__main__":
    today_str = today.strftime("%d-%m-%Y")
    ds_csv_address = Path(".") / "day_surgery_new.csv"
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "125", "", "", "", "", "", "", "32093", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "126", "", "", "", "", "", "", "32084", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "127", "", "", "", "", "", "", "32222", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "128", "", "", "", "", "", "", "32223", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "129", "", "", "", "", "", "", "32222", "", "", "", "", ""],
    # )
    update_day_surgery_csv(
        ds_csv_address,
        [today_str, "136", "first", "", "", "", "", "", "32228", "", "", "", "", ""],
    )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "135", "second", "", "", "", "", "", "32093", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "132", "", "", "", "", "", "", "32224", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "133", "", "", "", "", "", "", "", "", "", "", "", ""],
    # )
    # update_day_surgery_csv(
    #     ds_csv_address,
    #     [today_str, "134", "third", "", "", "", "", "", "32093", "", "", "", "", ""],
    # )

    """
    Things to do when adding to docbill

    Check   from tempfile import NamedTemporaryFile
            import shutil
         
         replace  day_surgery_to_csv  at line 539 with  update_day_surgery_csv

         put into line 1727

             today_str_for_ds = today.strftime("%d-%m-%Y")
            data_for_day_surgery = [
                today_str_for_ds,
                mrn,
                in_theatre,
                out_theatre,
                anaesthetist,
                endoscopist,
                asa,
                upper,
                colon,
                banding,
                nurse,
                clips,
                glp1,
                message,
            ]

            put over old call to day_surgery_to_csv

                ds_csv_address = epdata_path / "day_surgery_new.csv"

                update_day_surgery_csv(ds_csv_address, data_for_day_surgery)

"""
