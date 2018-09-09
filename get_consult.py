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
            elif consult in {'l', 's', '0'}:
                if consult == '0':
                    consult = None
                elif consult == 'l':
                    consult = '110'
                elif consult == 's':
                    consult = '117'
                break
            else:
                write_ts(ts)
                print('\033[31;1m' + 'help')
                print('Choices are l, s, 0')
                print()
                print('l is an initial or long consult. ')
                print('s is a short follow up')
                print()
                ans = input('Hit Enter to retry'
                            ' or q to return to the main menu:')
                if ans == 'q':
                    raise LoopException

    ts += '\n' + 'Consult:   {}'.format(str(consult))
    return (consult, message, ts)
