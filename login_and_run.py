# -*- coding: utf-8 -*-
from collections import namedtuple
import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import ftplib
import glob
import os
import os.path
import pickle
import pprint
import shutil
import sys
import time

import colorama
import dataset
import pyautogui as pya
import pyperclip
from tabulate import tabulate

from inputbill import (inputer, LoopException)
import names_and_codes as nc


class EpFullException(Exception):
    pass


LOGIN_STRING = """To login type your initials and press enter
To see if you are in the system press enter
Login as "locum" otherwise
To restart if you make an error press q"""


CHOICE_STRING = """To accept press enter
To change team press c
To redo a patient press r
To send a message to receptionists press m
To print a summary of today press ar
To quit program press q"""


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


def bill(anaesthetist, endoscopist, consultant, nurse, room):
    """Workhorse function"""
    try:
        data_entry = inputer(consultant, anaesthetist)

        (asa, upper, colon, banding, consult, message, op_time,
         ref, full_fund, insur_code, fund_number, clips, varix_flag, varix_lot,
         in_theatre, out_theatre) = data_entry

        message = episode_opener(message)
        episode_discharge(in_theatre, out_theatre, anaesthetist, endoscopist)

        episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot)
        episode_procedures(upper, colon, banding, asa)
        mrn, print_name, address, dob, mcn = episode_scrape()

        ae_csv, ae_db_dict = bill_process(
            dob, upper, colon, asa, mcn, insur_code, op_time,
            print_name, address, ref, full_fund, fund_number, endoscopist, anaesthetist)
        to_anaesthetic_database(ae_db_dict)

        if asa and anaesthetist == 'Dr J Tillett':
            to_csv(ae_csv)

        episode_string = make_episode_string(
            out_theatre, room, endoscopist, anaesthetist, print_name, consult,
            upper, colon, message)

        webpage = make_webpage(episode_string)

        offsite(webpage)

        pya.click(x=780, y=90)
    except (LoopException, EpFullException):
        return


def make_message_string(anaesthetist):
    message = input('Type your message. Your name is automatically included.')
    html = "<tr><td></td><td></td><td>Message from</td><td>{0}</td>\
            <td></td><td></td><td></td><td>{1}</td></tr>\n"
    message_string = html.format(anaesthetist, message)
    return message_string


def episode_update(room, endoscopist, anaesthetist, data_entry):
    # data_enry is a tuple -> unpack it
    (asa, upper, colon, banding, consult, message, op_time,
     ref, full_fund, insur_code, fund_number, clips, varix_flag,
     varix_lot, in_formatted, out_formatted) = data_entry

    message = episode_opener(message)
    episode_procedures(upper, colon, banding, asa)
    mrn, print_name, address, dob, mcn = episode_scrape()

    message += ' Updated this patient. Check Blue Chip is correct.'

    out_string = make_episode_string(
        out_formatted, endoscopist, print_name, consult,
        upper, colon, message, anaesthetist, room)
    webpage = make_webpage(out_string)
    offsite(webpage)
    time.sleep(1)
    pya.click(x=780, y=90)


def update_web():
    """Update the webpage. After index has been changed."""
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.html'
    base = 'd:\\JOHN TILLET\\episode_data\\'
    stored_index = os.path.join(base + date_filename)
    offsite(stored_index)


def analysis():
    """Print number of accounts ready to print and whether on weekly target."""

    csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\patients.csv'
    picklefile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\invoice_store.py'
    try:
        with open(csvfile, 'r') as file_handle:
            reader = csv.reader(file_handle)
            first_bill = next(reader)
            first_bill_invoice = int(first_bill[15])  # invoice from first acc
    except IOError:
        print("Can't find patients.csv")
        return
    with open(picklefile, 'rb') as handle:
        last_invoice = pickle.load(handle)
    print('Number on this print run - {}'.format(
        last_invoice - first_bill_invoice))
    first_date = datetime.datetime(2017, 7, 1)
    today = datetime.datetime.today()
    days_diff = (today - first_date).days
    desired_weekly = int(input('Weekly target: '))
    first_invoice = 5100
    invoice_diff = last_invoice - first_invoice
    desired_number = int(days_diff * desired_weekly / 7)
    excess = invoice_diff - desired_number
    print('{} excess to average {} per week.'.format(excess, desired_weekly))
    input('Hit Enter to continue.')


