"""CLI input for docbill.py."""
from collections import namedtuple
import datetime
from dateutil.relativedelta import relativedelta
import pprint
import sys

import colorama
import pyautogui as pya

import names_and_codes as nc


class LoopException(Exception):
    pass


Indata = namedtuple('Indata', 'asa, upper, colon, banding, consult,'
                    'message, op_time,'
                    'ref, full_fund, insur_code, fund_number,'
                    'clips, varix_flag, varix_lot, in_formatted,'
                    'out_formatted')


def get_asa(message):
    print('\033[2J')  # clear screen
    while True:
        asa = input('ASA:    ')
        if asa == 'q':
            raise LoopException
        if asa == '0':
            sedation_confirm = input('Really no sedation? ([y]/n): ')
            if sedation_confirm == 'n':
                continue
        if asa in {'0', '1', '2', '3', '4'}:
            asa = nc.ASA_DIC[asa]
            if asa is None:
                message += ' No Sedation'
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Press 0 for no sedation')
            print('Use asa 1 - 4 only - no extras.')
            print('Press q to go back')
    return asa, message


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
    if asa is None or anaesthetist not in nc.BILLING_ANAESTHETISTS:
        return insur_code, fund_number, ref, full_fund, message
    # get full_fund and insur_code
    while True:
        print()
        fund_input = input('Fund:   ')
        if fund_input == 'q':
            raise LoopException
        elif fund_input in nc.FUND_ABREVIATION:
            insur_code = nc.FUND_ABREVIATION[fund_input]
            print('{}'.format(nc.FUND_DIC[insur_code]))
            break
        else:
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
    if insur_code == 'os' and full_fund == 'Overseas':  # os - not in fund
        ref = fund_number = 'na'
    elif insur_code == 'os' and full_fund != 'Overseas':  # os - in fund
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

    return insur_code, fund_number, ref, full_fund, message


def get_upper(message):
    varix_flag = False
    varix_lot = ''
    print('\033[2J')  # clear screen
    while True:
        upper = input('Upper:  ')
        if upper == 'q':
            raise LoopException
        elif upper in {'c', '0c'}:
            message += ' pe cancelled'
            break
        elif len(upper) == 3 and upper[-1] == 'a':
            upper = upper[:2]
            if upper in nc.UPPER_DIC:
                print(nc.UPPER_HELP[upper])
                message += ' pe added on'
                break
        elif upper in nc.UPPER_DIC:
            print(nc.UPPER_HELP[upper])
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Here are your options')
            pprint.pprint(nc.UPPER_HELP)
            print('Add "a" on end of code if upper was not on the list')
            print('Type c or 0c to indicate upper cancelled')

    if upper == 'pv':
        varix_flag = True
        message += ' Bill varix bander'
        varix_lot = input('Bander LOT No: ')
    if upper == 'ha':
        while True:
            halo = input('[90] or [u]ltra?  ')
            if halo in {'90', 'u'}:
                if halo == 'u':
                    halo = 'ultra'
                break
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print("Type either '90' or 'u' for ultra")
        message += 'HALO {}'.format(halo)
    upper = nc.UPPER_DIC[upper]
    return upper, varix_flag, varix_lot, message


def get_colon(upper, message):
    while True:
        print()
        colon = input('Lower:  ')
        if colon == 'q':
            raise LoopException
        elif colon in nc.COLON_DIC:
            print(nc.COLON_HELP[colon])
            if colon == 'cs':       # blue chip does not accept these codes
                message += ' Bill 32088-00'
            if colon == 'csp':
                message += ' Bill 32089-00'
            colon = nc.COLON_DIC[colon]
            if not upper and not colon:
                print('You must enter either a pe or colon!')
                print('If you left out the pe press q to restart')
                continue
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Here are your options')
            pprint.pprint(nc.COLON_HELP)
    return colon, message


