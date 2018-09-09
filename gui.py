"""Gui for decbilling."""
import datetime
from dateutil.relativedelta import relativedelta

from tkinter import *
from tkinter import ttk

import pyautogui as pya
import gui_names_and_codes as gnc


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


def runner(*args):

    message = ''

    anaesthetist = an.get()
    endoscopist = end.get()
    nurse = nur.get()

    asa = asc.get()
    if asa == 'None':
        message += 'No sedation.'
    asa = gnc.ASA_DIC[asa]
    asc.set('1')

    upper = up.get()
    if upper == 'Cancelled':
        message += 'Upper cancelled.'
    if upper == 'Pe with varix banding':
        varix_flag = True
        message += 'Bill varix bander.'
        varix_lot = pya.prompt(text='Enter the varix bander lot number.',
                               title='Varix',
                               default='')
    else:
        varix_flag = False
        varix_lot = ''
    if upper == 'HALO':
        halo = pya.prompt(text='Type either "90" or "ultra".',
                          title='Halo',
                          default='90')
        message += halo + '.'
    upper = gnc.UPPER_DIC[upper]
    up.set('None')

    colon = co.get()
    if colon == 'Cancelled':
        message += 'Colon Cancelled.'
    if colon == 'Colon - Govt FOB screening':
        message += 'Bill 32088-00.'
    if colon == 'Colon with polyp - Govt FOB screening':
        message += 'Bill 32089-00.'
    colon = gnc.COLON_DIC[colon]
    co.set('None')

    banding = ba.get()
    if banding == 'Banding of haemorrhoids.':
        message += ' Banding haemorrhoids'
        if consultant == 'Dr A Wettstein':
            message += ' Bill bilateral pudendal blocks.'
    if banding == 'Anal Dilatation':
        message += ' Anal dilatation.'
        if consultant == 'Dr A Wettstein':
            message += ' Bill bilateral pudendal blocks.'
    banding = gnc.BANDING_DIC[banding]
    ba.set('None')

    clips = cl.get()
    clips = int(clips)
    if clips != 0:
        message += 'clips * {}.'.format(clips)

    consult = con.get()
    consult = gnc.CONSULT_DIC[consult]
    con.set('None')

    formal_message = mes.get()
    if formal_message:
        message += formal_message + '.'
    mes.set('')

    op_time = ot.get()
    op_time = int(op_time)
    ot.set('20')

    fund = fu.get()
    fu.set('')

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

    in_data = (anaesthetist, endoscopist, nurse, asa, upper, colon,
               banding, clips, consult, message, op_time, fund,
               in_theatre, out_theatre, varix_flag, varix_lot)
    print(in_data)


root = Tk()
root.title('Dec Billing')
root.geometry('450x470+900+100')
# root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# win = Toplevel(root)
# menubar = Menu(win)
# win['menu'] = menubar
# menubar = Menu(parent)
# menu_file = Menu(menubar)
# menu_edit = Menu(menubar)
# menubar.add_cascade(menu=menu_file, label='File')
# menubar.add_cascade(menu=menu_edit, label='Edit')

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
an['values'] = gnc.ANAESTHETISTS
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

ttk.Label(mainframe, text="Fund - ignore").grid(column=1, row=12, sticky=W)
fun = ttk.Combobox(mainframe, textvariable=fu)
fun['values'] = gnc.FUNDS
# fun['state'] = 'readonly'
fun.grid(column=2, row=12, sticky=W)

ttk.Button(mainframe, text='Send!', command=runner).grid(
    column=3, row=11, sticky=E)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

asc.set('1')
up.set('None')
co.set('None')
ba.set('None')
con.set('None')
ot.set('20')

root.mainloop()
