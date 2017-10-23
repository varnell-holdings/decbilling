import names_and_codes as nc
from bill import bill
from inputbill import inputer
from functions import (get_anaesthetist, get_endoscopist,
                       get_nurse, episode_update, send_message)


def login_and_run():
    while True:
        print('To login type your initials')
        print('To see if you are in the system type h')
        print('Login as locum otherwise')
        anaesthetist = get_anaesthetist()
        
        print ('\nWelcome Dr {}!\n'.format(
            anaesthetist.split()[-1]))

        if anaesthetist in nc.REGULAR_ANAESTHETISTS:
            print('Please let Kate know if you have any upcoming leave.\n')

        doctor, consultant = get_endoscopist()

        nurse = get_nurse()

        while True:
            choice = bill(anaesthetist, doctor, consultant, nurse)
            if choice == 'change team':
                break
            if choice == 'redo':
                data_entry = inputer(consultant, 'locum')
                episode_update(consultant, doctor, anaesthetist, data_entry)
            if choice == 'message':
                send_message(anaesthetist)


if __name__ == '__main__':
    login_and_run()
