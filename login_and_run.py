import names_and_codes as nc
from bill import bill


def get_anaesthetist():
    while True:
        initials = input('Anaesthetist:  ').lower()
        if initials in nc.ANAESTHETISTS:
            anaesthetist = nc.ANAESTHETISTS[initials]
            break
    return anaesthetist


def get_endoscopist():
    while True:
        initials = input('Endoscopist:  ').lower()
        if initials in nc.DOC_DIC:
            doctor = nc.DOC_DIC[initials]
            break
    return doctor


def get_nurse():
    while True:
        nurse = input('Nurse:  ')
        if nurse == 'js':
            nurse = 'jacqueline smith'
        if nurse == 'jg':
            nurse = 'Jacinta Goldenberg'
        if nurse in {'jacqueline smith', 'Jacinta Goldenberg', 'be', 'ro',
                     'yi', 'we', 'ja', 'la', 'ma', 'no', 'su', 'pa', 'ch'}:
            break
    return nurse


def login_and_run():
    while True:
        anaesthetist = get_anaesthetist()

        print ('Welcome Dr {}!'.format(
            anaesthetist.split()[-1]))

        print()

        doctor = get_endoscopist()

        print()

        nurse = get_nurse()

        while True:
            choice = bill(anaesthetist, doctor, nurse)
            if choice == 1:
                break