def get_banding(consultant, lower, message):
    if consultant not in nc.BANDERS or lower is None:
        banding = None
        return banding, message
    while True:
        print()
        banding = input('Anal:   ')
        if banding == 'q':
            raise LoopException
        elif banding == '0':
            banding = None
            break
        elif banding == 'b':
            banding = nc.BANDING_DIC[banding]
            message += ' Banding haemorrhoids'
            if consultant == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks'
            break
        elif banding == 'a':
            banding = nc.BANDING_DIC[banding]
            message += ' Anal dilatation'
            if consultant == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks'
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Select 0 for no anal procedure')
            print('Select a for anal dilatation')
            print('Select b for banding of haemorrhoids')
            print('Select q for quit')
    return banding, message


def get_clips(message):
    while True:
        print()
        clips = input('Clips: ')
        if clips == 'q':
            raise LoopException
        if clips.isdigit():
            clips = int(clips)
            if clips != 0:
                message += ' clips * {}'.format(clips)
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Type 0 or number of clips')
            print('No need for stickers or lot numbers')
            print('Type q to restart')
    return clips, message


def get_op_time():
    print()
    while True:
        op_time = input('Time in theatre:   ')
        if op_time == 'q':
            raise LoopException
        elif op_time.isdigit() and op_time not in {'0', '110', '116'}:
            op_time = int(op_time)
            break
        else:
            print('\033[31;1m' + 'TRY AGAIN!')
            print('Enter minutes in theatre other than 0, 116, or 110')
    return op_time


def get_consult(consultant, upper, lower, time_in_theatre, message):
    print()
    if consultant not in nc.CONSULTERS:
        consult = None

    elif consultant in nc.CONSULTERS:
        while True:
            consult = input('Consult: ')
            if consult == 'q':
                raise LoopException
            elif consult in {'110','116', '117', '0'}:
                if consult == '0':
                    consult = None
                break
#            else:
#                print('Dr {} sometimes charges a 110'.format(
#                    consultant.split()[-1]))
#                print('110 is an initial consult. '
#                      'Can usually only charge once in a year')
#                print('Cannot charge 116 if patient has had a colonoscopy')
#                print('Type 0 for no consult.')

#    elif consultant in nc.CONSULTERS and lower is None:
#        while True:
#            consult = input('Consult: ')
#            if consult == 'q':
#                raise LoopException
#            elif consult in {'110', '116', '0'}:
#                if consult == '0':
#                    consult = None
#                break
#            else:
#                print('Dr {} sometimes charges a 110'.format(
#                    consultant.split()[-1]))
#                print('110 is an initial consult. '
#                      'Can usually only charge once in a year')
#                print('116 is a subsequent consult')
#                print('Type 0 for no consult.')
    return (consult, message)


def in_and_out_calculater(time_in_theatre):
    time_in_theatre = int(time_in_theatre)
    nowtime = datetime.datetime.now()
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    return (in_formatted, out_formatted)


def inputer(consultant, anaesthetist):
    colorama.init(autoreset=True)

    message = ''

    try:
        asa, message = get_asa(message)

        insur_code, fund_number, ref, full_fund, message = get_insurance(
            asa, anaesthetist, message)

        upper, varix_flag, varix_lot, message = get_upper(message)

        colon, message = get_colon(upper, message)

        banding, message = get_banding(consultant, colon, message)

        clips, message = get_clips(message)

        op_time = get_op_time()

        consult, message = get_consult(
            consultant, upper, colon, op_time, message)
    except LoopException:
        raise

    (in_theatre, out_theatre) = in_and_out_calculater(op_time)

    in_data = Indata(asa, upper, colon, banding, consult, message, op_time,
                     ref, full_fund, insur_code, fund_number,
                     clips, varix_flag, varix_lot, in_theatre, out_theatre)

    return in_data


if __name__ == '__main__':
    consultant = sys.argv[1]
    print(inputer(consultant, anaesthetist='Dr J Tillett'))
