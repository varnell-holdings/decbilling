# -*- coding: utf-8 -*-
"""contains the following functions
log_input
bill_process
time_calculater
make_index
make_index_alt
episode_open
episode_dumper
episode_scrape
offsite
to_json
to_csv
to_database_room2
analysis
update_number_this_week
Created on Fri Nov 18 15:22:26 2016
@author: John
"""

import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import ftplib
import glob
import os
import os.path
import pickle
import shutil
import sys
import time
import webbrowser

import dataset
import pyautogui
import pyperclip

import names_and_codes as np

class BlueChipError(Exception):
        pass


def consult_check(consult, doctor, upper, lower):
    doc_test = doctor in {'Dr A Wettstein', 'Dr S Ghaly',
                          'Dr S Vivekanandarajah'} and consult == '0'
    path = upper in {'pb', 'pp'} or lower in {'cb', 'cp', 'sb', 'sp'}
    cv_test = (doctor == 'Dr C Vickers') and path and consult == '0'
    return doc_test or cv_test


def get_consult(doctor, upper, lower, loop_flag):
    while True:
        consult = input('Consult: ')
        if consult == '0':
            consult = 'none'
        if consult == 'q':
            loop_flag = True
            break
        if consult in {'110', '116', 'none'}:
            break
        print('TRY AGAIN!')

    if consult_check(consult, doctor, upper, lower) and loop_flag is False:
        print('Confirm with {} that he/she'
              ' does not want a consult'.format(doctor))
        while True:
            consult = input('Consult either 0,110,116: ')
            if consult == '0':
                consult = 'none'
            if consult in {'110', '116', 'none'}:
                break

    return consult, loop_flag


def bill_process(bc_dob, upper, lower, asa, mcn, insur_code):
    """
    Turn rawdata into stuff ready to go into my account.

    Generates and stores an incremented invoice number.
    """
    today_raw = datetime.datetime.today()
    today = today_raw.strftime('%d' + '//' + '%m' + '//' + '%Y')
    dob = parse(bc_dob, dayfirst=True)
    age_sep = relativedelta(today_raw, dob)
    if age_sep.years >= 70:
        age_seventy = 'Yes'
    else:
        age_seventy = 'No'
    if upper != '0':
        upper_done = 'Yes'
    else:
        upper_done = 'No'
    if lower != '0':
        lower_done = 'Yes'
    else:
        lower_done = 'No'
    if asa == '3' or asa == '4':
        asa_three = 'Yes'
    else:
        asa_three = 'No'
    if insur_code == 'os':
        mcn = ''
    with open('d:\\JOHN TILLET\\episode_data\\jtdata\\invoice_store.py', 'rb') as handle:
        invoice = pickle.load(handle)
        invoice += 1
    with open('d:\\JOHN TILLET\\episode_data\\jtdata\\invoice_store.py', 'wb') as handle:
        pickle.dump(invoice, handle)
    return today, upper_done, lower_done, age_seventy, asa_three, invoice, mcn


def time_calculater(time_in_theatre):
    nowtime = datetime.datetime.now()
    today_str = nowtime.strftime('%Y' + '-' + '%m' + '-'  + '%d')

    time_in_theatre = int(time_in_theatre)
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    time_base = '230'
    time_last = '10'
    second_last_digit = 1 + time_in_theatre // 15
    remainder = time_in_theatre % 15
    if remainder < 6:
        last_digit = 1
    elif remainder < 11:
        last_digit = 2
    else:
        last_digit = 3
    if time_in_theatre > 15:
        time_last = '%d%d' % (second_last_digit, last_digit)
    anaesthetic_time = time_base + time_last

    return (in_formatted, out_formatted, anaesthetic_time, today_str)


