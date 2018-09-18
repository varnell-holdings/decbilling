# -*- coding: utf-8 -*-
"""Gui for dec billing."""


import argparse
from collections import  deque
import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from jinja2 import Environment, FileSystemLoader
import os
import pickle
import shelve
import sys
import time
import webbrowser

from tkinter import ttk, StringVar, Tk, W, E, N, S, Spinbox, FALSE, Menu

import docx
import pyautogui as pya
import pyperclip

import decbatches

pya.PAUSE = 0.4

class BillingException(Exception):
    pass


ANAESTHETISTS = ['Dr D Bowring',
                 'Dr C Brown',
                 'Dr Felicity Doherty',
                 'Dr N Ignatenko',
                 'locum',
                 'Dr B Manasiev',
                 'Dr M Moyle',
                 "Dr E O'Hare",
                 "Dr Martine O'Neill",
                 "Dr G O'Sullivan",
                 'Dr J Riley',
                 'Dr Timothy Robertson',
                 'Dr N Steele',
                 'Dr J Stevens',
                 'Dr M Stone',
                 'Dr J Tester',
                 'Dr J Tillett',
                 'Dr S Vuong',
                 'Dr Rebecca Wood']



BILLING_ANAESTHETISTS = ['Dr S Vuong', 'Dr J Tillett' ]

NURSES = ['Belinda Plunkett',
          'Belinda Vickers',
          'Cheryl Guise',
          'Eva Aliparo',
          'Jacinta Goldenberg',
          'Jacqueline James',
          'Jacqueline Smith',
          'Larissa Berman',
          'Lorae Tamayo',
          'Mary Halter',
          'Nobue Chashin',
          'Parastoo Tavakoli Siahkali',
          'Subeia Aziz Silva',
          'Yi Lu']

ENDOSCOPISTS = ['Dr C Bariol',
                'DR M Danta',
                'Dr R Feller',
                'DR R Gett',
                'Dr S Ghaly',
                'Prof R Lord',
                'Dr A Meagher',
                'Dr A Stoita',
                'Dr C Vickers',
                'Dr S Vivekanandarajah',
                'Dr A Wettstein',
                'Dr D Williams',
                'Dr N De Luca',
                'Dr G Owen',
                'Dr A Kim',
                'Dr J Mill',
                'Dr V Nguyen',
                'Dr Yang Wu',
                'Dr Craig HAIFER',
                'Dr S Sanagapalli']

ASA = ['No Sedation', '1', '2', '3']

ASA_DIC = {'No Sedation': None,
           '1': '92515-19',
           '2': '92515-29',
           '3': '92515-39',
           '4': '92515-49'}

UPPERS = ['None',         
          'Pe',
          'Pe with bx',
          'Oesophageal diatation',
          'Pe with APC',         
          'Pe with polypectomy',
          'Pe with varix banding',
          'BRAVO',
          'HALO',
          'Cancelled']

UPPER_DIC = {'None': None,
             'Cancelled': None,
             'Pe': '30473-00',
             'Pe with bx': '30473-01',
             'Oesophageal diatation': '30475-00',
             'Pe with APC': '30478-20',
             'HALO': '30478-20',
             'Pe with polypectomy': '30478-04',
             'Pe with varix banding': '30478-20',
             'BRAVO': '30490-00'}

COLONS = ['None',
          'Long Colon',
          'Long Colon with bx',
          'Long Colon with polyp',
          'Short Colon',
          'Short Colon with bx',
          'Short Colon with polyp',
          'Cancel lower procedure',
          'Colon - Govt FOB screening',
          'Colon with polyp - Govt FOB screening']

COLON_DIC = {'None': None,
             'Cancel lower procedure': None,
             'Long Colon': '32090-00',
             'Colon - Govt FOB screening': '32088-00',
             'Long Colon with bx': '32090-01',
             'Long Colon with polyp': '32093-00',
             'Colon with polyp - Govt FOB screening': '32089-00',
             'Short Colon': '32084-00',
             'Short Colon with bx': '32084-01',
             'Short Colon with polyp': '32087-00'}

