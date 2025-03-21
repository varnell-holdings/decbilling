# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:27:05 2018

@author: John
"""
import datetime
import os
import shelve
import time
import webbrowser
from tkinter import ttk, W, E, N, S, Tk, Menu

from jinja2 import Environment, FileSystemLoader
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent, PatternMatchingEventHandler
import pyautogui as pya
import pyperclip

pya.PAUSE = 0.6
pya.FAILSAFE = True

# coord of doctor field and disposibles i theatre tab in day surgery
coords = {
    "John": ((510, 310), (100, 360)),
    "John2": ((320, 245), (320, 430)),
    "Recept1": ((320, 330), (320, 520)),
    "Recept4": ((320, 245), (320, 435)),
    "Recept3": ((100, 165), (100, 352)),
    "Recept5": ((320, 330), (320, 520)),
    "Admin3": ((100, 163), (100, 345)),
    "Accounts": ((320, 245), (320, 430)),
    "Regina": ((620, 350), (620, 540)),
}

observer = Observer()


class Handler(PatternMatchingEventHandler):
    def on_modified(self, event: FileModifiedEvent):
        global lab, root, but
        lab.configure(text="New Patient!")
        lab.configure(background="red")
        #        root.attributes("-topmost", True)
        time.sleep(10)
        root.deiconify()
        root.attributes("-topmost", True)


observer.schedule(
    event_handler=Handler("*"), path="d:\\john tillet\\episode_data\\watched\\"
)
observer.daemon = False
observer.start()


class EpFullException(Exception):
    pass


def episode_discharge(intime, outtime, anaesthetist, endoscopist):
    pya.hotkey("alt", "n")
    pya.typewrite(["left"] * 8)
    #    pya.typewrite(["enter"] * 4)
    pya.typewrite(["tab"] * 5)
    pya.typewrite(intime)
    pya.typewrite(["enter"] * 2)
    pya.typewrite(outtime)
    pya.typewrite(["enter"] * 3)
    pya.typewrite(["tab"] * 5)
    time.sleep(1)
    # pya.typewrite(anaesthetist)
    # time.sleep(1)
    # pya.typewrite(anaesthetist + "\n")
    # pyperclip.copy(anaesthetist)
    # time.sleep(1)
    # pyperclip.paste()
    

    #    pya.typewrite("\n")
    # time.sleep(4)
    # pya.press("tab")
    # pya.typewrite(endoscopist)
    # time.sleep(1)


def episode_claim():
    pya.hotkey("alt", "s")
    pya.typewrite(["left"] * 2)
    pya.hotkey("shift", "tab")
    fund_test = pyperclip.copy("empty")
    pya.hotkey("ctrl", "c")
    fund_test = pyperclip.paste()
    if fund_test in {"BUP", "ADF"}:
        bupa_flag = True
    else:
        bupa_flag = False
    #    bupa_flag = False
    pya.typewrite(["tab"] * 4)
    if fund_test == "999":
        pya.typewrite("NO COVER")
    else:
        pya.typewrite("FULL")
    #    pya.typewrite('FULL')
    pya.press("enter")
    pya.typewrite("self")
    pya.press("enter")
    pya.press("enter")
    time.sleep(2)

    return bupa_flag


def episode_procedures(upper, lower, anal, asa, bupa_flag=False):
    anal_flag = False
    pya.hotkey("alt", "p")
    if lower:  # first line - either upper or lower is always true
        pya.typewrite(lower + "\n")
        pya.press("enter")
    else:
        pya.typewrite(upper + "\n")
        pya.press("enter")
    pya.typewrite(["tab"] * 4)
    if bupa_flag:
        pya.typewrite("10.0")
    pya.typewrite(["tab"] * 2)
    if upper and lower:  # second line
        pya.typewrite(upper + "\n")
        pya.press("enter")
    elif anal:
        pya.typewrite(anal + "\n")
        pya.press("enter")
        anal_flag = True
    else:
        if asa:
            pya.typewrite(asa + "\n")
            pya.press("enter")
        return
    pya.typewrite(["tab"] * 2)
    if anal and anal_flag is False:  # third line
        pya.typewrite(anal + "\n")
        pya.press("enter")
    else:
        if asa:
            pya.typewrite(asa + "\n")
            pya.press("enter")
        return
    pya.typewrite(["tab"] * 2)
    if asa:  # fourth line
        pya.typewrite(asa + "\n")
        pya.press("enter")
    return


def episode_claim_b3(band3):
    pya.hotkey("alt", "s")
    pya.typewrite(["left"] * 2)
    for i in range(7):
        pya.hotkey("shift", "tab")
    if band3:
        pya.press("3")
    else:
        pya.press("1")


def episode_theatre(endoscopist, nurse, clips, varix_lot):
    pya.hotkey("alt", "n")
    pya.typewrite(["left"] * 2)

    user = os.getenv("USERNAME")
    doc_coord = coords.get(user, ((320, 245), (320, 430)))[0]

    
    pya.press("tab")
    pya.typewrite(nurse, interval=0.05)
    pya.press("enter")
    pya.press("e")
    pya.press("enter")


    pya.hotkey("shift", "tab")
    pya.moveTo(doc_coord)
    time.sleep(1)
    pya.click()
    pya.typewrite(endoscopist, interval=0.05)
    pya.press("enter")
    pya.press("e")
    pya.press("enter")
    pya.hotkey("shift", "tab")

    if clips != 0 or varix_lot:
        pros_coord = coords.get(user, ((320, 245), (320, 245)))[1]
        pya.moveTo(pros_coord)
        pya.click()
        if "v" in varix_lot:
            pyperclip.copy("Boston Scientific Speedband Superview Super 7")
            pya.hotkey("ctrl", "v")
            pya.press("enter")
            time.sleep(0.5)
            pya.typewrite("M00542250")
            pya.press("enter")

            pya.typewrite(["tab"] * 2)
        if "h" in varix_lot:
            pyperclip.copy("HB Haemoband")
            pya.hotkey("ctrl", "v")
            pya.press("enter")
            time.sleep(0.5)
            pya.typewrite("BH001")
            pya.press("enter")

            pya.typewrite(["tab"] * 2)
        if clips != 0:
            pyperclip.copy("M00521230")
            for i in range(clips):
                pya.typewrite(["b", "enter"])
                time.sleep(0.5)
                pya.hotkey("ctrl", "v")
                pya.press("enter")
                pya.typewrite(["tab"] * 2)





def write_as_billed_shelf(mrn):
    today = datetime.datetime.now()
    date_file_str = today.strftime("%Y" + "-" + "%m" + "-" + "%d")
    today_path = os.path.join(
        "d:\\JOHN TILLET\\episode_data\\webshelf\\" + date_file_str + "_19"
    )
    with shelve.open(today_path, writeback=False) as s:
        nested_dict = s[mrn]
        nested_dict["billed"] = "&#10004;"
        s[mrn] = nested_dict

    #        s[mrn]['billed'] = '&#10004;'

    return today_path


def make_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for web page of today's patients
    from shelf data
    """
    today = datetime.datetime.today()
    today_str = today.strftime("%A" + "  " + "%d" + "-" + "%m" + "-" + "%Y")
    with shelve.open(today_path) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x["out_theatre"], reverse=True)

    path_to_template = "D:\\JOHN TILLET\\episode_data\\today_sec_shelf_template_19.html"
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = "today_sec_shelf_template_19.html"
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open("d:\\Nobue\\today_new.html", "w", encoding="utf-8") as f:
        f.write(a)


