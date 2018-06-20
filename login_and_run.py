# -*- coding: utf-8 -*-
from collections import namedtuple,  deque
import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from jinja2 import Environment, FileSystemLoader
import logging
import os
import os.path
import pickle
import pprint
import sys
import time
import webbrowser

import colorama
import pyautogui as pya
import pyperclip

from inputbill import (inputer, LoopException)
import names_and_codes as nc
import decbatches

pya.PAUSE = 0.2
pya.FAILSAFE = True

today = datetime.datetime.now()

class EpFullException(Exception):
    pass


def clear():
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left


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


def bill(anaesthetist, endoscopist, consultant, nurse):
    """Workhorse function"""
    try:
        data_entry = inputer(endoscopist, consultant, anaesthetist)
#       unpack data_entry
        (asa, upper, colon, banding, consult, message, op_time, insur_code,
         fund, ref, fund_number,
         clips, varix_lot, in_theatre, out_theatre, band3) = data_entry

#        scrape fund details if billing anaesthetist
        if anaesthetist in nc.BILLING_ANAESTHETISTS and asa is not None:
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref)
        else:
            mcn = ref = fund = fund_number = ''
            

#        open day surgery and do some scrraping and pasting
        message = episode_open(message)
        mrn, name, address, postcode, dob = episode_scrape()
        gp = episode_gp()
        endoscopist = episode_discharge(
                in_theatre, out_theatre, anaesthetist, endoscopist)
        
#        anaesthetic billing
        if asa is not None and anaesthetist in nc.BILLING_ANAESTHETISTS:
            anaesthetic_tuple, message = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                name, address, ref, fund, fund_number, endoscopist,
                anaesthetist, message)
            to_anaesthetic_csv(anaesthetic_tuple, anaesthetist)
            render_anaesthetic_report(anaesthetist)
     
#        web page with jinja2
        message = message_parse(message)  # break message into lines
        today_path = episode_to_csv(
                out_theatre, endoscopist, anaesthetist, name,consult,
                upper, colon, message)
        make_web_secretary(today_path)
#        data collection into csv - not essential
        medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
                            upper, colon, banding, postcode, dob, gp)

#        finish data pasting into day surgery and exit
        episode_procedures(upper, colon, banding, asa)
        episode_theatre(endoscopist, nurse, clips, varix_lot)
        if band3:
            episode_claim()
        pya.click()
        episode_close()
        time.sleep(2)
        close_out(anaesthetist)

    except (LoopException, EpFullException):
        raise


def episode_get_mcn_and_ref():
    # get mcn
    mcn = pyperclip.copy('na')
    pya.moveTo(424, 474, duration=0.1)
    pya.dragTo(346, 474, duration=0.1)
    pya.hotkey('ctrl', 'c')
    mcn = pyperclip.paste()
    pya.moveTo(424, 474, duration=0.1)
    pya.click(button='right')
    pya.moveTo(481, 268, duration=0.1)
    pya.click()
    
    mcn = pyperclip.paste()
    mcn = mcn.replace(' ', '')
    # get ref
    ref = pyperclip.copy('na')
    pya.moveTo(500, 475, duration=0.1)
    pya.dragRel(-8, 0, duration=0.1)
    pya.hotkey('ctrl', 'c')
    ref = pyperclip.paste()
    pya.moveRel(8, 0, duration=0.1)
    pya.click(button='right')
    pya.moveTo(577, 274, duration=0.1)
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
    if fund == 'na':
        fund = pya.prompt(
            text='Please enter Fund name', title='Fund Name', default='')
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
    if fund_number == 'na':
        fund_number = pya.prompt(
            text='Please enter fund number!', title='Fund Number', default='')
    return fund_number


def episode_getfund(insur_code, fund, fund_number, ref):
#    ref may contain garrison episode id
    while True:
        if not pya.pixelMatchesColor(150, 630, (255, 0, 0)):
            print('Open the patient file.')
            input('Hit Enter when ready.')
        else:
            break
    # get mcn
    if insur_code == 'ga':
        mcn = ''
    elif insur_code == 'os' and fund != 'Overseas':
        fund_number = episode_get_fund_number()
        fund = episode_get_fund_name()
        mcn = ref = ''
    elif insur_code == 'os' and fund == 'Overseas':
        mcn = ref = ''
    elif insur_code in {'p', 'u', 'v'}:
        fund_number = ''
        mcn, ref = episode_get_mcn_and_ref()
    else:
        fund_number = episode_get_fund_number()
        mcn, ref = episode_get_mcn_and_ref()

    return (mcn, ref, fund, fund_number)


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
    time.sleep(2)
    pic = 'd:\\John TILLET\\source\\active\\billing\\aileen.png'
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
            message += ' New episode made.'
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

    test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    doctor = pyperclip.paste()

    endoscopist_surname = endoscopist.split()[-1].lower()

    doctor_surname = doctor.split()[-1].lower()

    if endoscopist_surname != doctor_surname:
        response = pya.confirm(
            text='You are logged in with {} but the secretaries have entered'
                 ' {}. Choose the correct one'.format(endoscopist, doctor),
            title='Confirm Endoscopist',
            buttons=['{}'.format(doctor), '{}'.format(endoscopist)])

        pya.typewrite(response)
        endoscopist = response
    return endoscopist


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


