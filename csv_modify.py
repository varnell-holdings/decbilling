import csv
import pandas as pd

with open("day_surgery.csv") as f1, open("episodes_ext.csv", "w") as f2:
    reader = csv.reader(f1)
    writer = csv.writer(f2)
    for a in reader:
        if len(a) == 14:
            a.extend(["", "", "", "", "", ""])
        writer.writerow(a)

with open("episodes_ext.csv") as f1, open("episodes_intermediate.csv", "w") as f2:
    reader = csv.reader(f1)
    writer = csv.writer(f2)
    for a in reader:
        a[4] = a[4].split()[-1]
        a[5] = a[5].split()[-1]
        if a[6] == "":
            a[6] = 0
        else:
            a[6] = a[6][-2]
        if a[7] != "":
            a[7] = a[7].split("-")[0]
        a[10] = a[10].split()[-1]
        a[12] = ""
        a[13] = ""
        writer.writerow(a)


# Read the CSV file without headers
df = pd.read_csv("episodes_intermediate.csv", header=None)

# Define your headers
headers = [
    "date",
    "mrn",
    "in",
    "out",
    "anaes",
    "endo",
    "asa",
    "upper",
    "colon",
    "anal",
    "nurse",
    "clips",
    "free1",
    "free2",
    "caecum",
    "title",
    "firstname",
    "surname",
    "dob",
    "email",
]

# Assign the headers to the dataframe
df.columns = headers

# Save the file with headers
df.to_csv("episodes.csv", index=False)
