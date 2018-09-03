# -*- coding: utf-8 -*-
from collections import  deque
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
import shelve
import sys
import time
import textwrap
import webbrowser

import colorama
import docx
from docx.shared import Mm, Pt
from fuzzyfinder import fuzzyfinder
import pyautogui as pya
import pyperclip

from inputbill import (inputer, LoopException)
import names_and_codes as nc
import decbatches

pya.FAILSAFE = True

today = datetime.datetime.now()

class EpFullException(Exception):
    pass

class BillingException(Exception):
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
         clips, varix_lot, in_theatre, out_theatre) = data_entry
         
        mrn, name = front_scrape()
        address, dob = address_scrape()
#        scrape fund details if billing anaesthetist
        if anaesthetist in nc.BILLING_ANAESTHETISTS and asa is not None:
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref)
        else:
            mcn = ref = fund = fund_number = ''
            
        shelver(mrn, in_theatre, out_theatre, anaesthetist, endoscopist, asa,
                upper, colon, banding, nurse, clips, varix_lot, message)
#        open day surgery and do some scrraping and pasting
#        message = episode_open(message)
#        episode_scrape(mrn)
#        mrn, name, address, postcode, dob = episode_scrape()
#        gp = episode_gp()
#        endoscopist = episode_discharge(
#                in_theatre, out_theatre, anaesthetist, endoscopist)
        
#        anaesthetic billing
        if asa is not None and anaesthetist in nc.BILLING_ANAESTHETISTS:
            anaesthetic_tuple, message = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                name, address, ref, fund, fund_number, endoscopist,
                anaesthetist, message)
            to_anaesthetic_csv(anaesthetic_tuple, anaesthetist)
            render_anaesthetic_report(anaesthetist)
            if fund == 'Overseas':
                message = print_receipt(
                        anaesthetist, anaesthetic_tuple, message)
     
#        web page with jinja2
        message = message_parse(message)  # break message into lines
        today_path = episode_to_csv(
                out_theatre, endoscopist, anaesthetist, name,consult,
                upper, colon, message, in_theatre, nurse, asa, banding, varix_lot)
        make_web_secretary(today_path)
        make_long_web_secretary(today_path)
#        data collection into csv - not essential
#        medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
#                            upper, colon, banding, postcode, dob)

#        finish data pasting into day surgery and exit
#        episode_procedures(upper, colon, banding, asa)
#        episode_theatre(endoscopist, nurse, clips, varix_lot)
#        if (upper in {'30490-00'}
#            or 'HALO' in message
#            or '32089-00' in message
#            or colon in {'32093-00', '32094-00'}
#            or banding in {'32153-00'}): 
#            episode_claim()
#        pya.click()
#        episode_close()
        time.sleep(2)
        close_out(anaesthetist)

    except (LoopException, EpFullException):
        raise


def front_scrape():
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
#        pya.press('down')
#        pya.press('enter')
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


def shelver(mrn, in_theatre, out_theatre, anaesthetist, endoscopist, asa,
            upper, colon, banding, nurse, clips, varix_lot, message):
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


def episode_scrape(mrn_front):
    pya.hotkey('alt', 'd')
    mrn = pyperclip.copy('')  # put '' on clipboard before each copy
    time.sleep(1)
    pya.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    if not mrn.isdigit() or mrn != mrn_front:
        pya.alert(text='Problem!! Try Again', title='', button='OK')
        time.sleep(1)
        pya.hotkey('alt', 'f4')
        raise EpFullException('EpFullException raised')
#    pya.press('tab')
#    title = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    title = pyperclip.paste()
#    pya.press('tab')
#    first_name = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    first_name = pyperclip.paste()
#    pya.typewrite(['tab'] * 2, interval=0.1)
#    last_name = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    last_name = pyperclip.paste()
#    print_name = title + ' ' + first_name + ' ' + last_name
#    pya.press('tab')
#    street_number = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    street_number = pyperclip.paste()
#    pya.press('tab')
#    street_name = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    street_name = pyperclip.paste()
#    pya.press('tab')
#    suburb = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    suburb = pyperclip.paste()
#    suburb = suburb.lower()
#    suburb = suburb.title()
#    pya.press('tab')
#    postcode = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    postcode = pyperclip.paste()
#    address = street_number + ' ' + street_name + ' ' + suburb + ' ' + postcode
#    pya.press('tab')
#    dob = pyperclip.copy('')
#    pya.hotkey('ctrl', 'c')
#    dob = pyperclip.paste()
#    return (mrn, print_name, address, postcode, dob)


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
    """Put breaks into message string."""
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
    """Write emessage to csv for web page generation."""
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


def write_as_billed(mrn):
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    temp_holder = []
    with open(today_path, 'r') as f:
        reader = csv.reader(
            f, dialect='excel', lineterminator='\n')
        for line in reader:
            if line[12] == mrn:
                line[13] = '&#10004;'
                temp_holder.append(line)
            else:
                temp_holder.append(line)
    with open(today_path, 'w') as handle:
        datawriter = csv.writer(
            handle, dialect='excel', lineterminator='\n')
        for line in temp_holder:
            datawriter.writerow(line)

    return today_path