def make_index(out_formatted, doctor, print_name, consult,
               upper, colon, banding, message,anaesthetist):
    def movehtml():
        base = 'd:\\JOHN TILLET\\episode_data\\'
        dest = 'd:\\JOHN TILLET\\episode_data\\html-backup'

        for src in glob.glob(base + '*.html'):
            shutil.move(src, dest)

    first_patient = False
    doc_surname = doctor.split()[-1]
    if doc_surname =='Vivekanandarajah':
        doc_surname = 'Suhirdan'
    anaes_surname = anaesthetist.split()[-1]
    docs = doc_surname + '/' + anaes_surname
    upper = np.UPPER_DIC[upper]
    colon = np.COLON_DIC[colon]
    banding = np.BANDING_DIC[banding]
    today = datetime.datetime.now()
    today_str = today.strftime('%A' + '  ' + '%d' + ':' + '%m' + ':' + '%Y')
    head_string = "%s <br><br>\n" % (today_str)
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.html'
    stored_index = os.path.join('d:\\JOHN TILLET\\'
                                'episode_data\\' + date_filename)

    if consult in {'110', '116'}:
        out_str = ('<b>%s</b> - %s - - %s - CONSULT:<b> %s </b>- UPPER: %s - LOWER: %s'
                   '<b>%s</b> <br><br>\n') % (out_formatted, docs, print_name, consult, upper,
                                              colon, message)
    else:
        out_str = ('<b>%s</b>- %s - - %s - CONSULT: %s - UPPER: %s - LOWER: %s'
                   '<b> %s </b> <br><br>\n') % (out_formatted, docs, print_name, consult, upper,
                                                colon, message)

    if os.path.isfile(stored_index):
        with open(stored_index, 'r') as original:
            original.readline()
            data = original.read()
        with open(stored_index, 'w') as modified:
            modified.write(head_string + out_str + data)
    else:
        base = 'd:\\JOHN TILLET\\episode_data\\'
        dest = 'd:\\JOHN TILLET\\episode_data\\html-backup'
        for src in glob.glob(base + '*.html'):
            shutil.move(src, dest)

        with open(stored_index, 'w') as new_index:
            new_index.write(head_string + out_str)
            first_patient = True
    return stored_index, first_patient


def episode_opener(message):
    while True:
        if not pyautogui.pixelMatchesColor(150, 630, (255, 0, 0)):
            print('Open the patient file.')
            input('Hit Enter when ready.')
        else:
            break
    pyautogui.moveTo(150, 50)
    pyautogui.click()
    pyautogui.press('f8')
    while not pyautogui.pixelMatchesColor(
            534, 330, (102, 203, 234), tolerance=10):
        time.sleep(1)
    pyautogui.press('n')
    while not pyautogui.pixelMatchesColor(
            820, 130, (195, 90, 80), tolerance=10):
        time.sleep(1)
    pyautogui.typewrite(['down'] * 11, interval=0.1)
    pyautogui.press('enter')
    pyautogui.hotkey('alt', 'f')
    time.sleep(1)
    if pyautogui.pixelMatchesColor(520, 380, (25, 121, 202),
                                   tolerance=10):
        time.sleep(1)
        pyautogui.press('enter')
        pyautogui.press('c')
        pyautogui.hotkey('alt', 'f4')
        time.sleep(1)
        pyautogui.press('f8')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('enter')
        message += 'New episode made -'

    return message


def episode_discharge(intime, outtime, anaesthetist, doctor):
    pyautogui.hotkey('alt', 'i')
    time.sleep(1)
    pyautogui.PAUSE = 0.1
    pyautogui.typewrite(['enter'] * 4, interval=0.1)

    test = pyperclip.copy('empty')
    pyautogui.hotkey('ctrl', 'c')
    test = pyperclip.paste()
    if test != 'empty':
        pyautogui.alert(text='There is data here already! Try Again', title='', button='OK')
        time.sleep(1)        
        pyautogui.hotkey('alt', 'f4')
        raise BlueChipError
    pyautogui.typewrite(intime)
    pyautogui.typewrite(['enter'] * 2, interval=0.1)
    pyautogui.typewrite(outtime)
    pyautogui.typewrite(['enter'] * 3, interval=0.1)
    if anaesthetist != 'locum':
        pyautogui.typewrite(['tab'] * 6, interval=0.1)
        pyautogui.typewrite(anaesthetist)
        pyautogui.typewrite('\n')
        pyperclip.copy('fail')
    else:
        pyautogui.typewrite(['tab'] * 7, interval=0.1)

    pyautogui.typewrite(doctor)