BANDING = ['None',
           'Banding of haemorrhoids',
           'Anal dilatation']

BANDING_DIC = {'None': None,
               'Banding of haemorrhoids': '32135-00',
               'Anal dilatation': '32153-00'}


CONSULT_LIST = ['None', 'Long - 110', 'Short - 117']

CONSULT_DIC = {'None': None,
               'Long - 110': '110',
               'Short - 117': '117'}

FUND_TO_CODE = {'HCF': 'hcf',
                'BUPA' : 'bup',
                'Medibank Private': 'mpl',
                'NIB': 'nib',
                "The Doctor's Fund": 'ama',
                'Australian Health Management': 'ahm',
                'Pensioner': 'p',
                'Uninsured': 'u',
                'Veterans Affairs': 'va',
                'Overseas': 'os',
                'Garrison Health': 'ga'}


FUNDS = ['BUPA',
             'HCF',
            'Medibank Private',
            'NIB',           
            'Australian Health Management',
            'Pensioner',
            'Uninsured',
            'Veterans Affairs',
            'Overseas',
            'Garrison Health',
            "The Doctor's Fund",
            '++++++++++++++++',
            'Australian Unity Health',
            'CBHS Health',
            'Cessnock District Health',
            'Credicare',
            'CUA',
            'Defence Health',
            "The Doctor's Fund",
            'Frank Health',
            'GMHBA',          
            'Grand United Corporate Health',
            'health.com.au',
            'Health Insurance Fund of WA',
            'Health Partners',
            'HBF',
            'Naval Health Benefits',
            'Peoplecare Health',
            'Pheonix Health',           
            'Railway & Transport Health',
            'Reserve Bank',
            'Teachers Federation Health',
            'Westfund']


today = datetime.datetime.today()

def in_and_out_calculater(time_in_theatre):
    """Calculate formatted in and out times given time in theatre."""
    time_in_theatre = int(time_in_theatre)
    nowtime = datetime.datetime.now()
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    return (in_formatted, out_formatted)


def front_scrape():
    """Scrape name and mrn from blue chip."""
    def get_title():
        pya.hotkey('alt', 't')
        title = pyperclip.copy('na')
        pya.moveTo(190, 135, duration=0.1)
        pya.click(button='right')
        pya.moveRel(55, 65)
        pya.click()
        title = pyperclip.paste()
        return title

    pya.click(50, 450)
    title = get_title()
    
    if title == 'na':
        pya.press('alt')
        pya.press('b')
        pya.press('c')
        title = get_title()
    
    if title == 'na':
        pya.alert('Error reading Blue Chip.')
        raise BillingException

    for i in range(4):
        first_name = pyperclip.copy('na')
        pya.moveTo(290, 135, duration=0.1)
        pya.click(button='right')
        pya.moveRel(55, 65)
        pya.click()
        first_name = pyperclip.paste()
        if first_name != 'na':
            break
        if first_name == 'na':
            first_name = pya.prompt(text='Please enter patient first name',
                              title='First Name',
                              default='')

    for i in range(4):
        last_name = pyperclip.copy('na')
        pya.moveTo(450, 135, duration=0.1)
        pya.click(button='right')
        pya.moveRel(55, 65)
        pya.click()
        last_name = pyperclip.paste()
        if last_name != 'na':
            break
        if last_name == 'na':
            last_name = pya.prompt(text='Please enter patient surname',
                              title='Surame',
                              default='')
 
    print_name = title + ' ' + first_name + ' ' + last_name

    mrn = pyperclip.copy('na')
    pya.moveTo(570, 250, duration=0.1)
    pya.dragTo(535, 250, duration=0.1)
    pya.moveTo(570, 250, duration=0.1)
    pya.click(button='right')
    pya.moveRel(55, 65)
    pya.click()
    mrn = pyperclip.paste()
    if not mrn.isdigit():
        mrn = pya.prompt("Please enter this patient's MRN")
    
    return (mrn, print_name)
        
