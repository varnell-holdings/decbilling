#!/usr/bin/env python2.7
'''Python 2.7.2 '''

import csv, os, webbrowser
from datetime import *
from dateutil.relativedelta import *
from dateutil.parser import *

# fund_fees is a dictionary with the key
# being the health fund ID and the data being a list with the consult fee
# and the unit fee for each fund.
# also import medicare codes
from module.fundfees import fund_fees, pe_code, col_code, age_code, sick_code

# these html codes for the account
from module.templates import base_html, table_html, terminal_html, batch_header_html

try:
    csvfile = open('/Users/jtair/Dropbox/DEC/new_billing_program/month_patients.csv', 'r')
except IOError:
    print('Oops. No file.')

patlist = csv.reader(csvfile)
newpatlist = [_ for _ in patlist]


for health_fund in ['HCF', 'BUPA', 'MPL', 'NIB', 'AHSA', 'AHM', 'AMA']:
    number_to_print = 0         # output the number of accounts printed as a check
    batch_claim = 0.0
    for row in newpatlist:
        if row[13] == health_fund:
            # extract data from csv file into variables - these are strings
            patient = row[0]
            address = row [1]
            dob = row[2]
            fund = row[3]
            fund_number = row[4]
            mcn = row[5]
            ref = row[6]
            ep_date = row[7]
            doctor = row[8]
            endo = row[9]  #expect Yes/No
            colon = row[10]
            sick = row[11]
            time = row[12]
            fund_details = fund + '   ' + fund_number
            medicare_details = 'Medicare No:  ' + mcn + '   Ref: ' + ref
            # Age calculation
            dob_parsed = parse(dob)
            ep_date_parsed = parse(ep_date)
            age_sep = relativedelta(ep_date_parsed, dob_parsed)
            if age_sep.years >= 70:
                age = 'Yes'
            else:
                age = 'No'


            # get fees from module depending on fund
            fee_package = fund_fees[health_fund]
            consult = fee_package[0]
            consult_as_float = float(fee_package[0])
            unit = float(fee_package[1])

            # get time info and calculate time fee
            # the fourth digit in the time code gives the number of units
            time_length = int(time[3])
            time_fee = time_length * unit

            # calculate total_fee, initialise total_fee and add on consult
            total_fee = consult_as_float

            if endo == 'Yes':
                total_fee += (unit * 5)
            if endo == 'No' and colon == 'Yes':
                total_fee += (unit * 4)
            if age == 'Yes':
                total_fee += unit
            if sick == 'Yes':
                total_fee += unit

            # add on time fees
            total_fee = total_fee + (time_length * unit)

            # put data (including consult fee) into base_html code
            output_html = base_html % (patient,address,dob, fund_details,medicare_details, ep_date, doctor, consult)
            # now append lines to the Fees Table at the bottom of the account
            if endo == 'Yes':
                output_html = output_html + table_html % (pe_code, 5 * unit)
                if colon == 'Yes':
                    output_html = output_html + table_html % (col_code, 0.00)
            if endo == 'No' and colon == 'Yes':
                output_html = output_html + table_html % (col_code, 4 * unit)
            if age == 'Yes':
                output_html = output_html + table_html % (age_code, unit)
            if sick == 'Yes':
                output_html = output_html + table_html % (sick_code, unit)

            # add on time fee
            output_html = output_html + table_html % (time, time_fee)
            # add on total fee
            output_html = output_html + table_html % ('Total Fee', total_fee)
            # add on terminal html code
            output_html = output_html + terminal_html

            # print output_html to file
            with open('/Users/jtair/Documents/Invoices/'
                      + row[0] + '.html', 'w') as ep_file:
                ep_file.write(output_html)

            number_to_print += 1
            batch_claim += total_fee
            if number_to_print == 2:
                print('You\'ve reached 20 accounts for %s' % health_fund)
                print('Claim amount for these accounts is  $%.2f' % batch_claim)
                header_file = batch_header_html % (health_fund, number_to_print, batch_claim)
                with open('/Users/jtair/Documents/Invoices/'
                      + health_fund +'_header' + '.html', 'w') as head_file:
                    head_file.write(header_file)

                print('Print them out with fn-f2')

                number_to_print = 0
                batch_claim = 0.0
                pauser = input('Hit Enter when ready to print next fund batch.')
                if pauser == '':
                    continue


    # final print out of number of accounts

    print('Number of {} accounts created is {}'.format(health_fund, number_to_print))
    print('Value of {} accounts created is ${}'.format(health_fund, batch_claim))
    if number_to_print != 0:
        header_file = batch_header_html % (health_fund, number_to_print, batch_claim)
        with open('/Users/jtair/Documents/Invoices/'
              + health_fund +'_header' + '.html', 'w') as head_file:
            head_file.write(header_file)
    print('Hit fn-f2 to print out.')
    pauser = input('Hit Enter when ready to print next fund batch.')
    if pauser == '':
        continue
csvfile.close()