def episode_procedures(upper, colon, banding, asa):
    pe_flag = False         # use these to keep state when entering lower lines
    banding_flag = False
    asa_flag = False

    def gastro_chooser(in_str):
        if in_str == '0':
            return False
        up_str = np.UPPER_DIC[in_str]
        pyautogui.typewrite(up_str + '\n')
        pyautogui.press('enter')

    def asa_chooser(asa):
        if asa == '0':
            return True
        a_str = np.ASA_DIC[asa]
        pyautogui.typewrite(a_str + '\n')
        pyautogui.press('enter')
        return True

    pyautogui.hotkey('alt', 'p')
    if colon == '0':
        pe_flag = gastro_chooser(upper)
    else:
        col_str = np.COLON_DIC[colon]
        pyautogui.typewrite(col_str + '\n')
        pyautogui.press('enter')

    pyautogui.typewrite(['tab'] * 6, interval=0.1)

    if upper != '0' and pe_flag is False:
        gastro_chooser(upper)
    elif banding == 'b':
        banding_flag = True
        pyautogui.typewrite('32135-00\n')
        pyautogui.press('enter')
    elif banding == 'a':
        banding_flag = True
        pyautogui.typewrite('32153-00\n')
        pyautogui.press('enter')
    else:
        asa_flag = asa_chooser(asa)

    if asa_flag:
        return
    else:
        pyautogui.typewrite(['tab'] * 2, interval=0.1)

    if banding == 'b'and banding_flag is False:
        banding_flag = True
        pyautogui.typewrite('32135-00\n')
        pyautogui.press('enter')
    elif banding == 'a':
        banding_flag = True
        pyautogui.typewrite('32153-00\n')
        pyautogui.press('enter')
    else:
        asa_flag = asa_chooser(asa)

    if asa_flag:
        return
    else:
        pyautogui.typewrite(['tab'] * 2, interval=0.1)

    asa_flag = asa_chooser(asa)

    if asa_flag:
        return


def episode_theatre(doctor, nurse, clips, varix_flag, varix_lot):
    pyautogui.hotkey('alt', 'n')
    pyautogui.typewrite(['left'] * 2, interval=0.1)
    pyautogui.moveTo(50, 155)
    pyautogui.click()
    pyautogui.press('tab')
    doc_test = pyperclip.copy('empty')
    pyautogui.hotkey('ctrl', 'c')
    doc_test = pyperclip.paste()
    if doc_test == 'Endoscopist':
        pyautogui.press('tab')
        pyautogui.typewrite(['enter'] * 2, interval=0.1)
        pyautogui.moveTo(450, 155)
        pyautogui.click()
        pyautogui.typewrite(['tab'] * 2, interval=0.1)
        pyautogui.typewrite(['enter'] * 2, interval=0.1)

    pyautogui.moveTo(50, 155)
    pyautogui.click()
    pyautogui.typewrite(doctor)
    pyautogui.typewrite(['enter', 'e', 'enter'], interval=0.1)
    pyautogui.moveTo(450, 155)
    pyautogui.click()
    pyautogui.typewrite(nurse)
    pyautogui.typewrite(['enter', 'e', 'enter'], interval=0.1)
    if clips != 0 or varix_flag is True:
        pyautogui.moveTo(50, 350)
        pyautogui.click()
        if varix_flag is True:
            pyperclip.copy('Boston Scientific Speedband Superview Super 7')
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            time.sleep(0.5)
            pyperclip.copy(varix_lot)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
            pyautogui.typewrite(['tab'] * 2, interval=0.1)
        if clips != 0:
            pyperclip.copy('M00521230')
            for i in range(clips):
                pyautogui.typewrite(['b', 'enter'], interval=0.2)
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'v')
                pyautogui.press('enter')
                pyautogui.typewrite(['tab'] * 2, interval=0.1)
    return None


def episode_scrape():
    pyautogui.hotkey('alt', 'd')
    pyautogui.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    title = pyperclip.paste()
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    first_name = pyperclip.paste()
    pyautogui.typewrite(['tab'] * 2, interval=0.1)
    pyautogui.hotkey('ctrl', 'c')
    last_name = pyperclip.paste()
    output_name = last_name + '   ' + first_name
    print_name = title + ' ' + first_name + ' ' + last_name
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    street_number = pyperclip.paste()
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    street_name = pyperclip.paste()
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    suburb = pyperclip.paste()
    suburb = suburb.lower()
    suburb = suburb.title()
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    postcode = pyperclip.paste()
    address = street_number + ' ' + street_name + ' ' + suburb + ' ' + postcode
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'c')
    dob = pyperclip.paste()
    pyautogui.typewrite(['tab'] * 6, interval=0.1)
    pyautogui.hotkey('ctrl', 'c')
    mcn = pyperclip.paste()
    pyperclip.copy(output_name)
    pyautogui.hotkey('alt', 'f4')
    return (mrn, print_name, address, dob, mcn)


