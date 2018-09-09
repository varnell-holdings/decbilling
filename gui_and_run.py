# -*- coding: utf-8 -*-
"""
Created on Thu May 17 14:38:23 2018

@author: John2
"""

"""Gui for decbilling."""
import datetime
from dateutil.relativedelta import relativedelta
import os
import time
import webbrowser

#from tkinter import *
from tkinter import ttk, StringVar, Tk, W, E, N, S, Spinbox, FALSE, Menu

import pyautogui as pya
import gui_names_and_codes as gnc
from login_and_run import *
from login_and_run import (
        message_to_csv, front_scrape, address_scrape, episode_getfund,
        shelver, bill_process, to_anaesthetic_csv, render_anaesthetic_report,
        print_receipt, message_parse, episode_to_csv, make_web_secretary,
        make_long_web_secretary, to_watched, close_out)

pya.PAUSE = 0.4

class BillingException(Exception):
    pass


def in_and_out_calculater(time_in_theatre):
    time_in_theatre = int(time_in_theatre)
    nowtime = datetime.datetime.now()
    outtime = nowtime + relativedelta(minutes=+3)
    intime = nowtime + relativedelta(minutes=-time_in_theatre)
    out_formatted = outtime.strftime('%H' + ':' + '%M')
    in_formatted = intime.strftime('%H' + ':' + '%M')

    return (in_formatted, out_formatted)


def open_roster():
    webbrowser.open('d:\\Nobue\\anaesthetic_roster.html')

def open_today():
    nob_today = 'd:\\Nobue\\today_new.html'
    webbrowser.open(nob_today)

def open_dox():
    pya.hotkey('ctrl', 'w')

def start_watcher():
    os.startfile(
                 'D:\\JOHN TILLET\\source\\active\\billing\\watcher.py')

def open_receipt():
    os.startfile('d:\\JOHN TILLET\\episode_data\\os_acc.docx')

def send_message():
    message = pya.prompt(text='Enter your message',
                               title='Message',
                               default='')
    today_path =  message_to_csv(message)
    make_web_secretary(today_path)


def update():
    today = datetime.datetime.now()
    date_file_str = today.strftime(
                             '%Y' + '-' + '%m' + '-' + '%d')
    date_filename = date_file_str + '.csv'
    today_path = os.path.join(
             'd:\\JOHN TILLET\\episode_data\\csv\\' + date_filename)
    make_web_secretary(today_path)
    make_long_web_secretary(today_path)
    nob_today = 'd:\\Nobue\\today_new.html'
    webbrowser.open(nob_today)


def open_help():
    webbrowser.open('d:\\nobue\\help.html')

