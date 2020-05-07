import boto3
import csv
import datetime


today = datetime.datetime.strptime("11/05/2020", "%d/%m/%Y")
print(today)


def pats_from_aws(date):
    s3 = boto3.resource('s3')

    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)

    try:
        s3.Object('dec601', 'patients.csv').download_file('test_data.csv')
    except Exception as e:
        print(e)

    #  make a list of patient bookings for one endoscopist for a specific day
    bookings_dic = {}
    mrn_dic = {}
    with open('test_data.csv') as h:
        reader = csv.reader(h)
        for patient in reader:
            correct_date = datetime.datetime.strptime(
                patient[0], "%d/%m/%Y") == date
            # correct_doctor = patient[1] == doc
            if correct_date:
                if patient[1] in bookings_dic:
                    bookings_dic[patient[1]].append((patient[3], patient[6]))
                else:
                    bookings_dic[patient[1]] = []
                    bookings_dic[patient[1]].append((patient[3], patient[6]))

                mrn_dic[patient[3]] = patient[2]

    return bookings_dic, mrn_dic


def get_list_from_dic(doctor, booking_dic):
    if doctor not in booking_dic:
        return ["Use Blue Chip"]
    else:
        lop = booking_dic[doctor]
        lop = sorted(lop, key=lambda x: x[1])
        return_list = ["Use Blue Chip"]
        for p in lop:
            return_list.append(p[0])
        return return_list


if __name__ == "__main__":
    print(pats_from_aws(today))
    book, mrns = pats_from_aws(today)
    print(get_list_from_dic('Stoita', book))
