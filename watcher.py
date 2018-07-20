# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:27:05 2018

@author: John
"""
import shelve
import sys
import pyautogui as pya
import pyperclip
import time
import webbrowser
from tkinter import ttk, W, E, N, S, Tk
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, PatternMatchingEventHandler

pya.PAUSE = 0.3
pya.FAILSAFE = True

observer = Observer()
        

class Handler(PatternMatchingEventHandler):
    def on_modified(self, event: FileModifiedEvent):
        global lab, root, but
        lab.configure(text='New Patient!')
        lab.configure(background='red')
#        root.attributes("-topmost", True)
        time.sleep(20)
        root.deiconify()
        root.attributes("-topmost", True)

observer.schedule(event_handler=Handler('*'), path='d:\\john tillet\\episode_data\\csv\\')
observer.daemon=False
observer.start()


class EpFullException(Exception):
    pass


def episode_discharge(intime, outtime, anaesthetist, endoscopist):
    pya.hotkey('alt', 'i')
    pya.typewrite(['enter'] * 4, interval=0.1)
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

    pya.typewrite(endoscopist)
    time.sleep(1)


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

def episode_claim():
    pya.hotkey('alt', 's')
    pya.typewrite(['left'] * 2, interval=0.1)
    for i in range(7):
        pya.hotkey('shift', 'tab')
    pya.press('3')


def episode_theatre(endoscopist, nurse, clips, varix_lot):
    pya.hotkey('alt', 'n')
    pya.typewrite(['left'] * 2, interval=0.1)
    pya.hotkey('shift', 'tab')
    pya.typewrite(endoscopist)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    pya.hotkey('alt', 'n')
    pya.typewrite(['left'] * 2, interval=0.1)
    pya.press('tab')
    pya.typewrite(nurse)
    pya.typewrite(['enter', 'e', 'enter'], interval=0.1)
    if clips != 0 or varix_lot:
        posi = pya.locateCenterOnScreen(
            'prosthesis.png', region= (0, 200, 400, 400))
        box_posi = (posi[0] + 10, posi[1] + 45)
        pya.moveTo(box_posi)
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


def dumper():
    pya.click(100, 500)
    pya.hotkey('alt', 'd')
    mrn = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    print(mrn)
    with shelve.open('d:\\JOHN TILLET\\episode_data\\dumper_data.db') as s:
        try:
            episode = s[mrn]
        except KeyError:
            pya.alert('No data available')
            sys.exit(1)
    episode_discharge(
            episode['in_theatre'], episode['out_theatre'], 
            episode['anaesthetist'], episode['endoscopist'])
    episode_procedures(
            episode['upper'], episode['colon'],
            episode['banding'], episode['asa'])
    episode_theatre(episode['endoscopist'], episode['nurse'],
                    episode['clips'], episode['varix_lot'])
    if (episode['upper'] in {'30490-00'}
            or 'HALO' in episode['message']
            or '32089-00' in episode['message']
            or episode['colon'] in {'32093-00', '32094-00'}
            or episode['banding'] in {'32153-00'}): 
            episode_claim()
    else:
        pya.hotkey('alt', 's')


def runner(*args):
    lab.configure(text='Up to date!')
    lab.configure(background='green')
#    webbrowser.register('chrome', None)
    webbrowser.open('d:\\Nobue\\today_new.html')
#    root.attributes("-topmost", False)
    time.sleep(2)
    root.iconify()
    


root = Tk()
root.title('Billing')
root.geometry('100x160+900+570')
#root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


lab = ttk.Label(mainframe, text="Up to date!")
lab.grid(column=0, row=0, sticky=W)


but = ttk.Button(mainframe, text='Open web page', command=runner)
but.grid(column=0, row=1, sticky=E)

but = ttk.Button(mainframe, text='Dump data', command=dumper)
but.grid(column=0, row=2, sticky=W)


for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)


root.mainloop()