def runner(*args):
    
    try:
        insur_code, fund, ref, fund_number, message = '', '', '','', ''
    
        anaesthetist = an.get()
        endoscopist = end.get()
        nurse = nur.get()
    
        asa = asc.get()
        if asa == 'No Sedation':
            message += 'No sedation.'
        asa = gnc.ASA_DIC[asa]
        
    
        upper = up.get()
        if upper == 'Cancelled':
            message += 'Upper cancelled.'
        if upper == 'Pe with varix banding':
            message += 'Bill varix bander.'
            varix_lot = pya.prompt(text='Enter the varix bander lot number.',
                                   title='Varix',
                                   default='')
        else:
            varix_lot = ''
        if upper == 'HALO':
            halo = pya.prompt(text='Type either "90" or "ultra".',
                              title='Halo',
                              default='90')
            message += halo + '.'
        upper = gnc.UPPER_DIC[upper]
    
        colon = co.get()
        if colon == 'Cancelled':
            message += 'Colon Cancelled.'
        colon = gnc.COLON_DIC[colon]
    
        banding = ba.get()
        if banding == 'Banding of haemorrhoids':
            message += ' Banding haemorrhoids.'
            if endoscopist == 'Dr A Wettstein':
               message += ' Bill bilateral pudendal blocks.'
        if banding == 'Anal Dilatation':
            message += ' Anal dilatation.'
            if endoscopist == 'Dr A Wettstein':
                message += ' Bill bilateral pudendal blocks.'
        banding = gnc.BANDING_DIC[banding]
    
        clips = cl.get()
        clips = int(clips)
        if clips != 0:
            message += 'clips * {}.'.format(clips)
    
        consult = con.get()
        consult = gnc.CONSULT_DIC[consult]
    
        formal_message = mes.get()
        if formal_message:
            message += formal_message + '.'
    
        op_time = ot.get()
        op_time = int(op_time)
    
        fund = fu.get()
        if fund == '':
            pya.alert(text='No fund!')
            raise BillingException
        
        insur_code = gnc.FUND_TO_CODE.get(fund, 'ahsa')
        if insur_code == 'ga':
            ref = pya.prompt(text='Enter Episode Id',
                             title='Ep Id',
                             default=None)
            fund_number = pya.prompt(text='Enter Approval Number',
                                     title='Approval Number',
                                     default=None)
        if insur_code == 'os':
            paying = pya.confirm(text='Paying today?', title='OS', buttons=['Yes', 'No'])
            if paying == 'Yes':
                fund = 'Overseas'
            else:
                fund = pya.prompt(text='Enter Fund Name',
                                  title='Fund',
                                  default='Overseas')
    
        (in_theatre, out_theatre) = in_and_out_calculater(op_time)
    
        if upper is None and colon is None:
            pya.alert(text='You must enter either an upper or lower procedure!',
                      title='', button='OK')
            raise BillingException
    
        if banding is not None and colon is None:
            pya.alert(text='Must enter a lower procedure with the anal procedure!',
                      title='', button='OK')
            raise BillingException
    
        if '' in (anaesthetist, endoscopist, nurse):
            pya.alert(text='Missing data!',
                      title='', button='OK')
            raise BillingException
        
        pya.click(50, 450)
        while True:
            if not pya.pixelMatchesColor(150, 630, (255, 0, 0)):
    #            print('Open the patient file.')
    #            input('Hit Enter when ready.')
    #            pya.click(50, 450)
                pya.alert(text='Patient file not open??')
                raise BillingException
            else:
                break
    
        mrn, name = front_scrape()
        address, dob = address_scrape()
    #        scrape fund details if billing anaesthetist
        if asa is not None:
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref)
        else:
            mcn = ref = fund = fund_number = ''
            
        shelver(mrn, in_theatre, out_theatre, anaesthetist, endoscopist, asa,
                upper, colon, banding, nurse, clips, varix_lot, message)
        
    #        anaesthetic billing
        if asa is not None:
            anaesthetic_tuple, message = bill_process(
                dob, upper, colon, asa, mcn, insur_code, op_time,
                name, address, ref, fund, fund_number, endoscopist,
                anaesthetist, message)
            to_anaesthetic_csv(anaesthetic_tuple, anaesthetist)
            
            if fund == 'Overseas':
                message = print_receipt(
                        anaesthetist, anaesthetic_tuple, message)
     
    #        web page with jinja2
        message = message_parse(message)  # break message into lines
        today_path = episode_to_csv(
                out_theatre, endoscopist, anaesthetist, name,consult,
                upper, colon, message, in_theatre,
                nurse, asa, banding, varix_lot, mrn)
        make_web_secretary(today_path)
        make_long_web_secretary(today_path)
        to_watched()
    
        time.sleep(2)
        render_anaesthetic_report(anaesthetist)
        close_out(anaesthetist)
    except BillingException:
        return
    
    asc.set('1')
    up.set('None')
    co.set('None')
    ba.set('None')
    cl.set('0')
    con.set('None')
    mes.set('')
    ot.set('20')
    fu.set('')

root = Tk()
root.title('Dec Billing')
root.geometry('350x450+900+100')
root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#win = Toplevel(root)
menubar = Menu(root)
root.config(menu=menubar)
#win['menu'] = menubar
menu_extras = Menu(menubar)
menu_admin = Menu(menubar)
menu_accounts = Menu(menubar)
menu_help = Menu(menubar)

menubar.add_cascade(menu=menu_extras, label='Extras')
menu_extras.add_command(label='Roster', command=open_roster)
menu_extras.add_command(label='Web Page', command=open_today)
menu_extras.add_command(label='Dox', command=open_dox)
#menu_extras.add_command(label='Spyder', command=start_spyder)
menu_extras.add_command(label='Message', command=send_message)

