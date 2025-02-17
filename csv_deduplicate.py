""" This will run through day_surgery.csv and remove
any duplication of entries with the same date and mrn.
The last entry of any duplicates is assumed
to be the one we want to keep.
It writes each day's entries into a dictionary which acts
like a set.
It is only to be run once - when the regular csv writer is bug free.
Writes to new_csv.csv which will have to replace day_surgery.csv
after checking all went well."""

import csv

# previous_date = "16-10-2020"
# in production make this the first date in day_surgery.csv

day_dict = {}
total_rows = 0
written_rows = 0
current_date = None

old_csv = "day_surgery.csv"
#  in production old_csv = "d:\\john tillet\\episode_data\\day_surgery.csv"

with open(old_csv, "r") as oldcsv, open("new_csv.csv", "w") as new_csv:
    reader = csv.reader(oldcsv)
    writer = csv.writer(new_csv)
    for entry in reader:
        total_rows += 1
        if "test" in entry[13].lower():
            continue
        date = entry[0]
        if current_date and date != current_date:
            # if we have moved to a new date, write dict to file, put new line in new dict and update current date
            for value in day_dict.values():
                writer.writerow(value)
                written_rows += 1
            day_dict = {entry[1]: entry}

        else:
            day_dict[entry[1]] = entry
        current_date = date
    # print(f" final day   {current_date}    {day_dict}")
    for value in day_dict.values():
        writer.writerow(value)
        written_rows += 1

print(f"Lines written:   ", written_rows)
print("Lines removed:   ", total_rows - written_rows)
