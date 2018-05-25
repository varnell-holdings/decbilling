
# coding: utf-8

# In[1]:

import csv
from collections import defaultdict
import math
import os
import sys
import time

import docx
from docx.shared import Mm

from names_and_codes import FUND_FEES, BILLER


# %load ./helpers/printacc.py
"""Prints a single accout to a docx document and returns it"""
def yes_no_decode(up ,low, age, asa):
    if up in {'Yes', 'No'}:
         up = 'upper_' + up
         low = 'lower_' + low
         age = 'age70_' + age
         asa = 'asa3_' + asa
    return up, low, age, asa


def print_account(ep, doc, unit, consult_as_float,
                  time_fee, total_fee, biller):

    biller = BILLER[biller]

    if ep['fund_code'] == 'ga':
        doc.add_heading('Account for Anaesthetic\nTo:'
                        ' Garrison Health Services, fax  1300 633 227',
                        level=1)
    else:
        doc.add_heading('Account for Anaesthetic', level=0)

    doc.add_heading(biller['name'], level=2)
    doc.add_heading(biller['address'], level=4)
    doc.add_heading('Provider Number: ' + biller['provider'], level=5)
    doc.add_heading(biller['contact'], level=5)
    doc.add_paragraph('')

    h_head = doc.add_heading('Patient Details', level=4)
    inv_string = '%s%s%s' % (('  ' * 20), 'Invoice Number  ', ep['invoice'])
    h_head.add_run(inv_string)
    doc.add_paragraph('')
    doc.add_paragraph('%s' % ep['name'])
    doc.add_paragraph('%s' % ep['address'])
    doc.add_paragraph('Date of birth  %s' % ep['dob'])
    if ep['fund_code'] == 'ga':
        doc.add_paragraph(
            'Fund:  %s   Episode Number:  %s' % (ep['fund_name'], ep['ref']))
        p_ga = doc.add_paragraph('Approval Number:')
        ga_str = '   %s' % ep['fund_number']
        p_ga.add_run(ga_str)
    elif ep['fund_code'] == 'os':
        doc.add_paragraph(
            'Fund:  %s   Number:  %s' % (ep['fund_name'], ep['fund_number']))
        doc.add_paragraph(
            'Patient not registered with Medicare for this service.')
    else:
        doc.add_paragraph(
            'Fund:  %s   Number:  %s' % (ep['fund_name'], ep['fund_number']))
        p_mc = doc.add_paragraph('Medicare Number')
        mc_str = '   %s    ref  %s' % (ep['medicare_no'], ep['ref'])
        p_mc.add_run(mc_str)
    doc.add_paragraph('Date of Procedure:  %s' % ep['date'])
    doc.add_paragraph('Procedure performed by %s' % ep['doctor'])
    doc.add_paragraph('Diagnostic Endoscopy Centre, Darlinghurst, NSW 2010')

    doc.add_paragraph('Item Number%sFee' % (' ' * 10))

    p_cons = doc.add_paragraph('17610')
    cons_str = '%.2f' % consult_as_float
    cons_str = cons_str.rjust(25)
    p_cons.add_run(cons_str)
    
    ep['upper'], ep['lower'], ep['seventy'], ep['asa_3'] = yes_no_decode(
            ep['upper'], ep['lower'], ep['seventy'], ep['asa_3']) 
    
    if ep['upper'] == 'upper_Yes':
        p_endo = doc.add_paragraph('20740')
        endo_str = '%.2f' % (unit * 5)
        endo_str = endo_str.rjust(24)
        p_endo.add_run(endo_str)
        if ep['lower'] == 'lower_Yes':
            p_col = doc.add_paragraph('20810')
            col_str = '%.2f' % 0.0
            col_str = col_str.rjust(26)
            p_col.add_run(col_str)
    if ep['upper'] == 'upper_No' and ep['lower'] == 'lower_Yes':
        p_col = doc.add_paragraph('20810')
        col_str = '%.2f' % (unit * 4)
        col_str = col_str.rjust(24)
        p_col.add_run(col_str)
    if ep['seventy'] == 'age70_Yes':
        p_age = doc.add_paragraph('25015')
        age_str = '%.2f' % unit
        age_str = age_str.rjust(25)
        p_age.add_run(age_str)
    if ep['asa_3'] == 'asa3_Yes':
        p_sick = doc.add_paragraph('25000')
        sick_str = '%.2f' % unit
        sick_str = sick_str.rjust(25)
        p_sick.add_run(sick_str)

    p_time_fee = doc.add_paragraph(ep['time'])
    time_fee_str = '%.2f' % time_fee
    time_fee_str = time_fee_str.rjust(25)
    p_time_fee.add_run(time_fee_str)

    p_tot = doc.add_paragraph('Total Fee')
    tot_str = '$%.2f' % total_fee
    tot_str = tot_str.rjust(19)
    p_tot.add_run(tot_str)

    doc.add_paragraph('')
    p_gst = doc.add_paragraph('')
    p_gst.add_run('No item on this invoice attracts GST').italic = True
    doc.add_page_break()

    section = doc.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    return doc


# In[ ]:

# %load ./helpers/printcalc.py
"""calculate number of invoices to print if there are more than 20."""


def print_calc(n):
    divisor = math.ceil(n / 20)
    return math.floor(n / divisor)


# In[ ]:

# %load ./helpers/printheader.py

