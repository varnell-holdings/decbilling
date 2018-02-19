# -*- coding: utf-8 -*-
from collections import namedtuple, OrderedDict
import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import glob
import logging
import os
import os.path
import pickle
import pprint
import shutil
import sys
import time
import webbrowser

import colorama
import dataset
import pyautogui as pya
import pyperclip
from tabulate import tabulate

from inputbill import (inputer, LoopException, clear)
import names_and_codes as nc

pya.PAUSE = 0.2
pya.FAILSAFE = False


class EpFullException(Exception):
    pass


def get_anaesthetist():
    while True:
        clear()
        initials = input('Anaesthetist initials:  ').lower()
        if initials in nc.ANAESTHETISTS:
            anaesthetist = nc.ANAESTHETISTS[initials]
            break
        else:
            print('\033[31;1m' + 'help')
            ans = input(
                'Type h for a list of initials or Enter to try again: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.ANAESTHETISTS)
                print()
                input('Hit Enter to try again: ')
    clear()
    print ('Welcome Dr {}.'.format(
        anaesthetist.split()[-1]))
    time.sleep(1)
    return anaesthetist


def get_endoscopist():
    while True:
        clear()
        initials = input('Endoscopist initials:  ').lower()
        if initials in nc.DOC_DIC:
            clear()
            print(nc.DOC_DIC[initials])
            time.sleep(0.7)
            endoscopist = nc.DOC_DIC[initials]
            break
        else:
            print('\033[31;1m' + 'help')
            ans = input(
                'Type h for a list of initials or Enter to try again: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.DOC_DIC)
                print()
                input('Hit Enter to try again: ')

    if endoscopist in nc.LOCUMS:  # inputer depends on doctor not locum
        while True:
            clear()
            initials = input('Who is Dr {} covering? '.format(
                endoscopist.split()[-1])).lower()
            if initials in nc.DOC_DIC:
                clear()
                print(nc.DOC_DIC[initials])
                time.sleep(0.7)
                consultant = nc.DOC_DIC[initials]
                break
            else:
                print('\033[31;1m' + 'help')
                ans = input('Type h for  initials or Enter to try again: ')
                if ans == 'h':
                    clear()
                    pprint.pprint(nc.DOC_DIC)
                    print()
                    input('Hit Enter to try again: ')
    else:
        consultant = endoscopist
    return endoscopist, consultant


def get_nurse():
    while True:
        clear()
        initials = input('Nurse initials:  ').lower()
        if initials in nc.NURSES_DIC:
            clear()
            print(nc.NURSES_DIC[initials])
            time.sleep(0.7)
            nurse = nc.NURSES_DIC[initials]
            break
        else:
            print('\033[31;1m' + 'help')
            ans = input('Type h for  initials or Enter to try again')
            if ans == 'h':
                clear()
                pprint.pprint(nc.NURSES_DIC)
                print()
                input('Hit Enter to try again: ')
    return nurse


def bill(anaesthetist, endoscopist, consultant, nurse, room):
    """Workhorse function"""
    try:
        data_entry = inputer(endoscopist, consultant, anaesthetist)

        (asa, upper, colon, banding, consult, message, op_time, insur_code,
         fund, ref, fund_number,
         clips, varix_flag, varix_lot, in_theatre, out_theatre) = data_entry

        if anaesthetist == 'Dr J Tillett' and asa is not None:
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref)
        else:
            mcn = ref = fund = fund_number = ''

        message = episode_open(message)
        mrn, name, address, postcode, dob = episode_scrape()
        gp = episode_gp()
        episode_discharge(in_theatre, out_theatre, anaesthetist, endoscopist)
        episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot, room)
        episode_procedures(upper, colon, banding, asa)
        episode_close()

        if asa is not None:
            ae_csv, ae_db_dict, message = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                name, address, ref, fund, fund_number, endoscopist,
                anaesthetist, message)
            to_anaesthetic_database(ae_db_dict)

        if asa is not None and anaesthetist == 'Dr J Tillett':
            to_csv(ae_csv)

        episode_string = make_episode_string(
            out_theatre, room, endoscopist, anaesthetist, name, consult,
            upper, colon, message)

        make_webpage(episode_string)
        medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
                            upper, colon, banding, postcode, dob, gp)
        close_out(anaesthetist)

    except (LoopException, EpFullException):
        raise