def episode_opener(message):
    while True:
        if not pya.pixelMatchesColor(150, 630, (255, 0, 0)):
            print('Open the patient file.')
            input('Hit Enter when ready.')
        else:
            break
    pya.moveTo(150, 50)
    pya.click()
    pya.press('f8')
    while not pya.pixelMatchesColor(534, 330, (102, 203, 234), tolerance=10):
        time.sleep(0.3)

    pya.press('n')
    while not pya.pixelMatchesColor(820, 130, (195, 90, 80), tolerance=10):
        time.sleep(1)

    pya.typewrite(['down'] * 11, interval=0.1)
    pya.press('enter')
    pya.hotkey('alt', 'f')
    time.sleep(1)
    if pya.pixelMatchesColor(520, 380, (25, 121, 202), tolerance=10):
        time.sleep(0.3)
        pya.press('enter')
        pya.press('c')
        pya.hotkey('alt', 'f4')
        time.sleep(1)
        pya.press('f8')
        time.sleep(1)
        pya.typewrite(['enter'] * 3, interval=1.0)
        message += ' New episode made'
    return message


def episode_discharge(intime, outtime, anaesthetist, endoscopist):
    pya.hotkey('alt', 'i')
    time.sleep(0.3)
    pya.typewrite(['enter'] * 4, interval=0.1)
    test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    test = pyperclip.paste()
    if test != 'empty':
        pya.alert(text='Data here already! Try Again', title='', button='OK')
        time.sleep(1)
        pya.hotkey('alt', 'f4')
        raise EpFullException
    pya.typewrite(intime)
    pya.typewrite(['enter'] * 2, interval=0.1)
    pya.typewrite(outtime)
    pya.typewrite(['enter'] * 3, interval=0.1)
    if anaesthetist != 'locum':
        pya.typewrite(['tab'] * 6, interval=0.1)
        pya.typewrite(anaesthetist)
        pya.typewrite('\n')
    else:
        pya.typewrite(['tab'] * 7, interval=0.1)
    pya.typewrite(endoscopist)


def episode_procedures(upper, lower, anal, asa):
    pya.hotkey('alt', 'p')
    if lower:  # first line - either upper or lower is always true
        pya.typewrite(lower + '\n')
        pya.press('enter')
    else:
        pya.typewrite(upper + '\n')
        pya.press('enter')
    pya.typewrite(['tab'] * 6, interval=0.1)
    if upper and lower:  # second line
        pya.typewrite(upper + '\n')
        pya.press('enter')
    elif anal:
        pya.typewrite(anal + '\n')
        pya.press('enter')
    else:
        if asa:
            pya.typewrite(asa + '\n')
            pya.press('enter')
        return
    pya.typewrite(['tab'] * 2, interval=0.1)
    if anal:  # third line
        pya.typewrite(anal + '\n')
        pya.press('enter')
    else:
        if asa:
            pya.typewrite(asa + '\n')
            pya.press('enter')
        return
    pya.typewrite(['tab'] * 2, interval=0.1)
    if asa:  # fourth line
        pya.typewrite(asa + '\n')
        pya.press('enter')


def episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot):
    pya.hotkey('alt', 'n')
    pya.typewrite(['left'] * 2, interval=0.1)
    pya.moveTo(50, 155)
    pya.click()
    pya.press('tab')
    doc_test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    doc_test = pyperclip.paste()
    if doc_test == 'Endoscopist':
        pya.press('tab')
        pya.typewrite(['enter'] * 2, interval=0.1)
        pya.moveTo(450, 155)
        pya.click()
        pya.typewrite(['tab'] * 2, interval=0.1)
        pya.typewrite(['enter'] * 2, interval=0.1)

    pya.moveTo(50, 155)
    pya.click()
    pya.typewrite(endoscopist)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    pya.moveTo(450, 155)
    pya.click()
    pya.typewrite(nurse)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    if clips != 0 or varix_flag is True:
        pya.moveTo(50, 350)
        pya.click()
        if varix_flag is True:
            pyperclip.copy('Boston Scientific Speedband Superview Super 7')
            pya.hotkey('ctrl', 'v')
            pya.press('enter')
            time.sleep(0.5)
            pyperclip.copy(varix_lot)
            pya.hotkey('ctrl', 'v')
            pya.press('enter')
            pya.typewrite(['tab'] * 2, interval=0.1)
        if clips != 0:
            pyperclip.copy('M00521230')
            for i in range(clips):
                pya.typewrite(['b', 'enter'], interval=0.2)
                time.sleep(0.5)
                pya.hotkey('ctrl', 'v')
                pya.press('enter')
                pya.typewrite(['tab'] * 2, interval=0.1)


def episode_scrape():
    pya.hotkey('alt', 'd')
    mcn = pyperclip.copy('')  # put '' on clipboard before each copy
    pya.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    title = pyperclip.paste()
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    first_name = pyperclip.paste()
    pya.typewrite(['tab'] * 2, interval=0.1)
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    last_name = pyperclip.paste()
    print_name = title + ' ' + first_name + ' ' + last_name
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    street_number = pyperclip.paste()
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    street_name = pyperclip.paste()
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    suburb = pyperclip.paste()
    suburb = suburb.lower()
    suburb = suburb.title()
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    postcode = pyperclip.paste()
    address = street_number + ' ' + street_name + ' ' + suburb + ' ' + postcode
    pya.press('tab')
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    dob = pyperclip.paste()
    pya.typewrite(['tab'] * 6, interval=0.1)
    mcn = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    mcn = pyperclip.paste()
    pya.hotkey('alt', 'f4')
    return (mrn, print_name, address, dob, mcn)


def get_age_difference(bc_dob):
    today_raw = datetime.datetime.today()
    dob = parse(bc_dob, dayfirst=True)
    age_sep = relativedelta(today_raw, dob)
    return age_sep.years


def get_invoice_number():
    s = 'd:\\JOHN TILLET\\episode_data\\jtdata\\invoice_store.py'
    with open(s, 'r+b') as handle:
        invoice = pickle.load(handle)
        invoice += 1
        handle.seek(0)
        pickle.dump(invoice, handle)
        handle.truncate()
    return invoice


def get_time_code(op_time):
    time_base = '230'
    time_last = '10'
    second_last_digit = 1 + op_time // 15
    remainder = op_time % 15
    if remainder < 6:
        last_digit = 1
    elif remainder < 11:
        last_digit = 2
    else:
        last_digit = 3
    if op_time > 15:
        time_last = '{}{}'.format(second_last_digit, last_digit)
    time_code = time_base + time_last
    return time_code


