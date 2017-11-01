"""CLI input for jtbill.py.

By John Tillett
"""
from collections import namedtuple
import datetime
from dateutil.relativedelta import relativedelta
import pprint
import sys

import colorama
from pyautogui import *

import names_and_codes as nc


def get_insurance(asa, anaesthetist, message):
    """Gets insurance details.

    returns insur_code, fund_number, ref, full_fund, message
    returns 'na' if detail not needed
    adds a message to secretaries in certain situations
    (overseas or bulk bill patients)

    asa None indicates no anaesthetic given
    only certain anaesthetists use this feature

    need both full_fund and insur_code variables
     as ahsa funds all have same fees
    ref is medicare ref number
    we get medicare number by scraping episode
    """
    ref = full_fund = insur_code = fund_number = 'na'
    loop_flag = False
    if asa is None or anaesthetist not in nc.BILLING_ANAESTHETISTS:
        return insur_code, fund_number, ref, full_fund, message, loop_flag
    # get full_fund and insur_code
    while True:
        fund_input = input('Fund:   ')
        if fund_input == 'q':
            loop_flag = True
            return insur_code, fund_number, ref, full_fund, message, loop_flag
        if fund_input in nc.FUND_ABREVIATION:
            insur_code = nc.FUND_ABREVIATION[fund_input]
            print('{}'.format(nc.FUND_DIC[insur_code]))
            break
        print('Your choices are.')
        pprint.pprint(nc.FUND_ABREVIATION)

    if insur_code == 'ahsa':
        while True:
            ahsa_fund = input('Fund first two letters or o or h: ')
            if ahsa_fund == 'h':
                pprint.pprint(nc.AHSA_DIC)
            elif ahsa_fund not in nc.AHSA_DIC:
                print('\033[31;1m' + 'TRY AGAIN!')
                continue
            elif ahsa_fund == 'o':
                full_fund = input('Enter Fund Name:  ')
                break
            else:
                full_fund = nc.AHSA_DIC[ahsa_fund]
                print('{}'.format(full_fund))
                break
    elif insur_code == 'os':
        while True:
            os_fund = input('OS patient Fund: ')
            if os_fund in {'h', 'b', 'm', 'n', 'o'}:  # o means not in fund
                break
            print('\033[31;1m' + "Choices: h, b, m, n, o")
        os_insur_code = nc.FUND_ABREVIATION[os_fund]
        full_fund = nc.FUND_DIC[os_insur_code]
    else:
        full_fund = nc.FUND_DIC[insur_code]
    print()
    # get ref and fund_number
    if full_fund == 'Overseas':  # overseas patient not in fund
        ref = fund_number = 'na'
    elif insur_code == 'os':  # overseas patient in fund
        ref = 'na'
        fund_number = input('F Num:  ')
        message = ' JT will bill {}.'.format(full_fund)
    elif insur_code == 'ga':
        ref = input('Episode ID: ')
        print()
        fund_number = input('Approval Number: ')
    elif insur_code == 'va':
        ref = 'na'
        fund_number = input('VA Num: ')
    elif insur_code == 'bb':
        while True:
            ref = input('Ref:    ')
            if ref.isdigit() and len(ref) == 1 and ref != '0':
                break
        fund_number = 'na'
        message += ' JT will bulk bill'
    else:
        while True:
            ref = input('Ref:    ')
            if ref.isdigit() and len(ref) == 1 and ref != '0':
                break
            print('\033[31;1m' + 'TRY AGAIN! Single digit only.')
        print()
        while True:
            fund_number = input('F Num:  ')
            if fund_number[:-1].isdigit():  # med private has a final letter
                break
            print('\033[31;1m' + 'TRY AGAIN!')

    return insur_code, fund_number, ref, full_fund, message, loop_flag