def episode_get_mcn_and_ref():
    # get mcn
    mcn = pyperclip.copy('na')
    pya.moveTo(424, 474, duration=0.1)
    pya.dragTo(346, 474, duration=0.1)
    pya.moveTo(424, 474, duration=0.1)
    pya.click(button='right')
    pya.moveTo(477, 542, duration=0.1)
    pya.click()
    mcn = pyperclip.paste()
    mcn = mcn.replace(' ', '')
    # get ref
    ref = pyperclip.copy('na')
    pya.moveTo(500, 475, duration=0.1)
    pya.dragRel(-8, 0, duration=0.1)
    pya.moveRel(8, 0, duration=0.1)
    pya.click(button='right')
    pya.moveTo(542, 536, duration=0.1)
    pya.click()
    ref = pyperclip.paste()
    return mcn, ref


def episode_get_fund_name():
    # get fund name
    fund = pyperclip.copy('na')
    pya.moveTo(696, 508, duration=0.1)
    pya.dragTo(543, 508, duration=0.1)
    pya.moveTo(696, 508, duration=0.1)
    pya.click(button='right')
    pya.moveTo(717, 579, duration=0.1)
    pya.click()
    fund = pyperclip.paste()
    if 'United' in fund:
        fund = 'Grand United Corporate Health'
    return fund


def episode_get_fund_number():
    # get fund number
    fund_number = pyperclip.copy('na')
    pya.moveTo(646, 545, duration=0.1)
    pya.dragTo(543, 545, duration=0.1)
    pya.moveTo(646, 545, duration=0.1)
    pya.click(button='right')
    pya.moveTo(692, 392, duration=0.1)
    pya.click()
    fund_number = pyperclip.paste()
    return fund_number


def episode_getfund(insur_code, fund, fund_number, ref):
    while True:
        if not pya.pixelMatchesColor(150, 630, (255, 0, 0)):
            print('Open the patient file.')
            input('Hit Enter when ready.')
        else:
            break
#    while True:
#        pic = 'd:\\John TILLET\\episode_data\\membership.png'
#        if pya.locateOnScreen(pic, region=(527, 512,100, 25)) is None:
#            print('Health Fund Membership summary is missing.')
#            input('Ask secretaries to fix. Then press Enter')
#        else:
#            break
    # get mcn
    if insur_code == 'ga':
        mcn = ''
    elif insur_code == 'os' and fund != 'Overseas':
        fund_number = episode_get_fund_number()
        fund = episode_get_fund_name()
        mcn = ref = ''
    elif insur_code in {'p', 'u'}:
        fund_number = ''
        mcn, ref = episode_get_mcn_and_ref()
    else:
        fund_number = episode_get_fund_number()
        mcn, ref = episode_get_mcn_and_ref()

    insur_details = (mcn, ref, fund, fund_number)
    csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\test_funds.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(insur_details)
    return insur_details


def episode_open(message):
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
        time.sleep(0.3)

    pya.typewrite(['down'] * 11, interval=0.1)
    pya.press('enter')
    pya.hotkey('alt', 'f')

    pic = 'd:\\John TILLET\\episode_data\\aileen.png'
    while pya.locateOnScreen(pic, region=(0, 45, 150, 40)) is not None:
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
    time.sleep(3)
    return message


def episode_discharge(intime, outtime, anaesthetist, endoscopist):
    pya.hotkey('alt', 'i')
    pya.typewrite(['enter'] * 4, interval=0.1)
    test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    test = pyperclip.paste()
    if test != 'empty':
        pya.alert(text='Data here already! Try Again', title='', button='OK')
        time.sleep(1)
        pya.hotkey('alt', 'f4')
        raise EpFullException('EpFullException raised')
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
    anal_flag = False
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
        anal_flag = True
    else:
        if asa:
            pya.typewrite(asa + '\n')
            pya.press('enter')
        return
    pya.typewrite(['tab'] * 2, interval=0.1)
    if anal and anal_flag is False:  # third line
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
    return


def episode_gp():
    pya.hotkey('alt', 'a')
    pya.typewrite(['tab'] * 4, interval=0.1)
    gp = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    gp = pyperclip.paste()
    return gp