def address_scrape():
    """Scrape address and dob from blue chip.
    Used if billing anaesthetist.
    """
    dob = pyperclip.copy('na')
    pya.moveTo(600, 175, duration=0.1)
    pya.click(button='right')
    pya.moveRel(55, 65)
    pya.click()
    dob = pyperclip.paste()
    
    street = pyperclip.copy('na')
    pya.moveTo(500, 240, duration=0.1)
    pya.click(button='right')
    pya.moveRel(55, 65)
    pya.click()
    street = pyperclip.paste()
    
    suburb = pyperclip.copy('na')
    pya.moveTo(330, 285, duration=0.1)
    pya.click(button='right')
    pya.moveRel(55, 65)
    pya.click()
    suburb = pyperclip.paste()
    
    postcode = pyperclip.copy('na')
    pya.moveTo(474, 285, duration=0.1)
    pya.dragTo(450, 285, duration=0.1)
    pya.moveTo(474, 285, duration=0.1)
    pya.click(button='right')
    pya.moveRel(55, 65)
    pya.click()
    postcode = pyperclip.paste()

    address = street + ' ' + suburb + ' ' + postcode

    return (address, dob)


def episode_get_mcn_and_ref():
    """Scrape mcn from blue chip."""
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
    """Scrape fund name from blue chip."""
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
    """Scrape fund number from blue chip."""
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
    """Controller function for scraping fund and medicare details.
    ref may contain garrison episode id.
    """
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


def shelver(mrn, in_theatre, out_theatre, anaesthetist, endoscopist, asa,
            upper, colon, banding, nurse, clips, varix_lot, message):
    """Write episode  data to a shelf.
    Used by watcher.py to dump data in day surgery.
    """
    with shelve.open('d:\\JOHN TILLET\\episode_data\\dumper_data.db') as s:
        s[mrn] = { 
                'in_theatre': in_theatre,
                'out_theatre': out_theatre,
                'anaesthetist': anaesthetist,
                'endoscopist': endoscopist,
                'asa': asa,
                'upper': upper,
                'colon': colon,
                'banding': banding,
                'nurse': nurse,
                'clips': clips,
                'varix_lot': varix_lot,
                'message': message,
                }


# Utility fucntions for bill processing

def get_age_difference(dob):
    """Is patients 70 or older?"""
    dob = parse(dob, dayfirst=True)
    age_sep = relativedelta(today, dob)
    return age_sep.years


def get_invoice_number():
    """Get pickled invoice, increment and repickle."""
    s = 'd:\\JOHN TILLET\\episode_data\\invoice_store.py'
    with open(s, 'r+b') as handle:
        invoice = pickle.load(handle)
        invoice += 1
        handle.seek(0)
        pickle.dump(invoice, handle)
        handle.truncate()
    return invoice


def get_time_code(op_time):
    """Calculate medicare time code from time in theatre."""
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
    """Turn raw data into stuff ready to go into anaesthetic csv file."""
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
    if anaesthetist == 'Dr J Tillett' and (insur_code == 'u' or insur_code == 'p'):
        insur_code = 'bb'
        message += 'JT will bulk bill.'
    elif anaesthetist == 'Dr S Vuong' and (insur_code == 'u' or insur_code == 'p'):
        insur_code = 'bb'
        message += 'SV will bulk bill.'

    time_code = get_time_code(op_time)

    invoice = get_invoice_number()
    invoice = 'DEC' + str(invoice)

    ae_csv = (today_for_invoice, patient, address, dob, mcn, ref,
              fund, fund_number, insur_code, endoscopist, upper_done,
              lower_done, age_seventy, asa_three, time_code, invoice)

    return ae_csv, message


def message_parse(message):
    """Put line breaks into message string."""
    message = message.rstrip('.')
    message = message.replace('.', '<br>')
    return message


