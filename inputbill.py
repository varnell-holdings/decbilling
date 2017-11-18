"""CLI input for docbill.py."""
from collections import namedtuple
import datetime
from dateutil.relativedelta import relativedelta
import pprint
import sys
import time

import colorama

import names_and_codes as nc


class LoopException(Exception):
    pass


Indata = namedtuple('Indata', 'asa, upper, colon, banding, consult,'
                    'message, op_time,'
                    'ref, full_fund, insur_code, fund_number,'
                    'clips, varix_flag, varix_lot, in_formatted,'
                    'out_formatted')


def clear():
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left
    print('\n\n\n')


def get_asa(message):
    while True:
        clear()
        asa = input('ASA or 0 for no sedation:    ')
        if asa == 'q':
            raise LoopException
        elif asa == '0':
            clear()
            print('Really no sedation?')
            print('Press n to confirm no sedation')
            no_sedation_confirm = input('Press Enter to try again: ')
            if no_sedation_confirm == 'n':
                message += ' No Sedation'
                break
        elif asa in {'1', '2', '3', '4'}:
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Press 0 for no sedation')
            print('Use asa 1 - 4 only - no extras.')
            print('Press q to go back')
            print('If not working try pressing numlock key')
            ans = input('Press Enter to try again: ')
            if ans == 'q':
                raise LoopException
    clear()
    print(nc.ASA_HELP[asa])
    asa = nc.ASA_DIC[asa]
    time.sleep(1)
    return asa, message


def get_insurance(asa, anaesthetist):
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
        return (insur_code, fund_number, ref, full_fund)
    # get full_fund and insur_code
    while True:
        print('\033[2J')  # clear screen
        print('\033[1;1H')  # move to top left
        print('\n\n\n')
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
    elif insur_code == 'ga':
        ref = input('Episode ID: ')
        print()
        fund_number = input('Approval Number: ')
    elif insur_code == 'va':
        ref = 'na'
        fund_number = input('VA Num: ')
    elif insur_code == 'p' or insur_code == 'u':
        while True:
            ref = input('Ref:    ')
            if ref.isdigit() and len(ref) == 1 and ref != '0':
                break
        fund_number = 'na'
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
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left
    return (insur_code, fund_number, ref, full_fund)