def dumper():
    pya.click(100, 500)
    pya.hotkey("alt", "d")
    pya.press("enter")
    pya.hotkey("alt", "d")
    mrn = pyperclip.copy("empty")
    pya.hotkey("ctrl", "c")
    mrn = pyperclip.paste()

    with shelve.open("d:\\JOHN TILLET\\episode_data\\dumper_data.db") as s:
        try:
            episode = s[mrn]
        except KeyError:
            pya.alert("No data available")
            return
    episode_discharge(
        episode["in_theatre"],
        episode["out_theatre"],
        episode["anaesthetist"],
        episode["endoscopist"],
    )
    bupa_flag = episode_claim()
    time.sleep(2)
    episode_procedures(
        episode["upper"],
        episode["colon"],
        episode["banding"],
        episode["asa"],
        bupa_flag,
    )
    band3 = (
        episode["upper"] in {"30490-00", "41819-00"}
        or "HALO" in episode["message"]
        or "32089-00" in episode["message"]
        or episode["colon"] in {"32093-00", "32094-00"}
        or episode["banding"] in {"32153-00"}
    )

    episode_claim_b3(band3)

    pya.hotkey("alt", "c")
    episode_theatre(
        episode["endoscopist"], episode["nurse"], episode["clips"], episode["varix_lot"]
    )

    try:
        today_path = write_as_billed_shelf(mrn)
        make_web_secretary_from_shelf(today_path)
    except:
        pass


def open_help():
    webbrowser.open("d:\\Nobue\\watcher_help.html")


def runner(*args):
    lab.configure(text="Up to date!")
    lab.configure(background="green")
    #    webbrowser.register('chrome', None)
    webbrowser.open("d:\\Nobue\\today_new.html")
    #    root.attributes("-topmost", False)
    time.sleep(2)
    root.iconify()


root = Tk()
root.title("Billing")
root.geometry("100x160+900+570")
# root.option_add('*tearOff', FALSE)


mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


menubar = Menu(root)
root.config(menu=menubar)
menu_help = Menu(menubar)

menubar.add_cascade(menu=menu_help, label="Help")
menu_help.add_command(label="Help Page", command=open_help)
# menu_admin.add_command(label='Add Staff', command=add_staff)


lab = ttk.Label(mainframe, text="Up to date!")
lab.grid(column=0, row=0, sticky=W)


but = ttk.Button(mainframe, text="Open web page", command=runner)
but.grid(column=0, row=1, sticky=E)

but = ttk.Button(mainframe, text="Dump data", command=dumper)
but.grid(column=0, row=2, sticky=W)


for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)


root.mainloop()