def bill_process(bc_dob, upper, lower, asa, mcn, insur_code, op_time,
                 print_name, address, ref, full_fund,
                 fund_number, endoscopist, anaesthetist):
    """Turn raw data into stuff ready to go into my account.

    Generates and stores an incremented invoice number.
    First returned tuple is for csv, second is for database
    """
    now = datetime.datetime.now()
    today_for_invoice = now.strftime('%d' + '-' + '%m' + '-' + '%Y')
    age_diff = get_age_difference(bc_dob)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = 'No'
    asa_code = seventy_code = ''

    if upper:
        upper_done = 'Yes'
    if lower:
        lower_done = 'Yes'
    if asa[-2] == '3':
        asa_three = 'Yes'
        asa_code = '25000'
    if asa[-2] == '4':
        asa_three = 'Yes'
        asa_code = '25005'
    if age_diff >= 70:
        age_seventy = 'Yes'
        seventy_code = '25015'
    if insur_code == 'os':  # get rid of mcn in reciprocal mc patients
        mcn = ''

    if upper:
        first_code = '20740'
    else:
        first_code = '20810'
    if upper and lower:
        second_code = '20810'
    else:
        second_code = ''

    time_code = get_time_code(op_time)
    
    if anaesthetist == 'Dr J Tillett':
        invoice = get_invoice_number()
    else:
        invoice = 'na'
    # db has direct aneasthetic codes under first and second
    # now used for anaesthetic day reports
    Anaes_ep = namedtuple(
        'Anaes_ep', 'today_for_invoice, print_name, address, bc_dob,'
        'mcn, ref, full_fund, fund_number, insur_code, endoscopist, anaesthetist,'
        'first_code, second_code, seventy_code, asa_code, time_code, invoice')

    anaesthetic_data = Anaes_ep(
        today_for_invoice, print_name, address, bc_dob, mcn, ref,
        full_fund, fund_number, insur_code, endoscopist, anaesthetist,
        first_code, second_code, seventy_code, asa_code, time_code, invoice)

    anaesthetic_data_dict = anaesthetic_data._asdict()  # for dataset

    # csv has fields with yes and no under upper_done etc
    # for my account printing program
    Aneas_ep_csv = namedtuple(
        'Aneas_ep_csv', 'today_for_invoice, print_name, address, bc_dob, mcn,'
        'ref, full_fund, fund_number, insur_code, endoscopist, upper_done,'
        'lower_done, age_seventy, asa_three, time_code, invoice')

    ae_csv = Aneas_ep_csv(
        today_for_invoice, print_name, address, bc_dob, mcn, ref,
        full_fund, fund_number, insur_code, endoscopist, upper_done,
        lower_done, age_seventy, asa_three, time_code, invoice)

    return ae_csv, anaesthetic_data_dict


def to_anaesthetic_database(an_ep_dict):
    """Write anaethetic episode to sqlite using dataset"""
    db_file = 'sqlite:///d:\\JOHN TILLET\\episode_data\\aneasthetics.db'
    db = dataset.connect(db_file)
    table = db['episodes']
    table.insert(an_ep_dict)


def to_csv(episode_data):
    """Write tuple of billing data to csv."""
    csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\patients.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)


def get_anaesthetic_eps_today(anaes):
    """Retrive a dict of all anaesthetics today by anaesthetist logged in"""
    now = datetime.datetime.now()
    today = now.strftime('%d' + '-' + '%m' + '-' + '%Y')
    db_file = 'sqlite:///d:\\JOHN TILLET\\episode_data\\aneasthetics.db'
    db = dataset.connect(db_file)
    table = db['episodes']
    results = table.find(today_for_invoice=today, anaesthetist=anaes, order_by=['endoscopist', 'id'])
    return results, today


def print_anaesthetic_report(results, today, anaesthetist):
    """Write & print a txt file of anaesthetics today by anaesthetist"""
    out_string = 'Patients for Dr {}   {}\n\n\n'.format(
        anaesthetist.split()[-1], today)
    endoscopist = ''
    for row in results:
        if endoscopist != row['endoscopist']:
            endoscopist = row['endoscopist']
            out_string += '{}:\n'.format(endoscopist)
        patient_string = '{} {} {} {} {} {}\n'.format(
            row['print_name'], row['first_code'], row['second_code'],
            row['seventy_code'], row['asa_code'], row['time_code'])
        out_string += patient_string
    s = 'd:\\JOHN TILLET\\episode_data\\anaesthetic_report.txt'
    with open(s, 'w') as f:
        f.write(out_string)
    os.startfile(s, 'print')