def get_upper(message):
    varix_flag = False
    varix_lot = ''
    while True:
        clear()
        upper = input('Upper:  ')
        if upper == 'q':
            raise LoopException
        elif upper in {'c', 'pec'}:
            message += ' pe cancelled'
            break
        elif len(upper) == 3 and upper[-1] == 'a':
            upper = upper[:2]
            if upper in nc.UPPER_DIC:
                message += ' pe added on'
                break
        elif upper in nc.UPPER_DIC:
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Press Enter to try again')
            ans = input('Press h to see your options: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.UPPER_HELP)
                print()
                print('Add "a" on end of code if upper was added on')
                print('Type c to indicate upper cancelled')
                print()
                ans = input('Hit Enter to retry or q to restart this patient:')
                if ans == 'q':
                    raise LoopException

    if upper == 'pv':
        varix_flag = True
        message += ' Bill varix bander'
        varix_lot = input('Bander LOT No: ')
    if upper in {'ha', 'ph'}:
        while True:
            halo = input('[90] or [u]ltra?  ')
            if halo in {'90', 'u'}:
                if halo == 'u':
                    halo = 'ultra'
                break
            else:
                print('\033[31;1m' + 'TRY AGAIN!')
                print("Type either '90' or 'u' for ultra")
        message += ' HALO {}'.format(halo)
    clear()
    print(nc.UPPER_HELP[upper])
    upper = nc.UPPER_DIC[upper]
    time.sleep(1)
    return upper, varix_flag, varix_lot, message


def get_colon(upper, message):
    while True:
        clear()
        colon = input('Lower:  ')
        if colon == 'q':
            raise LoopException
        elif colon in nc.COLON_DIC:
            if colon == 'cs':       # blue chip does not accept these codes
                message += ' Bill 32088-00'
            elif colon == 'csp':
                message += ' Bill 32089-00'
            elif upper is None and colon in {'0', 'c'}:
                print('\033[31;1m' + 'You must enter either a pe or colon!')
                print('If you left out the upper press q to restart')
                time.sleep(2)
                continue
            elif colon == 'c':
                message += ' Colon cancelled'
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Press Enter to try again')
            ans = input('Press h to see your options: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.COLON_HELP)
                print()
                ans = input('Hit Enter to retry or q to restart this patient:')
                if ans == 'q':
                    raise LoopException
    clear()
    print(nc.COLON_HELP[colon])
    colon = nc.COLON_DIC[colon]
    time.sleep(1)
    return colon, message


def get_banding(consultant, lower, message):
    if consultant not in nc.BANDERS or lower is None:
        banding = None
        return banding, message

    while True:
        clear()
        banding = input('Anal procedure:   ')
        if banding == 'q':
            raise LoopException
        elif banding == '0':
            break
        elif banding == 'b':
            message += ' Banding haemorrhoids'
            if consultant == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks'
            break
        elif banding == 'a':
            message += ' Anal dilatation'
            if consultant == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks'
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Select 0 for no anal procedure')
            print('Select a for anal dilatation')
            print('Select b for banding of haemorrhoids')
            ans = input('Hit Enter to retry or q to restart this patient:')
            if ans == 'q':
                raise LoopException
    clear()
    print(nc.BANDING_HELP[banding])
    time.sleep(1)
    banding = nc.BANDING_DIC[banding]
    return banding, message


def get_clips(message):
    while True:
        clear()
        clips = input('Clips: ')
        if clips == 'q':
            raise LoopException
        if clips.isdigit():
            clips = int(clips)
            if clips != 0:
                message += ' clips * {}'.format(clips)
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Type 0 or number of clips')
            print('No need for stickers or lot numbers')
            ans = input('Hit Enter to retry or q to restart this patient:')
            if ans == 'q':
                raise LoopException
    clear()
    print('{} clips.'.format(clips))
    time.sleep(1)
    return clips, message


def get_op_time():
    while True:
        clear()
        op_time = input('Time in theatre:   ')
        if op_time == 'q':
            raise LoopException
        elif op_time.isdigit() and op_time not in {'0', '110', '116'}:
            op_time = int(op_time)
            break
        else:
            clear()
            print('\033[31;1m' + 'help')
            print('Enter minutes in theatre other than 0, 116, or 110')
            ans = input('Hit Enter to retry or q to restart this patient:')
            if ans == 'q':
                raise LoopException
    clear()
    print('Time in Theatre was {} minutes.'.format(op_time))
    time.sleep(1)
    return op_time


def get_consult(consultant, upper, lower, time_in_theatre, message):
    if consultant in {'Dr A Stoita', 'Dr C Bariol'} or consultant in nc.VMOS:
        consult = None

    elif consultant in nc.CONSULTERS:
        while True:
            clear()
            print('Ask Dr {} what consult to bill.'.format(
                consultant.split()[-1]))
            consult = input('Consult: ')
            if consult == 'q':
                raise LoopException
            elif consult in {'110', '116', '117', '0'}:
                if consult == '0':
                    consult = None
                break
            else:
                clear()
                print('\033[31;1m' + 'help')
                print('Choices are 110, 117, 116, 0')
                print()
                print('110 is an initial consult. ')
                print('Can usually only charge a 110 once in a year')
                print('117 is a complex follow up')
                print('116 is a short follow up')
                print('Cannot charge 116 if patient has had a colonoscopy')
                print()
                ans = input('Hit Enter to retry or q to restart this patient:')
                if ans == 'q':
                    raise LoopException

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
    elif consultant == 'Dr D Williams':
        if int(time_in_theatre) > 30 and lower is not None:
            clear()
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
            consult = '117'
        else:
            consult = None

    elif consultant == 'Dr R Feller':
        clear()
        print("Dr Feller does 110's on new patients only")
        while True:
            consult = input('Consult: ')
            if consult == 'q':
                raise LoopException
            elif consult in {'110', '0'}:
                if consult == '0':
                    consult = None
                break
            else:
                clear()
                print('\033[31;1m' + 'help')
                print('110 for a long consult.')
                print('0 for no consult')
                ans = input('Hit Enter to retry or q to restart this patient:')
                if ans == 'q':
                    raise LoopException
    clear()
    if consult is None:
        print('Dr {} is not billing a consultation'.format(
            consultant.split()[-1]))
    else:
        print('Dr {} is billing a {}'.format(
            consultant.split()[-1], consult))
    time.sleep(1)
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
        (asa, message) = get_asa(message)

        (insur_code, fund_number, ref, full_fund) = get_insurance(
            asa, anaesthetist)

        (upper, varix_flag, varix_lot, message) = get_upper(message)

        (colon, message) = get_colon(upper, message)

        (banding, message) = get_banding(consultant, colon, message)

        (clips, message) = get_clips(message)

        op_time = get_op_time()

        (consult, message) = get_consult(
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