def episode_claim():
    pya.hotkey('alt', 's')
    pya.typewrite(['left'] * 2, interval=0.1)
    for i in range(7):
        pya.hotkey('shift', 'tab')
    pya.press('3')


def episode_theatre(endoscopist, nurse, clips, varix_lot):
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
    if clips != 0 or varix_lot:
        pya.moveTo(100, 360)
        pya.click()
        if varix_lot:
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


# Utility fucntions for bill processing

def get_age_difference(dob):
    dob = parse(dob, dayfirst=True)
    age_sep = relativedelta(today, dob)
    return age_sep.years


def get_invoice_number():
    s = 'd:\\JOHN TILLET\\episode_data\\invoice_store.py'
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
    """Turn raw data into stuff ready to go into anaesthetic csv file

    Generates and stores an incremented invoice number.
    Returns a namedtuple
    """
    today_for_invoice = today.strftime('%d' + '-' + '%m' + '-' + '%Y')
    age_diff = get_age_difference(dob)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = 'No'

    if upper:
        upper_done = 'upper_Yes'  # this goes to jrt csv file
    else:
        upper_done = 'upper_No'
    if lower:
        lower_done = 'lower_Yes'
    else:
        lower_done = 'lower_No'
    if asa[-2] == '3':
        asa_three = 'asa3_Yes'
    elif asa[-2] == '4':
        asa_three = 'asa3_Four'
    elif asa[-2] in {'1', '2'}:
        asa_three = 'asa3_No'
    if age_diff >= 70:
        age_seventy = 'age70_Yes'
    else:
        age_seventy = 'age70_No'
    if insur_code == 'os':  # get rid of mcn in reciprocal mc patients
        mcn = ''
    jt = anaesthetist == 'Dr J Tillett'
    if insur_code == 'u' or insur_code == 'p' and jt:
        insur_code = 'bb'
        message += ' JT will bulk bill.'

    time_code = get_time_code(op_time)

    invoice = get_invoice_number()
    invoice = 'DEC' + str(invoice)

    Aneas_ep_csv = namedtuple(
        'Aneas_ep_csv', 'today_for_invoice, patient, address, dob, mcn,'
        'ref, fund, fund_number, insur_code, endoscopist, upper_done,'
        'lower_done, age_seventy, asa_three, time_code, invoice')

    ae_csv = Aneas_ep_csv(
        today_for_invoice, patient, address, dob, mcn, ref,
        fund, fund_number, insur_code, endoscopist, upper_done,
        lower_done, age_seventy, asa_three, time_code, invoice)

    return ae_csv, message


def message_parse(message):
    """Put breaks into message string."""
    message = message.rstrip('.')
    message = message.replace('.', '<br>')
    return message


def to_anaesthetic_csv(episode_data, anaesthetist):
    """Write tuple of anaesthetic billing data to csv
    for billing anaesthetists"""
    surname = anaesthetist.split()[-1]
    csvfile = 'd:\\JOHN TILLET\\episode_data\\{}.csv'.format(surname)
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)


def episode_to_csv(outtime, endoscopist, anaesthetist, patient,
                   consult, upper, colon, message):
    """Write episode data to csv for web page generation."""
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
    episode_data = (outtime, docs, patient,
                    consult, upper, colon, message)
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    with open(today_path, 'a') as handle:
        datawriter = csv.writer(
            handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)

    return today_path


def make_web_secretary(today_path):
    """Render jinja2 template and write to file."""
    today_str = today.strftime(
        '%A' + '  ' + '%d' + '-' + '%m' + '-' + '%Y')
    today_data = deque()
    with open(today_path) as data:
        reader = csv.reader(data)
        for ep in reader:
            today_data.appendleft(ep)
    path_to_template = 'D:\\JOHN TILLET\\episode_data\\today_sec_template.html'
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = 'today_sec_template.html'
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open('d:\\Nobue\\today_new.html', 'w') as f:
        f.write(a)
    file_date = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    file_str = 'D:\\JOHN TILLET\\episode_data\\html-backup\\' + file_date + '.html'
    with open(file_str, 'w') as f:
        f.write(a)


def medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
                        upper, lower, anal, postcode, dob, gp):
    """Drop episode info into csv file for statistics."""
    today_date = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    episode_data = (today_date, endoscopist, consultant, anaesthetist, nurse,
                    upper, lower, anal, postcode, dob, gp)
    csvfile = 'D:\\JOHN TILLET\\episode_data\\medical_data.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)
 
def render_anaesthetic_report(anaesthetist):
    anaes_surname = anaesthetist.split()[-1]
    today_data = []
    count = 0
    today_date = today.strftime('%d' + '-' + '%m' + '-' + '%Y')
    csvfile = 'd:\\JOHN TILLET\\episode_data\\{}.csv'.format(anaes_surname)
    with open(csvfile) as handle:
        reader = csv.reader(handle)
        for episode in reader:
            if episode[0] == today_date:
                count += 1
                today_data.append(episode)
    path_to_template = 'D:\\JOHN TILLET\\episode_data\\today_anaesthetic_template.html'
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = 'today_anaesthetic_template.html'
    template = env.get_template(template_name)
    a = template.render(today_data=today_data,
                        today_date=today_date,
                        count=count,
                        anaes_surname = anaes_surname)
    with open('d:\\Nobue\\report_{}.html'.format(anaes_surname), 'w') as f:
        f.write(a)

    
def close_out(anaesthetist):
    """Close patient file with mouse click and display billing details
    if a billing anaesthetist."""
    time.sleep(1)
    pya.moveTo(x=780, y=90)
    pya.click()
    time.sleep(1)
    pya.hotkey('alt', 'n')
    pya.moveTo(x=780, y=110)
    if anaesthetist in nc.BILLING_ANAESTHETISTS:
        webbrowser.open(
                'd:\\Nobue\\report_{}.html'.format(anaesthetist.split()[-1]))
        

def jt_analysis():
    """Print whether on weekly target from first_date.
    Note need to set both first_date and first_date_lex
    """
    first_date = datetime.datetime(2018, 1, 1)
#    first_date_lex = '20180401'
    results = 74
    with open('d:\JOHN TILLET\episode_data\medical_data.csv') as h:
        reader = csv.reader(h)
        for ep in reader:
            if ep[0].split('-')[0] == '2018' and ep[3] == 'Dr J Tillett':
                results += 1
    a = today - first_date
    days_diff = a.days
    desired_weekly = 60
    desired_number = int(days_diff * desired_weekly / 7)
    excess = results - desired_number
    print('Number this year', results)
    print('{} excess to average {} per week.'.format(excess, desired_weekly))
    input('Hit Enter to continue.')



def login_and_run():
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
            if anaesthetist in nc.BILLING_ANAESTHETISTS:
                print(nc.CHOICE_STRING_BILLER)
            else:
                print(nc.CHOICE_STRING)
            choice = input().lower()
            if choice not in {
                    '', 'q', 'c', 's', 'a', 'u', 'r', 'w', 'p', 'm'}:
                continue
            try:
                if choice == '':
                    try:
                        while True:
                            bill(
                                anaesthetist, endoscopist,
                                consultant, nurse)
                    except LoopException:
                        continue
                    except EpFullException:
                        clear()
                        logger.error('Episode full exception.')
                        print(nc.FILLED_TEXT)
                        input('Press any key to continue: ')
                        continue
                if choice == 'q':
                    print('Thanks. Bye!')
                    time.sleep(2)
                    sys.exit(0)
                if choice == 'c':
                    break
                if choice == 'p':
                    decbatches.main(anaesthetist)
                if choice == 'r':
                    webbrowser.open('d:\\Nobue\\anaesthetic_roster.html')
                if choice == 'w':
                    webbrowser.open('d:\\Nobue\\today_new.html')
                if choice == 's':
                    os.startfile(
                            'D:\\JOHN TILLET\\source\\active\\billing\\spyder.cmd')
                if choice == 'a':
                    jt_analysis()
                if choice == 'u':
                     date_file_str = today.strftime(
                             '%Y' + '-' + '%m' + '-' + '%d')
                     date_filename = date_file_str + '.csv'
                     today_path = os.path.join(
                             'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
                     make_web_secretary(today_path)
                     render_anaesthetic_report(anaesthetist)
                if choice == 'm':
                    nowtime = datetime.datetime.now()
                    nowtime = nowtime.strftime('%H' + ':' + '%M')
                    message = input('Message: ')
                    today_path =  episode_to_csv(
                            nowtime, endoscopist, anaesthetist, '','', '', '', message)
                    make_web_secretary(today_path)
                    webbrowser.open('d:\\Nobue\\today_new.html')
                    
            except Exception as err:
                logger.error(err)
                sys.exit(1)

if __name__ == '__main__':
    login_and_run('R2')
