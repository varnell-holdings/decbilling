"""CLI input for docbill.py."""
import datetime
from dateutil.relativedelta import relativedelta
import pprint
import time

import colorama

import names_and_codes as nc


class LoopException(Exception):
    pass


def clear():
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left


def write_ts(ts):
    clear()
    print(ts)
    print('\033[13H')

def get_mrn():
    mrn = input('MRN: ')
    return mrn


def get_asa(message, ts):
    while True:
        write_ts(ts)
        asa = input('ASA or 0 for no sedation:    ')
        if asa == 'q':
            raise LoopException
        elif asa == '0':
            print('Really no sedation?')
            print('Press n to confirm no sedation')
            print('Press Enter to try again: ')
            no_sedation_confirm = input()
            if no_sedation_confirm == 'n':
                message += ' No Sedation'
                break
        elif asa in {'1', '2', '3', '4'}:
            break
        else:
            write_ts(ts)
            print('\033[31;1m' + 'help')
            print('Press 0 for no sedation')
            print('Use asa 1 - 4 only - no extras.')
            print('Press q to go back to the main menu')
            print('If not working try pressing numlock key')
            ans = input('Press Enter to try again: ')
            if ans == 'q':
                raise LoopException
    ts += '\n' + nc.ASA_HELP[asa]
    asa = nc.ASA_DIC[asa]
    return asa, message, ts


def get_insurance(asa, anaesthetist, ts):
    """Gets insur_code for jrt account program."""
    insur_code = fund = ref = fund_number = ''
    if asa is None or anaesthetist != 'Dr J Tillett':
        return insur_code, fund , ref, fund_number
    while True:
        write_ts(ts)
        fund_input = input('Fund:   ').lower()
        if fund_input == 'q':
            raise LoopException
        elif fund_input in nc.FUND_ABREVIATION:
            insur_code = nc.FUND_ABREVIATION[fund_input]
            print('{}'.format(nc.FUND_DIC[insur_code]))
            break
        else:
            write_ts(ts)
            print('Your choices are.')
            pprint.pprint(nc.FUND_ABREVIATION)
            ans = input('Press Enter to try again: ')
            if ans == 'q':
                raise LoopException

    if insur_code == 'ga':
        ref = input('Episode ID: ')
        fund_number = input('Approval Number: ')
        fund = 'Garrison Health'

    elif insur_code == 'ahsa':
        print('Enter 2 letter ahsa code')
        print('or Enter if not in list: ')
        ahsa_abbr = input().lower()
        if ahsa_abbr not in nc.AHSA_DIC.keys():
            fund = input("Enter fund name: ")
        else:
            fund = nc.AHSA_DIC[ahsa_abbr]

    elif insur_code == 'os':
        paying = input('Paying today? y/n ').lower()
        if paying == 'y':
            fund = 'Overseas'

    else:
        fund = nc.FUND_DIC[insur_code]
            
    
    return insur_code, fund, ref, fund_number


