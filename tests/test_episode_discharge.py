from os import time
import pyautogui as pya
import pyperclip


class EpFullException(Exception):
    pass


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
                 '{}. Choose the correct one'.format(endoscopist, doctor),
            title='Confirm Endoscopist',
            buttons=['{}'.format(endoscopist), '{}'.format(doctor)])

        pya.typewrite(response)