def episode_theatre(endoscopist, nurse, clips, varix_flag, varix_lot, room):
    pya.hotkey('alt', 'n')
    pya.typewrite(['left'] * 2, interval=0.1)

    doc_coord = (100, 155)

    pya.moveTo(doc_coord)
    pya.click()
    pya.press('tab')
    doc_test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    doc_test = pyperclip.paste()
    if doc_test == 'Endoscopist':
        pya.press('tab')
        pya.typewrite(['enter'] * 2, interval=0.1)
        pya.moveRel(400, 0)
        pya.click()
        pya.typewrite(['tab'] * 2, interval=0.1)
        pya.typewrite(['enter'] * 2, interval=0.1)

    pya.moveTo(doc_coord)
    pya.click()
    pya.typewrite(endoscopist)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    pya.moveRel(400, 0)
    pya.click()
    pya.typewrite(nurse)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    if clips != 0 or varix_flag is True:
        pya.moveTo(100, 360)
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
    mrn = pyperclip.copy('')  # put '' on clipboard before each copy
    time.sleep(1)
    pya.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    if not mrn.isdigit() or mrn == 19299:
        pya.alert(text='Problem!! Try Again', title='', button='OK')
        time.sleep(1)
        pya.hotkey('alt', 'f4')
        raise EpFullException('EpFullException raised')
    pya.press('tab')
    title = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    title = pyperclip.paste()
    pya.press('tab')
    first_name = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    first_name = pyperclip.paste()
    pya.typewrite(['tab'] * 2, interval=0.1)
    last_name = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    last_name = pyperclip.paste()
    print_name = title + ' ' + first_name + ' ' + last_name
    pya.press('tab')
    street_number = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    street_number = pyperclip.paste()
    pya.press('tab')
    street_name = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    street_name = pyperclip.paste()
    pya.press('tab')
    suburb = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    suburb = pyperclip.paste()
    suburb = suburb.lower()
    suburb = suburb.title()
    pya.press('tab')
    postcode = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    postcode = pyperclip.paste()
    address = street_number + ' ' + street_name + ' ' + suburb + ' ' + postcode
    pya.press('tab')
    dob = pyperclip.copy('')
    pya.hotkey('ctrl', 'c')
    dob = pyperclip.paste()
    return (mrn, print_name, address, postcode, dob)


def episode_close():
    pya.hotkey('alt', 'f4')


def get_age_difference(dob):
    today_raw = datetime.datetime.today()
    dob = parse(dob, dayfirst=True)
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


def bill_process(dob, upper, lower, asa, mcn, insur_code, op_time,
                 patient, address, ref, fund,
                 fund_number, endoscopist, anaesthetist, message):
    """Turn raw data into stuff ready to go into my account.

    Generates and stores an incremented invoice number.
    First returned tuple is for csv, second is for database
    """
    now = datetime.datetime.now()
    today_for_invoice = now.strftime('%d' + '-' + '%m' + '-' + '%Y')
    age_diff = get_age_difference(dob)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = 'No'
    upper_code = lower_code = asa_code = seventy_code = ''

    if upper:
        upper_done = 'Yes'  # this goes to jrt csv file
        upper_code = '20740'  # this goes to anaesthetic database
    if lower:
        lower_done = 'Yes'
        lower_code = '20810'
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
    if insur_code == 'u' or insur_code == 'p':
        insur_code = 'bb'
        message += ' JT will bulk bill'
    # if insur_code == 'os' and fund != 'Overseas':  # os - in fund
    #     message += ' JT will bill {}.'.format(fund)

    time_code = get_time_code(op_time)

    if anaesthetist == 'Dr J Tillett':
        invoice = get_invoice_number()
    else:
        invoice = ''
    # db has direct aneasthetic codes under first and second
    # now used for anaesthetic day reports
    Anaes_ep = namedtuple(
        'Anaes_ep', 'today_for_invoice, patient, address, dob,'
        'mcn, ref, fund, fund_number, insur_code, endoscopist,'
        'anaesthetist, upper_code, lower_code, seventy_code,'
        'asa_code, time_code, invoice')

    anaesthetic_data = Anaes_ep(
        today_for_invoice, patient, address, dob, mcn, ref,
        fund, fund_number, insur_code, endoscopist, anaesthetist,
        upper_code, lower_code, seventy_code, asa_code, time_code, invoice)

    anaesthetic_data_dict = anaesthetic_data._asdict()  # for dataset

    # csv has fields with yes and no under upper_done etc
    # for my account printing program
    Aneas_ep_csv = namedtuple(
        'Aneas_ep_csv', 'today_for_invoice, patient, address, dob, mcn,'
        'ref, fund, fund_number, insur_code, endoscopist, upper_done,'
        'lower_done, age_seventy, asa_three, time_code, invoice')

    ae_csv = Aneas_ep_csv(
        today_for_invoice, patient, address, dob, mcn, ref,
        fund, fund_number, insur_code, endoscopist, upper_done,
        lower_done, age_seventy, asa_three, time_code, invoice)

    return ae_csv, anaesthetic_data_dict, message