def test_print_anaesthetic_report(results, today, anaesthetist):
    """Write & print a txt file of anaesthetics today by anaesthetist"""
    out_string = 'Patients for Dr {}   {}\n\n\n'.format(
        anaesthetist.split()[-1], today)
    short_results = []
    number = 0
    for row in results:
        di = {'n':row['print_name'],'f': row['first_code'],
              's':row['second_code'], '70':row['seventy_code'],
              'a':row['asa_code'], 't':row['time_code']}
        short_results.append(di)
        number += 1
    patient_string = tabulate(short_results)
    bottom_string = '\n\nTotal number of patients {}'.format(number)
    out_string += patient_string
    out_string += bottom_string
    s = 'd:\\JOHN TILLET\\episode_data\\anaesthetic_report.txt'
    with open(s, 'w') as f:
        f.write(out_string)
    os.startfile(s, 'print')


def make_episode_string(outtime, room, endoscopist, anaesthetist, print_name,
                        consult, upper, colon, message):
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

    html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>\
            <td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>\n"
    ep_string = html.format(
        outtime, room, docs, print_name, consult, upper, colon, message)
    return ep_string


def make_webpage(ep_string):
    today = datetime.datetime.now()
    today_str = today.strftime('%A' + '  ' + '%d' + ':' + '%m' + ':' + '%Y')

    head_string = '<html><body><H4>DEC procedures for {}</H4>\
    <table cellspacing="10"><tr><th>Time</th><th>Room</th>\
    <th>Doctors</th><th>Patient</th><th>Consult</th><th>Upper</th>\
    <th>Lower</th><th>Message</th></tr>\n'.format(today_str)
    base_string = "</table></body></html>"

    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.html'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\' + date_filename)

    if os.path.isfile(today_path):
        with open(today_path, 'r') as original:
            original.readline()
            new_base_string = original.read()
        with open(today_path, 'w') as modified:
            modified.write(head_string + ep_string + new_base_string)
    else:
        base = 'd:\\JOHN TILLET\\episode_data\\'
        dest = 'd:\\JOHN TILLET\\episode_data\\html-backup'
        for src in glob.glob(base + '*.html'):
            shutil.move(src, dest)
        with open(today_path, 'w') as new_index:
            new_index.write(head_string + ep_string + base_string)
    return today_path


def offsite(stored_index):
    session = ftplib.FTP('www.home.aone.net.au',
                         'ca121480@a1.com.au',
                         'Andromeda1957gd5mbunm')
    session.cwd('./dec/')
    with open(stored_index, 'rb') as file_handle:
        session.storlines('STOR today.html', file_handle)
    session.quit()


def login_and_run(room):
    colorama.init(autoreset=True)
    while True:
        print('\033[2J')  # clear screen
        print(LOGIN_STRING)
        anaesthetist = get_anaesthetist()

        print ('\nWelcome Dr {}!\n'.format(
            anaesthetist.split()[-1]))

        if anaesthetist in nc.REGULAR_ANAESTHETISTS:
            input("""Please let Kate know if you
have any upcoming change in your roster.
Press enter to continue""")
        endoscopist, consultant = get_endoscopist()

        nurse = get_nurse()

        while True:
            print('\033[2J')  # clear screen
            print("""Current team is:
            
            Endoscopist: {1}
            Anaesthetist: {0}
            Nurse: {2}""".format(anaesthetist, endoscopist, nurse))
            print()
            
            while True:
                print(CHOICE_STRING)
                choice = input()
                if choice in {'', 'ar', 'q', 'c', 'r', 'm', 'a', 'u'}:
                    break
            if choice == '':
                bill(anaesthetist, endoscopist, consultant, nurse, room)
            if choice == 'q':
                print('Thanks. Bye!')
                time.sleep(2)
                sys.exit(0)
            if choice == 'c':
                break
            if choice == 'r':
                data_entry = inputer(consultant, 'locum')
                episode_update(room, endoscopist, anaesthetist, data_entry)
            if choice == 'm':
                message_string = make_message_string(anaesthetist)
                webpage = make_webpage(message_string)
                offsite(webpage)
            if choice == 'ar':
                results, today = get_anaesthetic_eps_today(anaesthetist)
                test_print_anaesthetic_report(results, today, anaesthetist)
            if choice == 'a':
                analysis()
            if choice == 'u':
                update_web()


if __name__ == '__main__':
    login_and_run('R2')
