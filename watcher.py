# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:27:05 2018

@author: John
"""
from collections import deque
import csv
import datetime
import os
import shelve
import sys
import pyautogui as pya
import pyperclip
import time
import webbrowser
from tkinter import ttk, W, E, N, S, Tk
from jinja2 import Environment, FileSystemLoader
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, PatternMatchingEventHandler

pya.PAUSE = 0.3
pya.FAILSAFE = True

coords = {'John' : ((100, 155), (100, 360)),
          'John2' : ((100, 155), (100, 360)),
          'Recept1' : ((100, 160), (100, 350)),
          'Recept2' : ((100, 190), (100, 378)),
          'Recept3' : ((100, 165), (100, 352)),
          'Recept5' : ((100, 160), (100, 350)),
          'Admin3': ((100, 163), (100, 345)),
	  'Accounts': ((100, 165), (100,352))}

observer = Observer()
        

class Handler(PatternMatchingEventHandler):
    def on_modified(self, event: FileModifiedEvent):
        global lab, root, but
        lab.configure(text='New Patient!')
        lab.configure(background='red')
#        root.attributes("-topmost", True)
        time.sleep(10)
        root.deiconify()
        root.attributes("-topmost", True)

observer.schedule(event_handler=Handler('*'), path='d:\\john tillet\\episode_data\\watched\\')
observer.daemon=False
observer.start()


class EpFullException(Exception):
    pass


def episode_discharge(intime, outtime, anaesthetist, endoscopist):
    pya.hotkey('alt', 'i')
    pya.typewrite(['enter'] * 4)
    pya.typewrite(intime)
    pya.typewrite(['enter'] * 2)
    pya.typewrite(outtime)
    pya.typewrite(['enter'] * 3)
    if anaesthetist != 'locum':
        pya.typewrite(['tab'] * 6)
        pya.typewrite(anaesthetist)
        pya.typewrite('\n')
    else:
        pya.typewrite(['tab'] * 7)

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
    pya.typewrite(['tab'] * 6)
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
    pya.typewrite(['tab'] * 2)
    if anal and anal_flag is False:  # third line
        pya.typewrite(anal + '\n')
        pya.press('enter')
    else:
        if asa:
            pya.typewrite(asa + '\n')
            pya.press('enter')
        return
    pya.typewrite(['tab'] * 2)
    if asa:  # fourth line
        pya.typewrite(asa + '\n')
        pya.press('enter')
    return

def episode_claim():
    pya.hotkey('alt', 's')
    pya.typewrite(['left'] * 2)
    for i in range(7):
        pya.hotkey('shift', 'tab')
    pya.press('3')


def episode_theatre(endoscopist, nurse, clips, varix_lot):
    pya.hotkey('alt', 'n')
    pya.typewrite(['left'] * 2)
#    if not pya.pixelMatchesColor(1100, 100, (240, 240, 240)):
#        pya.hotkey('ctrl', 'f1')
#        time.sleep(0.5)
    user = os.getenv('USERNAME')
    doc_coord = coords.get(user, ((100, 155), (100, 360)))[0]

    pya.moveTo(doc_coord)
    pya.click()
    pya.press('tab')
    doc_test = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    doc_test = pyperclip.paste()
    if doc_test == 'Endoscopist':
        pya.press('tab')
        pya.typewrite(['enter'] * 2)
        pya.moveRel(400, 0)
        pya.click()
        pya.typewrite(['tab'] * 2)
        pya.typewrite(['enter'] * 2)

    pya.moveTo(doc_coord)
    pya.click()
    pya.typewrite(endoscopist)
    pya.typewrite(['enter', 'e', 'enter'])
    pya.moveRel(400, 0)
    pya.click()
    pya.typewrite(nurse)
    pya.typewrite(['enter', 'e', 'enter'])
    if clips != 0 or varix_lot:
        pros_coord = coords.get(user, ((100, 155), (100, 360)))[1]
        pya.moveTo(pros_coord)
        pya.click()
        if varix_lot:
            pyperclip.copy('Boston Scientific Speedband Superview Super 7')
            pya.hotkey('ctrl', 'v')
            pya.press('enter')
            time.sleep(0.5)
            pyperclip.copy(varix_lot)
            pya.hotkey('ctrl', 'v')
            pya.press('enter')
            pya.typewrite(['tab'] * 2)
        if clips != 0:
            pyperclip.copy('M00521230')
            for i in range(clips):
                pya.typewrite(['b', 'enter'])
                time.sleep(0.5)
                pya.hotkey('ctrl', 'v')
                pya.press('enter')
                pya.typewrite(['tab'] * 2)


def write_as_billed(mrn):
    today = datetime.datetime.now()
    date_file_str = today.strftime('%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
        'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    temp_holder = []
    with open(today_path, 'r') as f:
        reader = csv.reader(
            f, dialect='excel', lineterminator='\n')
        for line in reader:
            if line[12] == mrn:
                line[13] = '&#10004;'
                temp_holder.append(line)
            else:
                temp_holder.append(line)
    with open(today_path, 'w') as handle:
        datawriter = csv.writer(
            handle, dialect='excel', lineterminator='\n')
        for line in temp_holder:
            datawriter.writerow(line)

    return today_path


def make_web_secretary(today_path):
    """Render jinja2 template and write to file for web page of today's patients"""
    today = datetime.datetime.now()
    today_str = today.strftime(
        '%A' + '  ' + '%d' + '-' + '%m' + '-' + '%Y')
    today_data = deque()
    with open(today_path) as data:
        reader = csv.reader(data)
        for ep in reader:
            today_data.appendleft(ep)
    path_to_template = 'D:\\JOHN TILLET\\episode_data\\today_sec_template.html'
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = 'today_sec_template.html'
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open('d:\\Nobue\\today_new.html', 'w') as f:
        f.write(a)


def dumper():
    pya.click(100, 500)
    pya.hotkey('alt', 'd')
    pya.press('enter')
    pya.hotkey('alt', 'd')
    mrn = pyperclip.copy('empty')
    pya.hotkey('ctrl', 'c')
    mrn = pyperclip.paste()
    print(mrn)
    today_path = write_as_billed(mrn)
    make_web_secretary(today_path)
    with shelve.open('d:\\JOHN TILLET\\episode_data\\dumper_data.db') as s:
        try:
            episode = s[mrn]
        except KeyError:
            pya.alert('No data available')
            return
    episode_discharge(
            episode['in_theatre'], episode['out_theatre'], 
            episode['anaesthetist'], episode['endoscopist'])
    episode_procedures(
            episode['upper'], episode['colon'],
            episode['banding'], episode['asa'])
    if (episode['upper'] in {'30490-00'}
            or 'HALO' in episode['message']
            or '32089-00' in episode['message']
            or episode['colon'] in {'32093-00', '32094-00'}
            or episode['banding'] in {'32153-00'}): 
            episode_claim()
    else:
        pya.hotkey('alt', 'c')
    episode_theatre(episode['endoscopist'], episode['nurse'],
                    episode['clips'], episode['varix_lot'])


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