def to_anaesthetic_csv(episode_data, anaesthetist):
    """Write tuple of anaesthetic billing data to csv
    for billing anaesthetists"""
    surname = anaesthetist.split()[-1]
    csvfile = 'd:\\JOHN TILLET\\episode_data\\sedation\\{}.csv'.format(surname)
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)


def message_to_csv(message):
    """Write message to csv for web page generation."""
    nowtime = datetime.datetime.now()
    nowtime = nowtime.strftime('%H' + ':' + '%M')
    episode_data = (nowtime, '', '',
                    '', '', '', message,
                    '', '', '', '', '', '', '')
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    with open(today_path, 'a') as handle:
        datawriter = csv.writer(
            handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)

    return today_path


def episode_to_csv(outtime, endoscopist, anaesthetist, patient,
                   consult, upper, colon, message, intime,
                   nurse, asa, banding, varix_lot, mrn):
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
    billed = ''
    episode_data = (outtime, docs, patient,
                    consult, upper, colon, message,
                    intime, nurse, asa, banding, varix_lot, mrn, billed)
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
    """Render jinja2 template
    and write to file for web page of today's patients
    """
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


def make_long_web_secretary(today_path):
    """Render jinja2 template
    and write to file for complete info on today's patients
    """
    today_str = today.strftime(
        '%A' + '  ' + '%d' + '-' + '%m' + '-' + '%Y')
    today_data = deque()
    with open(today_path) as data:
        reader = csv.reader(data)
        for ep in reader:
            today_data.appendleft(ep)
    path_to_template = 'D:\\JOHN TILLET\\episode_data\\today_long_sec_template.html'
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = 'today_long_sec_template.html'
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open('d:\\Nobue\\today_long.html', 'w') as f:
        f.write(a)
    file_date = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    file_str = 'D:\\JOHN TILLET\\episode_data\\html-backup\\' + file_date + '.html'
    with open(file_str, 'w') as f:
        f.write(a)


def to_watched():
    """Write dummy text to a folder. Watchdog in watcher.py watches this."""
    with open('D:\\JOHN TILLET\\episode_data\\watched\\watched.txt', mode='wt') as f:
        f.write('Howdy, watcher')


def render_anaesthetic_report(anaesthetist):
    """Make a web page if billing anaesthetist showing patients done today."""
    anaes_surname = anaesthetist.split()[-1]
    today_data = []
    count = 0
    csv_length = 0
    today_date = today.strftime('%d' + '-' + '%m' + '-' + '%Y')
    csvfile = 'd:\\JOHN TILLET\\episode_data\\sedation\\{}.csv'.format(anaes_surname)
    with open(csvfile) as handle:
        reader = csv.reader(handle)
        for episode in reader:
            csv_length += 1
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
                        anaes_surname=anaes_surname,
                        csv_length=csv_length)
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
    if anaesthetist in BILLING_ANAESTHETISTS:
        webbrowser.open(
            'd:\\Nobue\\report_{}.html'.format(anaesthetist.split()[-1]))


def jt_analysis():
    """Return difference from weekly target from first_date.
    Counts entries in master and current csv files.
    """
    first_date = datetime.datetime(2018, 4, 5)
    year = '2018'
    today = datetime.datetime.now()
#    first_date_lex = '20180401'
    results = 4
    with open('d:\\JOHN TILLET\\episode_data\\sedation\\Tillett_master.csv') as h:
        reader = csv.reader(h)
        for ep in reader:
            if ep[0].split('-')[-1] == year:
                results += 1

    with open('d:\\JOHN TILLET\\episode_data\\sedation\\Tillett.csv') as h:
        reader = csv.reader(h)
        for ep in reader:
            if ep[0].split('-')[-1] == year:
                results += 1
    a = today - first_date
    days_diff = a.days
    desired_weekly = 60
    desired_number = int(days_diff * desired_weekly / 7)
    excess = results - desired_number
    return excess


