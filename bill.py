import sys
import time

import colorama
import pyautogui

from inputbill import inputer
from functions import (time_calculater, make_index, to_database,
                       episode_scrape, episode_opener, offsite,
                       episode_theatre, episode_procedures, episode_discharge,
                       analysis, update_web, bill_process, BlueChipError,
                       to_csv, update_number_this_week, make_episode_string)


def intro(anaesthetist, doctor, nurse):
    colorama.init(autoreset=True)
    print('\033[2J')  # clear screen
    print('Current team is:\nEndoscopist: {1}\nAnaesthetist:'
          ' {0}\nNurse: {2}'.format(anaesthetist, doctor, nurse))
    print()
    while True:
        print('To accept press enter\nTo change team press c\n'
              'To redo a patient press r\nTo send a message to receptionists'
              ' press m\nTo quit program press q')
        choice = input()
        if choice in {'', 'c', 'q', 'a', 'u', 'r', 'm'}:
            break
    if choice == 'q':
        print('Thanks. Bye!')
        sys.exit(0)
    elif choice == '':
        return
    else:
        return choice


def bill(anaesthetist, doctor, consultant, nurse, room):
    choice = intro(anaesthetist, doctor, nurse)
    if choice == 'c':
        return 'change team'
    if choice == 'r':
        return 'redo'
    if choice == 'm':
        return 'message'
    if choice == 'a':
        analysis()
        input('Hit Enter to continue.')
        return
    if choice == 'u':
        update_web()
        input('Hit Enter to continue.')
        return
    data_entry = inputer(consultant, anaesthetist)

    (asa, upper, colon, banding, consult, message, time_in_theatre,
     ref, full_fund, insur_code, fund_number, clips,
     varix_flag, varix_lot) = data_entry

    (in_formatted, out_formatted,
     anaesthetic_time, today_for_db) = time_calculater(time_in_theatre)

    message = episode_opener(message)
    try:
        episode_discharge(in_formatted, out_formatted, anaesthetist, doctor)
    except BlueChipError:
        return
    episode_theatre(doctor, nurse, clips, varix_flag, varix_lot)
    episode_procedures(upper, colon, banding, asa)
    mrn, print_name, address, dob, mcn = episode_scrape()

    if asa != '0' and anaesthetist == 'Dr J Tillett':
        (proc_date, upper_done,
         lower_done, age_seventy,
         asa_three, invoice, mcn) = bill_process(dob, upper, colon, asa,
                                                 mcn, insur_code)

        jt_ep_data = [proc_date, print_name, address, dob, mcn, ref, full_fund,
                      fund_number, insur_code, doctor, upper_done, lower_done,
                      age_seventy, asa_three, anaesthetic_time, invoice]

        to_csv(jt_ep_data)

        update_number_this_week()

    episode_data_for_db = {
        'mrn': mrn, 'in_time': in_formatted,
        'out_time': out_formatted, 'anaesthetist': anaesthetist,
        'nurse': nurse, 'upper': upper, 'lower': colon,
        'banding': banding, 'asa': asa, 'today': today_for_db,
        'name': print_name, 'consult': consult, 'message': message,
        'doctor': doctor, 'anaesthetic_time': time_in_theatre,
        'consultant': consultant}

    to_database(episode_data_for_db)

    episode_string = make_episode_string(
        out_formatted, doctor, print_name, consult,
        upper, colon, banding, message, anaesthetist, room)

    stored_index = make_index(episode_string)

    offsite(stored_index)

    time.sleep(1)

    pyautogui.click(x=780, y=90)
