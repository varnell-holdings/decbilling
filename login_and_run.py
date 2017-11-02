import pprint

import colorama

import names_and_codes as nc
from bill import bill
from inputbill import inputer
from functions import (make_message_string, offsite,
                       make_webpage, episode_update)


def get_anaesthetist():
    while True:
        initials = input('Anaesthetist:  ').lower()
        if initials in nc.ANAESTHETISTS:
            anaesthetist = nc.ANAESTHETISTS[initials]
            break
        else:
            pprint.pprint(nc.ANAESTHETISTS)
    return anaesthetist


def get_endoscopist():
    while True:
        print()
        initials = input('Endoscopist:  ').lower()
        if initials in nc.DOC_DIC:
            endoscopist = nc.DOC_DIC[initials]
            print(endoscopist)
            break
        else:
            pprint.pprint(nc.DOC_DIC)

    if endoscopist in nc.LOCUMS:  # inputer depends on doctor not locum
        while True:
            initials = input('Who is Dr {} covering? '.format(
                endoscopist.split()[-1])).lower()
            if nc.DOC_DIC[initials] in nc.PARTNERS:
                consultant = nc.DOC_DIC[initials]
                print(consultant)
                break
            else:
                pprint.pprint(nc.PARTNERS)
    else:
        consultant = endoscopist
    return endoscopist, consultant


def get_nurse():
    while True:
        print()
        initials = input('Nurse:  ')
        if initials in nc.NURSES_DIC:
            nurse = nc.NURSES_DIC[initials]
            print(nurse)
            break
        else:
            pprint.pprint(nc.NURSES_DIC)
    return nurse


def login_and_run(s):
    colorama.init(autoreset=True)
    room = s
    while True:
        print('\033[2J')  # clear screen
        print('To login type your initials and press enter')
        print('To see if you are in the system press enter')
        print('Login as "locum" otherwise')
        print('Press the enter key in most places to get help')
        print('To restart if you make an error press q then enter')
        anaesthetist = get_anaesthetist()

        print ('\nWelcome Dr {}!\n'.format(
            anaesthetist.split()[-1]))

        if anaesthetist in nc.REGULAR_ANAESTHETISTS:
            input('Please let Kate know if you\nhave any'
                  ' upcoming change in your roster.\nPress enter to continue')
        endoscopist, consultant = get_endoscopist()

        nurse = get_nurse()

        while True:
            choice = bill(anaesthetist, endoscopist, consultant, nurse, room)
            if choice == 'change team':
                break
            if choice == 'redo':
                data_entry = inputer(consultant, 'locum')
                episode_update(room, endoscopist, anaesthetist, data_entry)
            if choice == 'message':
                message_string = make_message_string(anaesthetist)
                webpage = make_webpage(message_string)
                offsite(webpage)


if __name__ == '__main__':
    login_and_run('R2')
