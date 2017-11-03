import sys

import colorama
import pyautogui

from inputbill import inputer
from functions import (make_index, episode_scrape, episode_opener, offsite,
                       episode_theatre, episode_procedures, episode_discharge,
                       analysis, update_web, bill_process,
                       to_csv, make_episode_string)

class QuitInputError(Exception):
        pass


def intro(anaesthetist, endoscopist, nurse):
    colorama.init(autoreset=True)
    print('\033[2J')  # clear screen
    print('Current team is:\nEndoscopist: {1}\nAnaesthetist:'
          ' {0}\nNurse: {2}'.format(anaesthetist, endoscopist, nurse))
    print()
    while True:
        print('To accept press enter\nTo change team press c\n'
              'To redo a patient press r\nTo send a message to receptionists'
              ' press m\nTo quit program press q')
        choice = input()
        if choice in {'q', '', 'c', 'r', 'm', 'a', 'u'}:
            break
    if choice == 'q':
        print('Thanks. Bye!')
        sys.exit(0)
    else:
        return choice


def bill(anaesthetist, endoscopist, consultant, nurse, room):
    choice = intro(anaesthetist, endoscopist, nurse)
    if choice == '':
        pass
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
        return

    data_entry = inputer(consultant, anaesthetist)
    if data_entry == 'loop':
        return

    (asa, upper, colon, banding, consult, message, op_time,
     ref, full_fund, insur_code, fund_number, clips, varix_flag, varix_lot,
     in_formatted, out_formatted, today_for_db) = data_entry

    message = episode_opener(message)
    ret = episode_discharge(
        in_formatted, out_formatted, anaesthetist, endoscopist)
    if ret == 'ep full':
        return
    episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot)
    episode_procedures(upper, colon, banding, asa)
    mrn, print_name, address, dob, mcn = episode_scrape()

    if asa and anaesthetist == 'Dr J Tillett':
        anaesthetic_data_for_csv = bill_process(
            dob, upper, colon, asa, mcn, insur_code, op_time,
            print_name, address, ref, full_fund, fund_number, endoscopist)

        to_csv(anaesthetic_data_for_csv)

#    episode_data_for_db = {
#        'mrn': mrn, 'in_time': in_formatted,
#        'out_time': out_formatted, 'anaesthetist': anaesthetist,
#        'nurse': nurse, 'upper': upper, 'lower': colon,
#        'banding': banding, 'asa': asa, 'today': today_for_db,
#        'name': print_name, 'consult': consult, 'message': message,
#        'endoscopist': endoscopist, 'anaesthetic_time': op_time,
#        'consultant': consultant}
#
#    to_database(episode_data_for_db)

    episode_string = make_episode_string(
        out_formatted, endoscopist, print_name, consult,
        upper, colon, message, anaesthetist, room)

    stored_index = make_index(episode_string)

    offsite(stored_index)

#    time.sleep(1)

    pyautogui.click(x=780, y=90)