def get_consult(consultant, upper, lower, time_in_theatre, message, loop_flag):
    consult = None
    loop_flag = False

    if consultant == 'Dr A Stoita' or consultant not in nc.PARTNERS:
        pass

    elif consultant in nc.CONSULTERS:
        while True:
            print()
            consult = input('Consult: ')
            if consult == 'q':
                loop_flag = True
                break
            elif consult in {'110', '116'}:
                break
            elif consult == '0%':
                consult = None
                message += ' No consult'
                break
            else:
                print('Dr {} usually charges a 110 or 116'.format(
                    consultant.split()[-1]))
                print('110 is a long consult. '
                      'Can usually only charge once in a year')
                print('116 is a short consult')
                print('If you want no consult for Dr {} type 0%'.format(
                      consultant.split()[-1]))

    elif consultant == 'Dr R Feller':
        print("Dr Feller does 110's on new patients only")
        print("He rarely does 116's")
        while True:
            consult = input('Consult: ')
            if consult == 'q':
                loop_flag = True
                break
            elif consult in {'110', '0', '116'}:
                if consult == '0':
                    consult = None
                break
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print('110 is a long consult.')
                print('116 is a short consult')
                print('0 for no consult')

    elif consultant == 'Dr C Bariol':
        while True:
            print()
            consult = input('Consult: ')
            if consult == 'q':
                loop_flag = True
                break
            elif consult in {'110', '116', '0'}:
                if consult == '0':
                    consult = None
                break
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print('Enter 0 or 110 or 116')

    elif consultant == 'Dr D Williams':
        if int(time_in_theatre) > 30 and lower:
            print()
            print('\033[31;1m' + 'Dr Williams may bill a 110.')
            while True:
                response = input('Confirm ([y]/n) ')
                if response.lower() in {'y', 'n', ''}:
                    break
            if response in {'y', ''}:
                consult = '110'
            else:
                consult = None

    elif consultant == 'Dr C Vickers':
        pu = upper in {'30473-01', '30478-04', '41819-00'}
        pl = lower in {'32090-01', '32093-00', '32084-01', '32087-00'}
        if pu or pl:
            consult = '116'
    return (consult, message, loop_flag)


def get_banding(consultant, lower, message, loop_flag):
    if consultant not in nc.BANDERS or lower is None:
        banding = None
        return banding, message, loop_flag
    while True:
        banding = input('Anal:   ')
        if banding in {'h', ''}:
            print('Select 0 for no anal procedure')
            print('Select a for anal dilatation')
            print('Select b for banding of haemorrhoids')
            print('Select q for quit')
            continue
        if banding not in {'0', 'q', 'a', 'b', ''}:
            print('\033[31;1m' + 'TRY AGAIN! Press enter for help')
            continue
        break
    if banding == 'q':
        loop_flag = True
        return banding, message, loop_flag
    if banding == 'b':
        message += ' Banding haemorrhoids'
    elif banding == 'a':
        message += ' Anal dilatation'
    if banding in {'a', 'b'} and consultant == 'Dr A Wettstein':
        message += ' Bill bilateral pudendal blocks'
    banding = nc.BANDING_DIC[banding]
    return banding, message, loop_flag


def time_calculater(time_in_theatre):
    nowtime = datetime.datetime.now()
    today_str = nowtime.strftime('%Y' + '-' + '%m' + '-' + '%d')

    time_in_theatre = int(time_in_theatre)
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    return (in_formatted, out_formatted, today_str)