def offsite(stored_index):
    session = ftplib.FTP('www.home.aone.net.au', 'ca121480@a1.com.au',
                         'Andromeda1957gd5mbunm')
    session.cwd('./dec/')
    with open(stored_index, 'rb') as file_handle:
        session.storlines('STOR today.html', file_handle)
    session.quit()


def to_csv(ep_data):
    """Input tuple of billing data and print it to csv."""
    csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\patients.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(ep_data)


def to_database(episode_data):
    """Write episode data to sqlite database"""
    db_file = 'sqlite:///d:\\JOHN TILLET\\episode_data\\episodes_db.db'
    db = dataset.connect(db_file)
    table = db['episodes']
    table.insert(episode_data)


def analysis():
    """Work out numbers of patients done this year and whether on target"""
    def report_number_this_week():
        try:
            with open('d:\\JOHN TILLET\\episode_data\\jtdata\\weekly_data.py', 'rb') as pf:
                weekly = pickle.load(pf)
                print('Number this week: {}'.format(str(weekly['number'])))
        except IOError:
            print('Cant find weekly_data file')
            sys.exit(1)

    print()
    desired_weekly = int(input('Weekly target: '))

    print('      **********')
    print('This period starts 1-7-2017')
    first_date = datetime.datetime(2017, 7, 1)
    today = datetime.datetime.today()
    days_diff = (today - first_date).days
    print('Days this period %d' % days_diff)
    first_invoice = 5057
    csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\patients.csv'
    with open(csvfile, 'r') as file_handle:
        reader = csv.reader(file_handle)
        first_bill = next(reader)
        first_bill_invoice = int(first_bill[15])
    with open('d:\\JOHN TILLET\\episode_data\\jtdata\\invoice_store.py', 'rb') as handle:
        last_invoice = pickle.load(handle)
    invoice_diff = int(last_invoice - first_invoice)
    desired_number = int(days_diff * desired_weekly / 7)
    weekly_number = int((7 * invoice_diff / days_diff))
    number_to_give_away = invoice_diff - desired_number
    print('Weekly target %d' % desired_weekly)
    print('Number done this period  %d' % invoice_diff)
    report_number_this_week()
    print('Number done this print run  %d' % (int(last_invoice) - first_bill_invoice))
    print('Weekly no. patients %d' % weekly_number)
    print('Number available to give away %d to avereage %d per week.'
          % (number_to_give_away, desired_weekly))
    print('      **********')


def update_web():
    """Update the webpage. After index has been changed."""
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.html'
    base = 'd:\\JOHN TILLET\\episode_data\\'
    stored_index = os.path.join(base + date_filename)
    offsite(stored_index)
    offsite_page = 'www.home.aone.net.au/~tillett/dec/today.html'
    webbrowser.open_new_tab(offsite_page)
    pyautogui.click(x=80, y=745)
    time.sleep(2)
    pyautogui.click(x=200, y=200)
    pyautogui.hotkey('ctrl', 'pageup')
    pyautogui.hotkey('ctrl', 'f4')
    print('Update succesful!')


def update_number_this_week():
    try:
        with open('d:\\JOHN TILLET\\episode_data\\jtdata\\weekly_data.py', 'rb') as pf:
            weekly = pickle.load(pf)
    except IOError:
        print('Cant find weekly_data file')
        sys.exit(1)

    if datetime.date.today() == weekly['last_procedure_date']:
        weekly['number'] += 1
        with open('d:\\JOHN TILLET\\episode_data\\jtdata\\weekly_data.py', 'wb') as pf:
            pickle.dump(weekly, pf)
    else:
        today = datetime.date.today()
        # if we are in the same week increment weekly['number']

        if weekly['last_procedure_date'] + datetime.timedelta(days=today.weekday()) >= today:
            weekly['number'] += 1
            weekly['last_procedure_date'] = datetime.date.today()
            with open('d:\\JOHN TILLET\\episode_data\\jtdata\\weekly_data.py', 'wb') as pf:
                pickle.dump(weekly, pf)
        else:
            csvfile = 'd:\\JOHN TILLET\\episode_data\\jtdata\\weekly_numbers.csv'
            with open(csvfile, 'a') as handle:
                datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
                datawriter.writerow(str(weekly['number']))
            weekly['number'] = 1
            weekly['last_procedure_date'] = datetime.date.today()
            with open('d:\\JOHN TILLET\\episode_data\\jtdata\\weekly_data.py', 'wb') as pf:
                pickle.dump(weekly, pf)
