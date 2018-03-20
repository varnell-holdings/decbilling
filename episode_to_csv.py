"""episode_to_csv
need to make episode_data/csv and episode_data/csv/backup folders on d drive
"""


import datetime
import csv
import os
import glob
import shutil


def episode_to_csv(outtime, room, endoscopist, anaesthetist, patient,
                   consult, upper, colon, message, banding, clips, varix_flag, mrn):
    """Write episode data data to csv."""
    doc_surname = endoscopist.split()[-1]
    if doc_surname == 'Vivekanandarajah':
        doc_surname = 'Suhir'
    anaesthetist_surname = anaesthetist.split()[-1]
    docs = doc_surname + '/' + anaesthetist_surname

    if not consult:
        consult = ''
    if not upper:
        upper = ''
    if not colon:
        colon = ''

    episode_data = (outtime, room, docs, patient,
                    consult, upper, colon, message, banding, clips, varix_flag)
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    if os.path.isfile(today_path):
        with open(today_path, 'a') as handle:
            datawriter = csv.writer(
                handle, dialect='excel', lineterminator='\n')
            datawriter.writerow(episode_data)
    else:
        # move old files to episode-csv folder
        base = 'd:\\JOHN TILLET\\episode_data\\csv\\'
        dest = 'd:\\JOHN TILLET\\episode_data\\csv\\csv-backup'
        for src in glob.glob(base + '*.csv'):
            shutil.move(src, dest)
        with open(today_path, 'w') as handle:
            datawriter = csv.writer(
                handle, dialect='excel', lineterminator='\n')
            datawriter.writerow(episode_data)
