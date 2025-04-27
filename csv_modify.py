import csv

with open("day_surgery.csv") as f1, open("episodes.csv", "w") as f2:
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
