import sys
import time

import colorama
import pyautogui

from inputbill import inputer, LoopException
from functions import (make_webpage, episode_scrape, episode_opener, offsite,
                       episode_theatre, episode_procedures, episode_discharge,
                       analysis, update_web, bill_process,
                       to_csv, make_episode_string, EpFullException)


colorama.init(autoreset=True)


def intro(anaesthetist, endoscopist, nurse):
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

    try:
        data_entry = inputer(consultant, anaesthetist)
        # if data_entry == 'loop':
        #     return

        (asa, upper, colon, banding, consult, message, op_time,
         ref, full_fund, insur_code, fund_number, clips, varix_flag, varix_lot,
         in_theatre, out_theatre) = data_entry

        message = episode_opener(message)
        episode_discharge(in_theatre, out_theatre, anaesthetist, endoscopist)
        # if ret == 'ep full':
        #     return
        episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot)
        episode_procedures(upper, colon, banding, asa)
        mrn, print_name, address, dob, mcn = episode_scrape()

        if asa and anaesthetist == 'Dr J Tillett':
            ae_csv, ae_db_dict = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                print_name, address, ref, full_fund, fund_number, endoscopist)

            to_csv(ae_csv)

        episode_string = make_episode_string(
            out_theatre, room, endoscopist, anaesthetist, print_name, consult,
            upper, colon, message)

        webpage = make_webpage(episode_string)

        offsite(webpage)

        time.sleep(1)

        pyautogui.click(x=780, y=90)
    except LoopException, EpFullException:
        return
