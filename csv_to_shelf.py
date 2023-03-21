"""transfer data from csv to shelf. csv conatains various day surgery data.
last_colon.db shelve will have key of mrn and value a datetime.datetime object.
This will be used to fill shelf with old data in a legacy csv - one time use"""

import csv
from dateutil.parser import parse
import shelve


def csv_to_shelf():
    colon_codes = {'32090', '32093', '32222', '32223', '32224', '32225', '32226', '32227', '32228'}
    csv_address = "D:\\Nobue\\day_surgery.csv"
    shelve_address = "D:\\Nobue\\last_colon_day"

    with shelve.open(shelve_address) as s:
        with open(csv_address, mode='r') as handle:
            datareader = csv.reader(handle, dialect="excel", lineterminator="\n")
            for episode in datareader:
                date_proc = episode[0]
                mrn = episode[1]
                colon = episode[8]
                if colon in colon_codes:
                    date_as_datetime = parse(date_proc, dayfirst=True)
                    date_as_date_object = date_as_datetime.date()
                    s[mrn] = date_as_date_object

if __name__ == '__main__':
    csv_to_shelf()