def print_receipt(anaesthetist, episode, message):
    """Print a receipt if overseas patient."""
    headers = ["date", "name", "address", "dob", "medicare_no", "ref",
               "fund_name", "fund_number", "fund_code", "doctor",
               "upper", "lower", "seventy", "asa_3", "time", "invoice"]
    episode = dict(zip(headers, episode))

    (grand_total, consult_as_float, unit,
            time_fee, total_fee) = decbatches.process_acc(0.0, episode)   

    message += 'Bill pt ${:.0f} for {}.'.format(total_fee, anaesthetist)
    doc = docx.Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Verdana'
    acc = decbatches.print_account(episode, doc, unit, consult_as_float,
                  time_fee, total_fee, anaesthetist)
    printfile = 'd:\\JOHN TILLET\\episode_data\\os_acc.docx'
    acc.save(printfile)
    return message


# menu bar programs
def open_roster():
    webbrowser.open('d:\\Nobue\\anaesthetic_roster.html')

def open_today():
    nob_today = 'd:\\Nobue\\today_new.html'
    webbrowser.open(nob_today)

def open_dox():
    pya.hotkey('ctrl', 'w')

def start_watcher():
    os.startfile(
                 'D:\\JOHN TILLET\\source\\active\\billing\\watcher.py')

def open_receipt():
    os.startfile('d:\\JOHN TILLET\\episode_data\\os_acc.docx')

def send_message():
    message = pya.prompt(text='Enter your message',
                               title='Message',
                               default='')
    today_path =  message_to_csv(message)
    make_web_secretary(today_path)