def to_anaesthetic_database(an_ep_dict):
    """Write anaethetic episode to sqlite using dataset"""
    db_file = 'sqlite:///d:\\JOHN TILLET\\episode_data\\aneasthetics.db'
    db = dataset.connect(db_file)
    table = db['episodes']
    table.insert(an_ep_dict)


def to_csv(episode_data):
    """Write tuple of jrt's billing data to csv."""
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
    results = table.find(today_for_invoice=today,
                         anaesthetist=anaes,
                         order_by=['id'])
    return results, today


def make_anaesthetic_report(results, today, anaesthetist):
    """Write & print a txt file of anaesthetics today by anaesthetist"""
    out_string = 'Patients for Dr {}   {}\n\n\n'.format(
        anaesthetist.split()[-1], today)
    results_list = []
    number = 0
    for row in results:
        # tabulate seems to expect list of dicts
        d = [('n', row['patient']), ('add', row['address']),
             ('dob', row['dob']),
             ('end', row['endoscopist']), ('f', row['upper_code']),
             ('s', row['lower_code']), ('70', row['seventy_code']),
             ('a', row['asa_code']), ('t', row['time_code']),
             ('mcn', row['mcn']),
             ('ref', row['ref']), ('fund', row['fund']),
             ('fund_number', row['fund_number'])]
        d = OrderedDict(d)
        results_list.append(d)
        number += 1
    patient_string = tabulate(results_list, tablefmt='html')
    bottom_string = '\n\nTotal number of patients {}'.format(number)
    out_string += patient_string
    out_string += bottom_string
    s = 'd:\\Nobue\\anaesthetic_report.html'
    with open(s, 'w') as f:
        f.write(out_string)
    return s


def make_simple_anaesthetic_report(results, today, anaesthetist):
    """Write & print a txt file of anaesthetics today by anaesthetist"""
    out_string = 'Patients for Dr {}   {}\n\n\n'.format(
        anaesthetist.split()[-1], today)
    results_list = []
    number = 0
    for row in results:
        # tabulate seems to expect list of dicts
        d = [('n', row['patient']), ('f', row['upper_code']),
             ('s', row['lower_code']), ('70', row['seventy_code']),
             ('a', row['asa_code']), ('t', row['time_code'])]
        d = OrderedDict(d)
        results_list.append(d)
        number += 1
    patient_string = tabulate(results_list, tablefmt='html')
    bottom_string = '\n\nTotal number of patients {}'.format(number)
    out_string += patient_string
    out_string += bottom_string
    s = 'd:\\Nobue\\simple_anaesthetic_report.html'
    with open(s, 'w') as f:
        f.write(out_string)
    return s


def view_log():
    os.startfile('d:\\JOHN TILLET\\episode_data\\doc_error.txt')


def open_calendar():
    webbrowser.open('d:\\Nobue\\anaesthetic_roster.html')


def make_episode_string(outtime, room, endoscopist, anaesthetist, patient,
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
        outtime, room, docs, patient, consult, upper, colon, message)
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
    nob_today = 'd:\\Nobue\\today.html'
    shutil.copyfile(today_path, nob_today)


def medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
                        upper, lower, anal, postcode, dob, gp):
    today = datetime.datetime.now()
    today = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    episode_data = (today, endoscopist, consultant, anaesthetist, nurse,
                    upper, lower, anal, postcode, dob, gp)
    csvfile = 'D:\\JOHN TILLET\\episode_data\\medical_data.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)


def close_out(anaesthetist):
        time.sleep(1)
        pya.moveTo(x=780, y=90)
        pya.click()
        time.sleep(1)
        pya.hotkey('alt', 'n')
        pya.moveTo(x=780, y=110)
        if anaesthetist == 'Dr J Tillett':
            results, today = get_anaesthetic_eps_today(anaesthetist)
            s = make_anaesthetic_report(results, today, anaesthetist)
            os.startfile(s)


def update_html():
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.html'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\' + date_filename)
    nob_today = 'd:\\Nobue\\today.html'
    shutil.copyfile(today_path, nob_today)


# currently not used
def open_file(mrn):
    pya.click(100, 100)
    pya.hotkey('alt', 'f')
    time.sleep(1)
    pya.press('enter')
    time.sleep(1)
    pya.typewrite(['tab'] * 2)
    pya.press('down')
    pya.hotkey('shift', 'tab')
    pya.hotkey('shift', 'tab')
    pya.typewrite(mrn)
    pya.press('enter')