def inputer(consultant, anaesthetist):
    colorama.init(autoreset=True)

    while True:
        message = ''
        loop_flag = False
        varix_flag = False
        varix_lot = ''

        print('\033[2J')  # clear screen
        while True:  # get_asa()
            asa = input('ASA:    ')
            if asa == '0':
                sedation_confirm = input('Really no sedation? ([y]/n): ')
                if sedation_confirm == 'n':
                    continue
            if asa in {'0', '1', '2', '3', '4'}:
                asa = nc.ASA_DIC[asa]
                break
            if asa == 'q':
                return 'loop'
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Press 0 for no sedation')
            print('Use asa 1 - 4 only - no extras.')
            print('Press q to go back')

        if asa is None:
            message += ' No Sedation'

        print()
        (insur_code, fund_number, ref, full_fund,
         message, loop_flag) = get_insurance(asa, anaesthetist, message)

        if loop_flag:
            return 'loop'

        print('\033[2J')  # clear screen
        while True:  # get_upper()
            addon_message = ''
            upper = input('Upper:  ')
            if len(upper) >= 2 and upper[-1] == 'x':
                addon_message = ' Upper added on'
                if upper in ('0x', 'cx'):
                    upper = upper[0]
                else:
                    upper = upper[0:2]
            if upper in nc.UPPER_DIC:
                print(nc.UPPER_HELP[upper])
                break
            elif upper == 'q':
                return 'loop'
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print('Here are your options')
                pprint.pprint(nc.UPPER_HELP)
                print('Add an x on end of code if upper was not on the list')

        if upper == 'pv':
            varix_flag = True
            message += ' Bill varix bander'
            varix_lot = input('Bander LOT No: ')
        if upper == 'ha':
            halo = input('90 or ultra?  ')
            message += 'HALO {}'.format(halo)
        if upper == 'c':
            message += ' Upper not done'
            addon_message = ''
        message += addon_message
        upper = nc.UPPER_DIC[upper]

        print()
        while True:  # get_colon()
            colon = input('Lower:  ')
            if colon in nc.COLON_DIC:
                print(nc.COLON_HELP[colon])
                break
            elif colon == 'q':
                return 'loop'
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print('Here are your options')
                pprint.pprint(nc.COLON_HELP)

        if colon == 'cs':       # blue chip does not accept these codes
            message += ' Bill 32088-00'
        if colon == 'csp':
            message += ' Bill 32089-00'
        colon = nc.COLON_DIC[colon]

        if not upper and not colon:
            alert(text='You must enter a procedure!!', title='', button='OK')
            continue

        banding, message, loop_flag = get_banding(
            consultant, colon, message, loop_flag)

        if loop_flag:
            return 'loop'

        print()
        while True:  # get_clips()
            clips = input('Clips: ')
            if clips == 'q':
                return 'loop'
            if clips == '':
                print('Type 0 or number of clips')
                print('No need for stickers or lot numbers')
                continue
            if not clips.isdigit():
                print(colorama.Fore.RED + 'TRY AGAIN!')
                continue
            clips = int(clips)
            if clips != 0:
                message_add = ' clips * {}'.format(clips)
                message += message_add
            break

        print()
        while True:  # get_op_time()
            op_time = input('Time in theatre:   ')
            if op_time == 'q':
                return 'loop'
            if op_time in {'0', '110', '116'} or not op_time.isdigit():
                print('\033[31;1m' + 'TRY AGAIN!')
                print('Enter number of minutes other than 0, 116, or 110')
                continue
            break

        consult, message, loop_flag = get_consult(
            consultant, upper, colon, op_time, message, loop_flag)

        if loop_flag:
            return 'loop'

        (in_formatted, out_formatted, today_for_db) = time_calculater(op_time)

        Indata = namedtuple('Indata', 'asa, upper, colon, banding, consult,'
                            'message, op_time,'
                            'ref, full_fund, insur_code, fund_number,'
                            'clips, varix_flag, varix_lot, in_formatted,'
                            'out_formatted, today_for_db')

        in_data = Indata(asa, upper, colon, banding, consult, message, op_time,
                         ref, full_fund, insur_code, fund_number,
                         clips, varix_flag, varix_lot, in_formatted,
                         out_formatted, today_for_db)

        return in_data


if __name__ == '__main__':
    consultant = sys.argv[1]
    pprint.pprint(inputer(consultant, anaesthetist='Dr J Tillett'), width=20)