def update():
    today = datetime.datetime.now()
    date_file_str = today.strftime(
                             '%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
             'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    make_web_secretary(today_path)
    make_long_web_secretary(today_path)
    nob_today = 'd:\\Nobue\\today_new.html'
    webbrowser.open(nob_today)


def open_help():
    webbrowser.open('d:\\nobue\\help.html')

def runner(*args):
    """Main program. Runs when button pushed."""
    
    try:
        insur_code, fund, ref, fund_number, message = '', '', '','', ''
    
        anaesthetist = an.get()
        endoscopist = end.get()
        nurse = nur.get()
    
        asa = asc.get()
        if asa == 'No Sedation':
            message += 'No sedation.'
        asa = ASA_DIC[asa]
        
    
        upper = up.get()
        if upper == 'Cancelled':
            message += 'Upper cancelled.'
        if upper == 'Pe with varix banding':
            message += 'Bill varix bander.'
            varix_lot = pya.prompt(text='Enter the varix bander lot number.',
                                   title='Varix',
                                   default='')
        else:
            varix_lot = ''
        if upper == 'HALO':
            halo = pya.prompt(text='Type either "90" or "ultra".',
                              title='Halo',
                              default='90')
            message += halo + '.'
        upper = UPPER_DIC[upper]
    
        colon = co.get()
        if colon == 'Cancelled':
            message += 'Colon Cancelled.'
        colon = COLON_DIC[colon]
    
        banding = ba.get()
        if banding == 'Banding of haemorrhoids':
            message += ' Banding haemorrhoids.'
            if endoscopist == 'Dr A Wettstein':
               message += ' Bill bilateral pudendal blocks.'
        if banding == 'Anal Dilatation':
            message += ' Anal dilatation.'
            if endoscopist == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks.'
        banding = BANDING_DIC[banding]
    
        clips = cl.get()
        clips = int(clips)
        if clips != 0:
            message += 'clips * {}.'.format(clips)
    
        consult = con.get()
        consult = CONSULT_DIC[consult]
    
        formal_message = mes.get()
        if formal_message:
            message += formal_message + '.'
    
        op_time = ot.get()
        op_time = int(op_time)

        if anaesthetist in BILLING_ANAESTHETISTS:  
            fund = fu.get()
            if fund == '':
                pya.alert(text='No fund!')
                raise BillingException
        
        insur_code = FUND_TO_CODE.get(fund, 'ahsa')
        if insur_code == 'ga':
            ref = pya.prompt(text='Enter Episode Id',
                             title='Ep Id',
                             default=None)
            fund_number = pya.prompt(text='Enter Approval Number',
                                     title='Approval Number',
                                     default=None)
        if insur_code == 'os':
            paying = pya.confirm(text='Paying today?', title='OS', buttons=['Yes', 'No'])
            if paying == 'Yes':
                fund = 'Overseas'
            else:
                fund = pya.prompt(text='Enter Fund Name',
                                  title='Fund',
                                  default='Overseas')
    
        (in_theatre, out_theatre) = in_and_out_calculater(op_time)
    
        if upper is None and colon is None:
            pya.alert(text='You must enter either an upper or lower procedure!',
                      title='', button='OK')
            raise BillingException
    
        if banding is not None and colon is None:
            pya.alert(text='Must enter a lower procedure with the anal procedure!',
                      title='', button='OK')
            raise BillingException
    
        if '' in (anaesthetist, endoscopist, nurse):
            pya.alert(text='Missing data!',
                      title='', button='OK')
            raise BillingException
        
        pya.click(50, 450)
        while True:
            if not pya.pixelMatchesColor(150, 630, (255, 0, 0)):
                pya.alert(text='Patient file not open??')
                raise BillingException
            else:
                break

        mrn, name = front_scrape()

        shelver(mrn, in_theatre, out_theatre, anaesthetist, endoscopist, asa,
                upper, colon, banding, nurse, clips, varix_lot, message)

      
    #        anaesthetic billing
        if asa is not None and anaesthetist in BILLING_ANAESTHETISTS:
            address, dob = address_scrape()
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref)

            anaesthetic_tuple, message = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                name, address, ref, fund, fund_number, endoscopist,
                anaesthetist, message)
            to_anaesthetic_csv(anaesthetic_tuple, anaesthetist)
            
            if fund == 'Overseas':
                message = print_receipt(
                        anaesthetist, anaesthetic_tuple, message)
     
        message = message_parse(message)
        today_path = episode_to_csv(
                out_theatre, endoscopist, anaesthetist, name,consult,
                upper, colon, message, in_theatre,
                nurse, asa, banding, varix_lot, mrn)
        make_web_secretary(today_path)
        make_long_web_secretary(today_path)
        to_watched()
    
        time.sleep(2)
        if anaesthetist in BILLING_ANAESTHETISTS:
            render_anaesthetic_report(anaesthetist)
        close_out(anaesthetist)
    except BillingException:
        return

    # reset variables in gui
    asc.set('1')
    up.set('None')
    co.set('None')
    ba.set('None')
    cl.set('0')
    con.set('None')
    mes.set('')
    ot.set('20')
    fu.set('')

parser = argparse.ArgumentParser()
parser.add_argument("--bill", help="Use program for billing.", action="store_true")
args = parser.parse_args()
# Set up gui. Runs on program load.
root = Tk()
root.title('Dec Billing')
root.geometry('350x450+900+100')
root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#win = Toplevel(root)
menubar = Menu(root)
root.config(menu=menubar)
#win['menu'] = menubar
menu_extras = Menu(menubar)
menu_admin = Menu(menubar)
menu_accounts = Menu(menubar)
menu_help = Menu(menubar)

menubar.add_cascade(menu=menu_extras, label='Extras')
menu_extras.add_command(label='Roster', command=open_roster)
menu_extras.add_command(label='Web Page', command=open_today)
menu_extras.add_command(label='Dox', command=open_dox)
#menu_extras.add_command(label='Spyder', command=start_spyder)
menu_extras.add_command(label='Message', command=send_message)

menubar.add_cascade(menu=menu_admin, label='Admin')
menu_admin.add_command(label='Update', command=update)
menu_admin.add_command(label='Watcher', command=start_watcher)

