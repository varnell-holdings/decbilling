import csv
import pyautogui as pya


def episode_close():
    pya.hotkey('alt', 'f4')


def episode_to_csv(endoscopist, consultant, anaesthetist, nurse,
                   upper, lower, anal, postcode, dob):
    episode_data = (endoscopist, consultant, anaesthetist, nurse,
                    upper, lower, anal, postcode, dob)
    csvfile = 'medical_data.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)