menubar.add_cascade(menu=menu_admin, label='Admin')
menu_admin.add_command(label='Update', command=update)
menu_admin.add_command(label='Watcher', command=start_watcher)

menubar.add_cascade(menu=menu_accounts,  label='Accounts')
menu_accounts.add_command(label='Receipt', command=open_receipt)

menubar.add_cascade(menu=menu_help,  label='Help')
menu_help.add_command(label='Help Page', command=open_help)


an = StringVar()
end = StringVar()
nur = StringVar()
asc = StringVar()
up = StringVar()
co = StringVar()
ba = StringVar()
cl = StringVar()
con = StringVar()
mes = StringVar()
ot = StringVar()
fu = StringVar()

ttk.Label(mainframe, text="Anaesthetist").grid(column=1, row=1, sticky=W)
an = ttk.Combobox(mainframe, textvariable=an)
an['values'] = gnc.BILLING_ANAESTHETISTS
an['state'] = 'readonly'
an.grid(column=2, row=1, sticky=W)

ttk.Label(mainframe, text="Endoscopist").grid(column=1, row=2, sticky=W)
end = ttk.Combobox(mainframe, textvariable=end)
end['values'] = gnc.ENDOSCOPISTS
end['state'] = 'readonly'
end.grid(column=2, row=2, sticky=W)

ttk.Label(mainframe, text="Nurse").grid(column=1, row=3, sticky=W)
nur = ttk.Combobox(mainframe, textvariable=nur)
nur['values'] = gnc.NURSES
nur['state'] = 'readonly'
nur.grid(column=2, row=3, sticky=W)

ttk.Label(mainframe, text="ASA").grid(column=1, row=4, sticky=W)
asc = ttk.Combobox(mainframe, textvariable=asc)
asc['values'] = gnc.ASA
asc['state'] = 'readonly'
asc.grid(column=2, row=4, sticky=W)

ttk.Label(mainframe, text="Upper").grid(column=1, row=5, sticky=W)
up = ttk.Combobox(mainframe, textvariable=up)
up['values'] = gnc.UPPERS
up['state'] = 'readonly'
up.grid(column=2, row=5, sticky=W)

ttk.Label(mainframe, text="Lower").grid(column=1, row=6, sticky=W)
co = ttk.Combobox(mainframe, textvariable=co)
co['values'] = gnc.COLONS
co['state'] = 'readonly'
co.grid(column=2, row=6, sticky=W)

ttk.Label(mainframe, text="Anal").grid(column=1, row=7, sticky=W)
ba = ttk.Combobox(mainframe, textvariable=ba)
ba['values'] = gnc.BANDING
ba['state'] = 'readonly'
ba.grid(column=2, row=7, sticky=W)

ttk.Label(mainframe, text="Clips").grid(column=1, row=8, sticky=W)
s = Spinbox(mainframe, from_=0, to=20, textvariable=cl)
s.grid(column=2, row=8, sticky=W)

ttk.Label(mainframe, text="Consult").grid(column=1, row=9, sticky=W)
con = ttk.Combobox(mainframe, textvariable=con)
con['values'] = gnc.CONSULT_LIST
con['state'] = 'readonly'
con.grid(column=2, row=9, sticky=W)

ttk.Label(mainframe, text="Message").grid(column=1, row=10, sticky=W)
ttk.Entry(mainframe, textvariable=mes).grid(column=2, row=10, sticky=W)


ttk.Label(mainframe, text="Time").grid(column=1, row=11, sticky=W)
ti = Spinbox(mainframe, from_=0, to=90, textvariable=ot)
ti.grid(column=2, row=11, sticky=W)

ttk.Label(mainframe, text="Fund").grid(column=1, row=12, sticky=W)
fun = ttk.Combobox(mainframe, textvariable=fu)
fun['values'] = gnc.FUNDS
# fun['state'] = 'readonly'
fun.grid(column=2, row=12, sticky=W)

ttk.Button(mainframe, text='Send!', command=runner).grid(
    column=2, row=13, sticky=W)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
root.bind('<Return>', runner)
asc.set('1')
up.set('None')
co.set('None')
ba.set('None')
con.set('None')
ot.set('20')
fu.set('')

root.mainloop()