def make_web_secretary(today_path):
    """Render jinja2 template and write to file for web page of today's patients"""
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
#    file_date = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
#    file_str = 'D:\\JOHN TILLET\\episode_data\\html-backup\\' + file_date + '.html'
#    with open(file_str, 'w') as f:
#        f.write(a)

def make_long_web_secretary(today_path):
    """Render jinja2 template and write to file for complete info on today's patients"""
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
    with open('D:\\JOHN TILLET\\episode_data\\watched\\watched.txt', mode='wt') as f:
        f.write('Howdy, watcher')


def medical_data_to_csv(endoscopist, consultant, anaesthetist, nurse,
                        upper, lower, anal, postcode, dob):
    """Drop episode info into csv file for statistics."""
    today_date = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    episode_data = (today_date, endoscopist, consultant, anaesthetist, nurse,
                    upper, lower, anal, postcode, dob)
    csvfile = 'D:\\JOHN TILLET\\episode_data\\medical_data.csv'
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)
 
def render_anaesthetic_report(anaesthetist):
    anaes_surname = anaesthetist.split()[-1]
    if anaes_surname == "Tillett":
        excess = jt_analysis()
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
                        anaes_surname = anaes_surname,
                        csv_length = csv_length,
                        excess = excess)
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
    """Return whether on weekly target from first_date.
    Count entries in master and current csv files.
    """
    first_date = datetime.datetime(2018, 4, 5)
    year = '2018'
    today = datetime.datetime.now()
#    first_date_lex = '20180401'
    results = 4
    with open('d:\JOHN TILLET\episode_data\sedation\Tillett_master.csv') as h:
        reader = csv.reader(h)
        for ep in reader:
            if ep[0].split('-')[-1] == year:
                results += 1
    
    with open('d:\JOHN TILLET\episode_data\sedation\Tillett.csv') as h:
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

        

def dantafind():
    """Fuzzy search for patients in Danta study."""
    file = 'D:\\JOHN TILLET\\episode_data\\dantapolypdata.csv'
    with open(file, 'r') as h:
        reader =csv.reader(h, delimiter=',')
        pat_list = [p[0].lower() for p in reader]
    clear()           
    while True:
        print()
        query_string = input('Name in lower case, q to quit:  ')
        if query_string == 'q':
            break     
        if query_string == '':
            clear()
            continue
        try:
            suggestions = fuzzyfinder(query_string, pat_list)
            suggestions = sorted(
                        list(suggestions), key= lambda x: x.split()[-1])
            clear()
            if not suggestions:
                print('No one here.')
            else:
                for p in suggestions:
                    print(p)
        except UnicodeDecodeError:
            print('Try another list of letters!')
            continue

def print_receipt(anaesthetist, episode, message):

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
    

def update_web():
    date_file_str = today.strftime(
             '%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
     'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    make_web_secretary(today_path)
    make_long_web_secretary(today_path)



def intro(anaesthetist):
    clear()
    anaes_surname = anaesthetist.split()[-1]
    print('Dear Dr  {}'.format(anaes_surname))
    intro_message = textwrap.dedent('''\
        Sabine.
        Can you find out what the doctors fund
        is currently paying? I can't find it.
        Your contact details updated to the same as Greg.
        John''')

    print(intro_message)
    input()
    webbrowser.open('d:\\Nobue\\anaesthetic_fees.html')
    
            
       

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
#        if anaesthetist == 'Dr S Vuong':
#            intro(anaesthetist)

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
                    '', 'q', 'c', 's', 'a', 'u', 'rec', 
                    'r', 'w', 'p', 'm', 'sw', 'df'}:
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
                if choice =='sw':
                    os.startfile(
                            'D:\\JOHN TILLET\\source\\active\\billing\\watcher.py')
                if choice == 'df':
                    dantafind()
                if choice == 'u':
                     date_file_str = today.strftime(
                             '%Y' + '-' + '%m' + '-' + '%d')
                     date_filename = date_file_str + '.csv'
                     today_path = os.path.join(
                             'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
                     make_web_secretary(today_path)
                     make_long_web_secretary(today_path)
                     try:
                         render_anaesthetic_report(anaesthetist)
                     except:
                         pass
                if choice == 'm':
                    nowtime = datetime.datetime.now()
                    nowtime = nowtime.strftime('%H' + ':' + '%M')
                    message = input('Message: ')
                    today_path =  episode_to_csv(
                            nowtime, endoscopist, anaesthetist, '','', '', '',
                            message,'','','','','')
                    make_web_secretary(today_path)
                    webbrowser.open('d:\\Nobue\\today_new.html')
                if choice == 'rec':
                    os.startfile('d:\\JOHN TILLET\\episode_data\\os_acc.docx')
                    
            except Exception as err:
                logger.error(err)
                sys.exit(1)

if __name__ == '__main__':
    login_and_run()