def make_message_string(anaesthetist):
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left
    print('Type your message. Your name is automatically included.')
    message = input('Message: ')
    html = "<tr><td></td><td></td><td>Message from</td><td>{0}</td>\
            <td></td><td></td><td></td><td>{1}</td></tr>\n"
    message_string = html.format(anaesthetist, message)
    return message_string


def episode_update(room, endoscopist, anaesthetist, data_entry):
    # data_enry is a tuple -> unpack it
    (asa, upper, colon, banding, consult, message, op_time,
     insur_code, fund, ref, fund_number, clips, varix_flag,
     varix_lot, in_formatted, out_formatted) = data_entry

    message = episode_open(message)
    episode_procedures(upper, colon, banding, asa)
    mrn, print_name, address, dob, mcn = episode_scrape()

    message += ' Updated this patient. Check Blue Chip is correct.'

    out_string = make_episode_string(
        out_formatted, room, endoscopist, anaesthetist, print_name,
        consult, upper, colon, message)
    make_webpage(out_string)
    close_out(anaesthetist)


def open_today():
    nob_today = 'd:\\Nobue\\today.html'
    webbrowser.open(nob_today)


def open_intranet():
    intranet = 'https://intranet.stvincents.com.au'
    webbrowser.open(intranet)


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
    first_date = datetime.datetime(2018, 1, 1)
    today = datetime.datetime.today()
    days_diff = (today - first_date).days
    desired_weekly = 60
    first_invoice = 6848
    invoice_diff = last_invoice - first_invoice
    desired_number = int(days_diff * desired_weekly / 7)
    excess = invoice_diff - desired_number
    print('{} excess to average {} per week.'.format(excess, desired_weekly))
    input('Hit Enter to continue.')


def login_and_run(room):
    colorama.init(autoreset=True)
    logging.basicConfig(
        filename='d:\\JOHN TILLET\\episode_data\\doc_error.txt',
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger = logging.getLogger(__name__)
    while True:
        anaesthetist = get_anaesthetist()

        endoscopist, consultant = get_endoscopist()

        nurse = get_nurse()

        while True:
            clear()
            print("""Current team is:

            Endoscopist: {1}
            Anaesthetist: {0}
            Nurse: {2}""".format(anaesthetist, endoscopist, nurse))
            print()
            print(nc.CHOICE_STRING)
            choice = input().lower()
            if choice not in {
                    '', 'ar', 'par', 'end', 'h', 'c', 'r',
                    'm', 'a', 'u', 'cal', 'w', 'l', 'i'}:
                continue
            try:
                if choice == '':
                    try:
                        while True:
                            bill(
                                anaesthetist, endoscopist,
                                consultant, nurse, room)

                    except LoopException:
                        continue
                    except EpFullException:
                        clear()
                        logger.error('Episode full exception.')
                        print(nc.FILLED_TEXT)
                        input('Press any key to continue: ')
                        continue
                if choice == 'end':
                    print('Thanks. Bye!')
                    time.sleep(2)
                    sys.exit(0)
                if choice == 'h':
                    clear()
                    print(nc.USER_GUIDE)
                    input('Hit any key to continue:')
                if choice == 'c':
                    break
                if choice == 'r':
                    try:
                        data_entry = inputer(endoscopist, consultant, 'locum')
                    except LoopException:
                        continue
                    episode_update(room, endoscopist, anaesthetist, data_entry)
                if choice == 'm':
                    message_string = make_message_string(anaesthetist)
                    make_webpage(message_string)
                if choice == 'ar':
                    results, today = get_anaesthetic_eps_today(anaesthetist)
                    s = make_simple_anaesthetic_report(
                        results, today, anaesthetist)
                    os.startfile(s)
                if choice == 'par':
                    results, today = get_anaesthetic_eps_today(anaesthetist)
                    s = make_simple_anaesthetic_report(
                        results, today, anaesthetist)
                    os.startfile(s, 'print')
                if choice == 'cal':
                    open_calendar()
                if choice == 'w':
                    open_today()
                if choice == 'i':
                    open_intranet()
                if choice == 'l':
                    view_log()
                if choice == 'a':
                    analysis()
                if choice == 'u':
                    update_html()
            except Exception as err:
                logger.error(err)
                sys.exit(1)


if __name__ == '__main__':
    login_and_run('R2')