def get_upper(message, ts):
    varix_flag = False
    varix_lot = ''
    while True:
        write_ts(ts)
        upper = input('Upper:  ').lower()
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
            print('\033[31;1m' + 'help')
            print('Hit Enter to retry or q to return to the main menu:')
            ans = input('Press h to see your options: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.UPPER_HELP)
                print()
                print('Add "a" on end of code if upper was added on')
                print('Type c to indicate upper cancelled')
                print()
                ans = input('Hit Enter to retry'
                            ' or q to return to the main menu:')
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
    ts += '\n' + nc.UPPER_HELP[upper]
    upper = nc.UPPER_DIC[upper]
    return upper, varix_flag, varix_lot, message, ts


def get_colon(upper, message, ts):
    while True:
        write_ts(ts)
        colon = input('Lower:  ').lower()
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
            print('\033[31;1m' + 'help')
            print('Press Enter to try again')
            ans = input('Press h to see your options: ')
            if ans == 'h':
                clear()
                pprint.pprint(nc.COLON_HELP)
                print()
                ans = input('Hit Enter to retry'
                            ' or q to return to the main menu:')
                if ans == 'q':
                    raise LoopException
    ts += '\n' + nc.COLON_HELP[colon]
    colon = nc.COLON_DIC[colon]
    return colon, message, ts


def get_banding(consultant, lower, message, ts):
    if consultant not in nc.BANDERS or lower is None:
        banding = '0'
        ts += '\n' + nc.BANDING_HELP[banding]
        banding = nc.BANDING_DIC[banding]
        return banding, message, ts

    while True:
        write_ts(ts)
        banding = input('Anal procedure:   ').lower()
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
            write_ts(ts)
            print('\033[31;1m' + 'help')
            print('Select 0 for no anal procedure')
            print('Select a for anal dilatation')
            print('Select b for banding of haemorrhoids')
            ans = input('Hit Enter to retry or q to return to the main menu:')
            if ans == 'q':
                raise LoopException
    ts += '\n' + nc.BANDING_HELP[banding]
    banding = nc.BANDING_DIC[banding]
    return banding, message, ts


def get_clips(message, ts):
    while True:
        write_ts(ts)
        clips = input('Clips: ')
        if clips == 'q':
            raise LoopException
        if clips.isdigit():
            clips = int(clips)
            if clips != 0:
                message += ' clips * {}'.format(clips)
            break
        else:
            write_ts(ts)
            print('\033[31;1m' + 'help')
            print('Type 0 or number of clips')
            print('No need for stickers or lot numbers')
            ans = input('Hit Enter to retry or q to return to the main menu:')
            if ans == 'q':
                raise LoopException
    ts += '\n' + '{} clips.'.format(clips)
    return clips, message, ts


def get_op_time(ts):
    while True:
        write_ts(ts)
        op_time = input('Time in theatre:   ')
        if op_time == 'q':
            raise LoopException
        elif op_time.isdigit() and op_time not in {'0', '110', '116'}:
            op_time = int(op_time)
            break
        else:
            write_ts(ts)
            print('\033[31;1m' + 'help')
            print('Enter minutes in theatre other than 0, 116, or 110')
            ans = input('Hit Enter to retry or q to return to the main menu:')
            if ans == 'q':
                raise LoopException
    ts += '\n' + 'Time in Theatre was {} minutes.'.format(str(op_time))
    return op_time, ts


def get_consult(consultant, upper, lower, time_in_theatre, message, ts):
    if consultant in {'Dr A Stoita', 'Dr C Bariol'} or consultant in nc.VMOS:
        consult = None

    elif consultant in nc.CONSULTERS:
        while True:
            write_ts(ts)
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
                write_ts(ts)
                print('\033[31;1m' + 'help')
                print('Choices are 110, 117, 116, 0')
                print()
                print('110 is an initial consult. ')
                print('Can usually only charge a 110 once in a year')
                print('117 is a complex follow up')
                print('116 is a short follow up')
                print('Cannot charge 116 if patient has had a colonoscopy')
                print()
                ans = input('Hit Enter to retry'
                            ' or q to return to the main menu:')
                if ans == 'q':
                    raise LoopException

#    elif consultant in {'Dr D Williams', 'Dr R Feller'}:
#        longcol = time_in_theatre > 30 and lower is not None
#        if longcol and consultant == 'Dr D Williams':
#            write_ts(ts)
#            print('Dr Williams may bill a 110.')
#        elif consultant == 'Dr R Feller':
#            write_ts(ts)
#            print("Dr Feller does 110's on new patients only")
#        while True:
#            consult = input('Consult: ')
#            if consult == 'q':
#                raise LoopException
#            elif consult in {'110', '0'}:
#                if consult == '0':
#                    consult = None
#                break
#            else:
#                write_ts(ts)
#                print('\033[31;1m' + 'help')
#                print('110 for a long consult.')
#                print('0 for no consult')
#                ans = input('Hit Enter to retry'
#                            ' or q to return to the main menu: ')
#                if ans == 'q':
#                    raise LoopException

#    elif consultant == 'Dr C Vickers':
#        pu = upper in {'30473-01', '30478-04', '41819-00'}
#        pl = lower in {'32090-01', '32093-00', '32084-01', '32087-00'}
#        if pu or pl:
#            consult = '117'
#        else:
#            consult = None

    ts += '\n' + 'Consult:   {}'.format(str(consult))
    return (consult, message, ts)


def confirm(message, ts):
    while True:
        write_ts(ts)
        print('Hit Enter to confirm the above')
        print('Type q to start again')
        print('Type m to add a message')
        ans = input()
        if ans == 'q':
            raise LoopException
        elif ans == 'm':
            added = input()
            message += ' ' + added
            ts += '\n' + 'Message: {}'.format(message)
        else:
            break
    return message


def in_and_out_calculater(time_in_theatre):
    time_in_theatre = int(time_in_theatre)
    nowtime = datetime.datetime.now()
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    return (in_formatted, out_formatted)


def inputer(endoscopist, consultant, anaesthetist):
    colorama.init(autoreset=True)

    message = ''
    ts = 'Endoscopist:  {}'.format(endoscopist)
    try:
#        if anaesthetist == 'Dr J Tillett':
#            mrn = get_mrn()
        
        (asa, message, ts) = get_asa(message, ts)

        insur_code, fund, ref, fund_number = get_insurance(
            asa, anaesthetist, ts)

        (upper, varix_flag, varix_lot, message, ts) = get_upper(message, ts)

        (colon, message, ts) = get_colon(upper, message, ts)

        (banding, message, ts) = get_banding(consultant, colon, message, ts)

        (clips, message, ts) = get_clips(message, ts)

        op_time, ts = get_op_time(ts)

        (consult, message, ts) = get_consult(
            consultant, upper, colon, op_time, message, ts)

        message = confirm(message, ts)
    except LoopException:
        raise

    (in_theatre, out_theatre) = in_and_out_calculater(op_time)

    in_data = (asa, upper, colon, banding, consult, message, op_time,
               insur_code, fund, ref, fund_number, clips, varix_flag,
               varix_lot, in_theatre, out_theatre)

    return in_data


if __name__ == '__main__':
    print(inputer(endoscopist='Dr A Wettstein', consultant='Dr A Wettstein',
                  anaesthetist='Dr J Tillett'))
