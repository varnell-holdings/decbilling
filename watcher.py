# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:27:05 2018

@author: John
"""

import time
import webbrowser
from tkinter import *
from tkinter import ttk
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, PatternMatchingEventHandler

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
#try:
#    observer.join()
#except KeyboardInterrupt:
#    observer.stop()


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
root.geometry('100x80+900+600')
#root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


lab = ttk.Label(mainframe, text="Up to date!")
lab.grid(column=0, row=0, sticky=W)


but = ttk.Button(mainframe, text='Open web page', command=runner)
but.grid(column=0, row=1, sticky=E)


for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)


root.mainloop()