menubar.add_cascade(menu=menu_accounts,  label='Accounts')
menu_accounts.add_command(label='Receipt', command=open_receipt)

menubar.add_cascade(menu=menu_help,  label='Help')
menu_help.add_command(label='Help Page', command=open_help)


an = StringVar()
end = StringVar()
nur = StringVar()
asc = StringVar()
up = StringVar()
co = StringVar()
ba = StringVar()
cl = StringVar()
con = StringVar()
mes = StringVar()
ot = StringVar()
fu = StringVar()

ttk.Label(mainframe, text="Anaesthetist").grid(column=1, row=1, sticky=W)
an = ttk.Combobox(mainframe, textvariable=an)
an['values'] = ANAESTHETISTS
an['state'] = 'readonly'
an.grid(column=2, row=1, sticky=W)

ttk.Label(mainframe, text="Endoscopist").grid(column=1, row=2, sticky=W)
end = ttk.Combobox(mainframe, textvariable=end)
end['values'] = ENDOSCOPISTS
end['state'] = 'readonly'
end.grid(column=2, row=2, sticky=W)

ttk.Label(mainframe, text="Nurse").grid(column=1, row=3, sticky=W)
nur = ttk.Combobox(mainframe, textvariable=nur)
nur['values'] = NURSES
nur['state'] = 'readonly'
nur.grid(column=2, row=3, sticky=W)

ttk.Label(mainframe, text="ASA").grid(column=1, row=4, sticky=W)
asc = ttk.Combobox(mainframe, textvariable=asc)
asc['values'] = ASA
asc['state'] = 'readonly'
asc.grid(column=2, row=4, sticky=W)

ttk.Label(mainframe, text="Upper").grid(column=1, row=5, sticky=W)
up = ttk.Combobox(mainframe, textvariable=up)
up['values'] = UPPERS
up['state'] = 'readonly'
up.grid(column=2, row=5, sticky=W)

ttk.Label(mainframe, text="Lower").grid(column=1, row=6, sticky=W)
co = ttk.Combobox(mainframe, textvariable=co)
co['values'] = COLONS
co['state'] = 'readonly'
co.grid(column=2, row=6, sticky=W)

ttk.Label(mainframe, text="Anal").grid(column=1, row=7, sticky=W)
ba = ttk.Combobox(mainframe, textvariable=ba)
ba['values'] = BANDING
ba['state'] = 'readonly'
ba.grid(column=2, row=7, sticky=W)

ttk.Label(mainframe, text="Clips").grid(column=1, row=8, sticky=W)
s = Spinbox(mainframe, from_=0, to=20, textvariable=cl)
s.grid(column=2, row=8, sticky=W)

ttk.Label(mainframe, text="Consult").grid(column=1, row=9, sticky=W)
con = ttk.Combobox(mainframe, textvariable=con)
con['values'] = CONSULT_LIST
con['state'] = 'readonly'
con.grid(column=2, row=9, sticky=W)

ttk.Label(mainframe, text="Message").grid(column=1, row=10, sticky=W)
ttk.Entry(mainframe, textvariable=mes).grid(column=2, row=10, sticky=W)


ttk.Label(mainframe, text="Time").grid(column=1, row=11, sticky=W)
ti = Spinbox(mainframe, from_=0, to=90, textvariable=ot)
ti.grid(column=2, row=11, sticky=W)

if args.bill:
    ttk.Label(mainframe, text="Fund").grid(column=1, row=12, sticky=W)
    fun = ttk.Combobox(mainframe, textvariable=fu)
    fun['values'] = FUNDS
    # fun['state'] = 'readonly'
    fun.grid(column=2, row=12, sticky=W)

ttk.Button(mainframe, text='Send!', command=runner).grid(
    column=2, row=13, sticky=W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
root.bind('<Return>', runner)
asc.set('1')
up.set('None')
co.set('None')
ba.set('None')
con.set('None')
ot.set('20')
fu.set('')

root.mainloop()
