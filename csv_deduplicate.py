""" This will run through day_surgery.csv and remove
any duplication of entries with the same date and mrn.
The last entry of any duplicates is assumed
to be the one we want to keep.
It writes each day's entries into a dictionary which acts
like a set.
It is only to be run once - when the regular csv writer is bug free."""

import csv

previous_date = "19-10-2020"
# in production make this the first date in day_surgery.csv

day_dict = {}

old_csv = "old_csv.csv"
#  in production old_csv = "d:\\john tillet\\episode_data\\day_surgery.csv"

with open(old_csv, "r") as oldcsv, open("new_csv.csv", "a") as new_csv:
    reader = csv.reader(oldcsv)
    writer = csv.writer(new_csv)
    for entry in reader:
        current_date = entry[0]
        if current_date != previous_date:
            # print(f"  {previous_date}    {day_dict}")
            for value in day_dict.values():
                writer.writerow(value)
            day_dict = {entry[1]: entry}
            previous_date = current_date
        else:
            day_dict[entry[1]] = entry
    # print(f" final day   {current_date}    {day_dict}")
    for value in day_dict.values():
        writer.writerow(value)