def print_batch_header(doc, fund, number_printed, total):
    if fund[:4] == 'ahsa':
        fund = fund[5:]
    doc.add_heading('Batch Header', level=0)
    doc.add_paragraph('')
    doc.add_paragraph('Fund:  %s' % fund)
    doc.add_paragraph('')
    doc.add_paragraph('Number in batch:  %d' % number_printed)
    doc.add_paragraph('')
    doc.add_paragraph('Total fees:  %.2f' % total)
    doc.add_page_break()

    return doc


# In[ ]:

# %load ./helpers/processacc.py
"""Make calculations before printing account."""


def process_acc(grand_total, ep):
    """Do some calculations before printing account.

    Input - grand_total a float and ep an Ordered Dictionary
    """

    # get fees from module depending on fund
    fee_package = FUND_FEES[ep['fund_code']]
    consult_as_float = float(fee_package[0])
    unit = float(fee_package[1])

    # get time info and calculate time fee
    # the fourth digit in the time code gives the number of units
    time_length = int(ep['time'][3])
    time_fee = time_length * unit

    # calculate total_fee, initialise total_fee with consult
    total_fee = consult_as_float

    if ep['upper'] == 'Yes':
        total_fee += (unit * 5)
    if ep['upper'] == 'No' and ep['lower'] == 'Yes':
        total_fee += (unit * 4)
    if ep['seventy'] == 'Yes':
        total_fee += unit
    if ep['asa_3'] == 'Yes':
        total_fee += unit

    # add on time fees
    total_fee = total_fee + (time_length * unit)
    grand_total += total_fee

    return (grand_total, consult_as_float, unit,
            time_fee, total_fee, unit)


# In[ ]:

# %load ./helpers/cleanup.py
"""Close and delete files at end of script."""


def cleanup(datafile, masterfile, summaryfile, printfile):
    """Close and delete files at end of script."""
    input('Press Enter to open accounts summary for printing')
    os.startfile(summaryfile)
    input('Press Enter to open accounts for printing')
    os.startfile(printfile)
    print()
    while True:
        merge = """When finished printing accounts, Press y to save these patients.
Press n to just exit (current batch will stay in place.)
"""
        flag = input(merge)
        if flag in {'y', 'n'}:
            break
    if flag == 'n':
        pass

    elif flag == 'y':
        with open(datafile) as csvhandle:
            with open(masterfile, 'a') as filehandle:
                csvdata = csv.reader(csvhandle)
                csvwriter = csv.writer(filehandle, dialect='excel', lineterminator='\n')
                for p in csvdata:
                    csvwriter.writerow(p)
        try:
            os.remove(datafile)
        except FileNotFoundError:
            pass

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 25, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


def main(biller):
    """Print account in batches of funds with total fees."""

    biller_surmame = biller.split()[-1]
    summaryfile = 'D:\\JOHN TILLET\\episode_data\\accts_summary.txt'
    printfile = 'D:\\JOHN TILLET\\episode_data\\accts.docx'
    datafile = 'D:\\JOHN TILLET\\episode_data\\' + biller_surmame + '.csv'
    masterfile = 'D:\\JOHN TILLET\\episode_data\\csv\\' + biller_surmame + '.csv'
    
    headers = ["date", "name", "address", "dob", "medicare_no", "ref",
               "fund_name", "fund_number", "fund_code", "doctor",
               "upper", "lower", "seventy", "asa_3", "time", "invoice"]
    try:
        os.remove(summaryfile)
    except IOError:
        pass

    try:
        with open(datafile) as csvfile:
            reader = csv.DictReader(csvfile, headers)
            ep_list = [_ for _ in reader]

    except IOError:
        print('No csv file found.')
        sys.exit(1)

    print("Hi - printing Dr {}'s accounts".format(biller_surmame))
    doc = docx.Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Verdana'

    # build a dictionary pat_dict where keys are fund names
    # and values are a list of episodes
    pat_dict = defaultdict(list)

    for episode in ep_list:
        if episode['fund_code'] == 'ahsa':
            fund_id = episode['fund_code'] + '_' + episode['fund_name']  # [:2]
            pat_dict[fund_id].append(episode)
        else:
            fund_id = episode['fund_code']
            pat_dict[fund_id].append(episode)

    # for each fund in pat_dict get the list of episodes ep_list and print
    # them out in equal batches < 20
    
    length = len(ep_list)
    print(length)
    iteration = 0
    printProgressBar(iteration, length, prefix = 'Progress:', suffix = 'Complete', length = 25)
    

    for fu in pat_dict.keys():
        ep_list = pat_dict[fu]
        fund_len = len(ep_list)
        fund_left = fund_len
        start = 0
        if fund_len == 0:
            continue
        while True:
            grand_total = 0.0
            num_p = print_calc(fund_left)
            end = start + num_p
            for np in ep_list[start: end]:
                iteration += 1
                processed = process_acc(grand_total, np)
                grand_total, consult_as_float, unit, time_fee, total_fee, unit = processed
                acc = print_account(np, doc, unit, consult_as_float,
                                    time_fee, total_fee, biller)

            with open(summaryfile, 'a') as file:
                if np['fund_code'] == 'os':
                    file.write('Overseas -- %s\n ' % num_p)
                else:
                    file.write('%s -- %s\n ' % (np['fund_name'], num_p))
                
            acc = print_batch_header(doc, fu, num_p, grand_total)
            fund_left -= num_p
            start += num_p

            printProgressBar(iteration, length, prefix = 'Progress:', suffix = 'Complete', length = 25)
            time.sleep(0.1)
            if start >= fund_len:
                break
    print()
    acc.save(printfile)
    print()
    cleanup(datafile, masterfile, summaryfile, printfile)
if __name__ == '__main__':
    main(False, False, False, biller='Dr S Vuong')
