# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 10:19:58 2025

@author: John2

adding a recall feature to docbill
"""


from awsenv import aws_access_key_id, aws_secret_access_key
import boto3
from configparser import ConfigParser
import csv
from dataclasses import dataclass
import datetime
import logging
import os
from pathlib import Path
import pickle
from pprint import pprint
import random
import re
import shelve
import shutil
from tempfile import NamedTemporaryFile
import threading
import time
from tkinter import ttk, StringVar, Tk, W, E, N, S
from tkinter import Spinbox, FALSE, Menu, Frame, messagebox

import tkinter as tk
import webbrowser

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import docx
from jinja2 import Environment, FileSystemLoader
import pymsgbox as pmb

import pyautogui as pya
import requests
from pyisemail import is_email
import pyperclip

# import win32api

import decbatches

pya.PAUSE = 0.2


class BillingException(Exception):
    pass


class ScrapingException(Exception):
    pass


# globals
overide_endoscopist = False
finish_time = False
biller_anaesthetist_flag = False
double_set = set()

# ST = 10

epdata_path = Path("D:\\JOHN TILLET\\episode_data")
source_path = Path("D:\\JOHN TILLET\\source")
nobue_path = Path("D:\\Nobue")

caecum_csv_file = source_path / "active" / "caecum" / "caecum.csv"
sec_web_page = nobue_path / "today_new.html"
sec_web_page1 = nobue_path / "today_new1.html"
sec_long_web_page = nobue_path / "today_long.html"
aws_data_path = source_path / "active" / "billing" / "aws_data.csv"


logfilename = epdata_path / "doclog.log"
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler(logfilename), logging.StreamHandler()],
    format="%(asctime)s %(message)s",
)

today = datetime.datetime.today()

# need this for boto3
# sys.path.append("C:\\Users\\John2\\Miniconda3\\lib\\site-packages\\urllib3\\util\\")


config_parser = ConfigParser(allow_no_value=True)

staff_path = epdata_path / "STAFF.ini"
config_parser.read(staff_path)
NURSES = config_parser.options("nurses")
NURSES = [a.title() for a in NURSES]
ENDOSCOPISTS = config_parser.options("endoscopists")
ENDOSCOPISTS = [a.title() for a in ENDOSCOPISTS]
ANAESTHETISTS = config_parser.options("anaesthetists")
ANAESTHETISTS = [a.title() for a in ANAESTHETISTS]

funds_path = epdata_path / "FUNDS.ini"
config_parser.read(funds_path)
FUNDS = config_parser.options("funds")
FUNDS = [a.title() for a in FUNDS]


user = os.getenv("USERNAME")

if user == "John":
    RED_BAR_POS = (280, 790)
    TITLE_POS = (230, 170)
    MRN_POS = (740, 315)
    POST_CODE_POS = (610, 355)
    DOB_POS = (750, 220)
    FUND_NO_POS = (770, 703)
    CLOSE_POS = (1020, 120)
elif user == "John2":
    RED_BAR_POS = (160, 630)
    TITLE_POS = (200, 134)
    MRN_POS = (600, 250)
    POST_CODE_POS = (490, 284)
    DOB_POS = (600, 174)
    FUND_NO_POS = (580, 548)
    CLOSE_POS = (774, 96)

BILLING_ANAESTHETISTS = ["Dr S Vuong", "Dr J Tillett"]

scr_width, scr_height = pya.size()

BILLING_ENDOSOSCOPISTS = [
    "Dr A Wettstein",
    "A/Prof R Feller",
    "Dr S Vivekanandarajah",
    "Dr S Ghaly",
    "Dr J Mill",
    "Dr S Sanagapalli",
    "Dr J Chetwood",
]


DEC_ENDOSCOPISTS = {
    "bariol": 1,
    "ghaly": 6,
    "feller": 4,
    "vivekanandarajah": 18,
    "wettstein": 40,
    "williams": 42,
    "mill": 8,
    "sanagapalli": 10,
    "stoita": 13,
}

RECALL_PROC = {"upper": 2, "colon": 1, "double": 3}

YEARS_TO_WEEKS = {1: "52", 2: "104", 3: "156", 5: "260"}

RECALL_DIC = {
    "No colon recall": 0,
    "No Pe recall": 0,
    "? Pe recall": 0,
    "? Col recall": 0,
    "1 year": 1,
    "2 years": 2,
    "3 years": 3,
    "5 years": 5,
}

ASA = ["No Sedation", "ASA 1", "ASA 2", "ASA 3"]

ASA_DIC = {
    "No Sedation": "",
    "ASA 1": "92515-19",
    "ASA 2": "92515-29",
    "ASA 3": "92515-39",
}

UPPERS = [
    "No Upper",
    "Pe",
    "Pe with Bx",
    "Oesophageal diatation",
    "O Dil + PE",
    "Pe with APC",
    "Pe with polypectomy",
    "Pe with varix banding",
    "Cancelled",
    "BRAVO",
    "HALO",
    "Pe + Botox Crico",
]

UPPER_DIC = {
    "No Upper": "",
    "Cancelled": "",
    "Pe": "30473-00",
    "Pe with Bx": "30473-01",
    "Oesophageal diatation": "30475-00",
    "O Dil + PE": "30475-00",
    "Pe with APC": "30478-20",
    "HALO": "30478-20",
    "Pe with polypectomy": "30478-04",
    "Pe with varix banding": "30478-20",
    "BRAVO": "30490-00",
    "Pe + Botox Crico": "30473-00",
}

COLONS = [
    "No Lower",
    "Planned Short Colon",
    "Exam via stoma",
    "Failure to reach caecum",
    "Cancelled",
    "Non Rebatable",
    "32222",
    "32223",
    "32224",
    "32225",
    "32226",
    "32227",
    "32228",
    "32230",
]

COLON_DIC = {
    "No Lower": "",
    "Planned Short Colon": "32084-00",
    "Exam via stoma": "32095-00",
    "Failure to reach caecum": "32084-00",
    "Cancelled": "",
    "Non Rebatable": "Non Rebatable",
    "32222": "32222",
    "32223": "32223",
    "32224": "32224",
    "32225": "32225",
    "32226": "32226",
    "32227": "32227",
    "32228": "32228",
    "32230": "32230",
}

BANDING = ["No Anal Procedure", "Banding", "Banding + Pudendal", "Anal dilatation"]

BANDING_DIC = {
    "No Anal Procedure": "",
    "Banding": "32135-00",
    "Banding + Pudendal": "32135-00",
    "Anal dilatation": "32153-00",
}

CONSULT_DIC = {"No Consult": "", "Consult": "110", "No need": ""}


FUND_TO_CODE = {
    "": "",
    "Bulk Bill": "bb",
    "Veterans Affairs": "va",
    "Adf Hsc": "adf",
    "Account Today": "bill_given",
    "Account Later": "send_bill",
}


def pats_from_aws():
    try:
        requests.head("https://www.google.com", timeout=3)
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ap-southeast-2",
            verify=True,
        )

        s3.Object("dec601", "patients.csv").download_file(aws_data_path)

    except requests.ConnectionError:
        logging.error("Failed to get patients list.", exc_info=False)


def process_aws_data():
    global double_set
    date = today.strftime("%d/%m/%Y")
    with open(aws_data_path, encoding="utf-8") as h:
        reader = csv.reader(h)
        for patient in reader:
            this_day = patient[0]
            if len(this_day) == 9:
                this_day = "0" + this_day
            if (this_day == date) and patient[3] == "True":
                double_set.add(patient[1])
    print(f"Doubles : {double_set}")


def download_and_process():
    pats_from_aws()
    process_aws_data()


@dataclass
class ProcedureData:
    anaesthetist: str
    endoscopist: str
    nurse: str
    upper: str
    colon: str
    banding: str
    asa: str
    polyp: str
    caecum_reason_flag: str
    consult: str
    message: str
    clips: int
    op_time: str
    pe_recall: str
    col_recall: str
    mrn: str = ""
    title: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    dob: str = ""
    email: str = ""
    in_theatre: str = ""
    out_theatre: str = ""
    varix_lot: str = ""
    upper_for_daysurgery: str = ""
    colon_for_daysurgery: str = ""
    fund: str = ""
    fund_number: str = ""
    mcn: str = ""
    ref: str = ""
    insur_code: str = ""
    street: str = ""
    suburb: str = ""
    state: str = ""
    postcode: str = ""
    full_address: str = ""

    @classmethod
    def from_string_vars(
        cls, an, end, nur, up, co, ba, asc, po, caecum, con, mes, cl, ot
    ):
        form_data = cls(
            anaesthetist=an.get(),
            endoscopist=end.get(),
            nurse=nur.get(),
            upper=up.get(),
            colon=co.get(),
            banding=ba.get(),
            asa=asc.get(),
            polyp=po.get(),
            caecum_reason_flag=caecum.get(),
            consult=con.get(),
            message=mes.get(),
            clips=int(cl.get()),
            pe_recall=per.get(),
            col_recall=colr.get(),
            op_time=ot.get(),
            fund=fu.get(),
        )
        form_data.process_inputs()
        return form_data

    def process_inputs(self):
        """Get data ready for web page and dumper."""
        if self.message:
            self.message += "."
        if self.upper == "Cancelled":
            self.message += "Upper cancelled."
        if self.upper == "Pe with varix banding":
            self.message += "Bill varix bander - BS225"
            self.varix_lot += "v"
        if self.upper == "O Dil + PE":
            self.message += "Also bill 30473-00"
        if self.upper == "HALO":
            self.message += "Halo Ultra."
        if self.upper == "Pe + Botox Crico":
            self.message += "Botox Cricopharyngeus."

        self.upper = UPPER_DIC[self.upper]
        if self.upper == "30475-00":
            self.upper_for_daysurgery = "41819-00"
        else:
            self.upper_for_daysurgery = self.upper

        if self.colon == "Cancelled":
            self.message += "Colon cancelled."
        elif self.colon == "Non Rebatable":
            resp = pmb.confirm(
                text="You have billed a non rebatable colon.",
                title="",
                buttons=["Continue", "Go Back"],
            )
            if resp == "Go Back":
                raise BillingException()
            self.message += "Colon done but Non Rebatable."
        elif self.colon == "Failure to reach caecum":
            self.message += "Short colon only."
        elif self.colon[0:3] == "322":
            self.caecum_reason_flag = "success"

        self.colon = COLON_DIC[self.colon]

        if self.banding == "Banding":
            self.message += "Banding haemorrhoids 32135 & disposable DH011."
        elif self.banding == "Banding + Pudendal":
            self.message += "Banding haemorrhoids 32135 & disposable DH011.Also bill Pudendal Block."
        elif self.banding == "Anal dilatation":
            self.message += "Anal dilatation."
        if self.endoscopist.lower()[-1] == "gett" and "Banding" in self.message:
            self.message.replace("32135", "BH0001")

        self.banding = BANDING_DIC[self.banding]

        if self.asa == "No Sedation":
            self.message += "No sedation."

        self.asa = ASA_DIC[self.asa]

        if self.polyp == "Biopsy" and self.colon == "32084-00":
            self.colon = "32084-01"
        elif self.polyp == "Polypectomy":
            self.polyp = "32229"

        if self.colon == "32084-00" and self.polyp == "32229":
            self.colon = "32087-00"
            self.polyp = ""

        # day surgery uses the old style codes
        if self.colon in {"32084-00", "32084-01", "32087-00", "32095-00"}:
            self.colon_for_daysurgery = self.colon
        elif self.colon == "Non Rebatable":
            self.colon_for_daysurgery = "32090-00"
        elif self.colon == "32227":
            dil_flag = pmb.confirm(
                text="Was that a colonic dilatation?", buttons=["Dilatation", "Other"]
            )
            if dil_flag == "Dilatation":
                self.colon_for_daysurgery = "32094-00"
            elif self.polyp == "32229":
                self.colon_for_daysurgery = "32093-00"
            else:
                self.colon_for_daysurgery = "32090-00"
        elif self.colon and self.polyp == "32229":
            self.colon_for_daysurgery = "32093-00"
        elif self.colon and self.polyp == "Biopsy":
            self.colon_for_daysurgery = "32090-01"
        elif self.colon and self.polyp == "No colon pathology":
            self.colon_for_daysurgery = "32090-00"
        else:
            self.colon_for_daysurgery = None

        if self.polyp in {"Colon Pathology", "No colon pathology", "Biopsy"}:
            self.polyp = ""
        if self.colon == "32230":
            self.polyp = ""

        self.consult = CONSULT_DIC[self.consult]
        if self.clips:
            self.message += f"{self.clips} clips used"

        self.pe_recall = RECALL_DIC[self.pe_recall]
        self.col_recall = RECALL_DIC[self.col_recall]

        self.insur_code = FUND_TO_CODE.get(self.fund, "no_gap")

        if self.insur_code in {"send_bill"} and self.anaesthetist == "Dr J Tillett":
            self.fund = pmb.prompt(
                text="Enter Fund Name or just Enter if none",
                title="Pay Later",
                default="",
            )

        if self.insur_code == "adf":
            self.ref = pmb.prompt(text="Enter Episode Id", title="Ep Id", default=None)
            self.fund_number = pmb.prompt(
                text="Enter Approval Number", title="Approval Number", default=None
            )
        if self.insur_code == "bb":
            self.message += "Sedation Bulk Bill"


def double_check(pd, doubles_set):
    if pd.mrn not in doubles_set:
        return True
    elif (pd.upper != "No Upper" or pd.upper == "Cancelled") and (
        pd.colon != "No Lower" or pd.colon == "Cancelled"
    ):
        return True
    else:
        pmb.alert(
            text="""Patient booked for double.
                        Choose cancelled or a procedure in both lists.""",
            title="",
            button="OK",
        )
        return False


# menu bar programs
def open_roster():
    webbrowser.open("d:\\Nobue\\anaesthetic_roster.html")


def open_today():
    nob_today = "d:\\Nobue\\today_new.html"
    webbrowser.open(nob_today)


def open_weekends():
    weekends = "file:///D:/Nobue/anaesthetic_contacts.html"
    webbrowser.open(weekends)


def error_log():
    webbrowser.open(logfilename)


def open_meditrust():
    webbrowser.open("https://www.meditrust.com.au/mtv4/home")


def add_message():
    mess_box.grid()
    mess_box.focus()


def open_dox():
    webbrowser.open("http://dox.endoscopy.local/Landing")


#     pya.hotkey("ctrl", "w")


def add_staff():
    staff = epdata_path / "STAFF.ini"
    os.startfile(str(staff))


def delete_record():
    """Delete patient from web page. Does not delete from billing csv."""
    pass
    # today_str = today.strftime("%Y-%m-%d")
    # today_path = os.path.join("d:\\JOHN TILLET\\episode_data\\webshelf\\" + today_str)
    # mrn = pya.prompt(text="Enter mrn of record to delete.", title="", default="")
    # if not mrn:
    #     return
    # with shelve.open(today_path) as s:
    #     try:
    #         del s[mrn]
    #     except Exception:
    #         pya.alert(text="Already deleted!", title="", button="OK")
    # make_web_secretary_from_shelf(today_path)
    # make_long_web_secretary_from_shelf(today_path)


def start_decbatches():
    """Because system is set to use pythonw need to write cmd file
    to fire up python for terminal programs"""
    user = os.getenv("USERNAME")
    if user == "John":
        os.startfile("c:\\Users\\John\\Miniconda3\\bccode\\start_decbatches.cmd")
    elif user == "John2":
        os.startfile("c:\\Users\\John2\\Miniconda3\\bccode\\start_decbatches.cmd")


def open_receipt():
    path = epdata_path / "sedation" / "accounts"
    os.startfile(str(path))


def open_sedation():
    path = epdata_path / "meditrust"
    os.startfile(str(path))


def asa_click(event):
    as1 = asc.get()
    if as1 == "No Sedation":
        fund_box.grid_remove()
    else:
        if biller_anaesthetist_flag:
            fund_box.grid()


def upper_combo_click(event):
    upper = up.get()
    endo = end.get()
    endo = endo.split()[-1].lower()
    if upper not in {"No Upper", "Cancelled"} and endo in DEC_ENDOSCOPISTS:
        pe_recall.grid()
    else:
        pe_recall.grid_remove()


def colon_combo_click(event):
    colon_proc = co.get()
    endo = end.get()
    endo = endo.split()[-1].lower()
    if colon_proc not in {"No Lower", "Cancelled"}:
        path_box.grid()
        ba_box.grid()
        col_recall.grid()
        if endo in DEC_ENDOSCOPISTS:
            col_recall.grid()
        else:
            col_recall.grid_remove()
    else:
        po.set("Colon Pathology")
        ba.set("No Anal Procedure")
        path_box.grid_remove()
        ba_box.grid_remove()
        col_recall.grid_remove()

    if colon_proc != "Failure to reach caecum":
        caecum_box.grid_remove()
        fail_text_label.set("")
    else:
        caecum_box.grid()
        fail_text_label.set("Reason for Failure")


def is_biller_endoscopist(event):
    endo = end.get()

    if endo in BILLING_ENDOSOSCOPISTS:
        con.set("None")
        con_label.grid()
        con_button1.grid()
        con_button2.grid()
    else:
        con.set("No need")
        con_label.grid_remove()
        con_button1.grid_remove()
        con_button2.grid_remove()


def is_biller_anaesthetist(event):
    global biller_anaesthetist_flag
    biller_anaesthetist = an.get()
    if biller_anaesthetist in {"Dr J Tillett", "Dr S Vuong"}:
        biller_anaesthetist_flag = True
        fund_box.grid()
        fu.set("Fund")
    else:
        fu.set("")
        biller_anaesthetist_flag = False
        fund_box.grid_remove()


def update_spin():
    t = int(ot.get())
    t += 1
    t = str(t)
    ot.set(t)
    root.after(60000, update_spin)


def button_enable(*args):
    """Toggle Send button when all data entered"""
    anas = an.get()
    endo = end.get()
    endo = endo.split()[-1].lower()
    nurs = nur.get()
    asa = asc.get()
    consult = con.get()
    upper = up.get()
    col = co.get()
    failure = caecum.get()
    path = po.get()
    pe_recall = per.get()
    col_recall = colr.get()
    fund = fu.get()

    top_line = anas != "Anaesthetist" and endo != "endoscopist" and nurs != "Nurse"
    if not top_line:
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Missing staff  data"
        root.update_idletasks()
        return

    if upper == "No Upper" and col == "No Lower":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Procedure ?"
        root.update_idletasks()
        return

    if asa == "ASA":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "ASA ?"
        root.update_idletasks()
        return

    if consult == "No Need":
        btn.config(state="disabled")
        btn_txt.set("")
        root.update_idletasks()
        return

    if consult == "None":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Consult ?"
        root.update_idletasks()
        return

    if col not in {"No Lower", "Cancelled"} and path == "Colon Pathology":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Colon path?"
        root.update_idletasks()
        return

    if (
        upper not in {"No Upper", "Cancelled"}
        and endo in DEC_ENDOSCOPISTS
        and pe_recall == "? Pe recall"
    ):
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Pe recall?"
        root.update_idletasks()
        return

    if (
        col not in {"No Lower", "Cancelled"}
        and endo in DEC_ENDOSCOPISTS
        and col_recall == "? Col recall"
    ):
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Col recall?"
        root.update_idletasks()
        return
    if (
        (anas in BILLING_ANAESTHETISTS)
        and (fund in {"Fund", "++++ Other Funds ++++"})
        and (asa != "No Sedation")
    ):
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Fund!"
        root.update_idletasks()
        return

    if upper != "No Upper" and col in {"No Lower", "Cancelled"}:
        btn.config(state="normal")
        btn_txt.set("Send")
        feedback["text"] = "Check time and clips then Send!"
        root.update_idletasks()
        return

    if failure == "" and col == "Failure to reach caecum":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Reason for failure?"
        root.update_idletasks()
        return

    if col != "No Lower" and path != "Colon Pathology":
        btn.config(state="normal")
        btn_txt.set("Send")
        feedback["text"] = "Check time and clips then Send!"
        root.update_idletasks()
        return


def to_watched():
    """Write dummy text to a folder. Watchdog in watcher.py watches this."""
    watched_file = epdata_path / "watched" / "watched.txt"
    with open(watched_file, mode="wt") as f:
        f.write("Howdy, watcher")


def update_and_verify_last_colon(pd):
    """
    If no long colon done it just returns None
    check if dates and codes are in conflict with Medicare rules - note exact date 1,3,5 years ago passes
    update shelf  record to today's date and return None
    note: shelf is a dictionary of keys - mrn as string, values - date of last colon as datetime.date object
    note: in docbill the global 'today' is a datetime.datetime object and has to be converted to a datetime.date object
    for comparisons to work properly
    """
    if not pd.colon:
        return
    if pd.colon[0:3] != "322":
        return
    last_colon_address = epdata_path / "last_colon_date"
    with shelve.open(str(last_colon_address)) as s:
        try:
            last_colon_date = s[pd.mrn]  # this is a datetime.date object
        except KeyError:
            last_colon_date = None

        if last_colon_date and (
            last_colon_date != today.date()
        ):  # second test is in case this is a resend today
            time_sep = relativedelta(today.date(), last_colon_date).years
            last_colon_date_printed = last_colon_date.strftime("%d-%m-%Y")

            if (pd.colon == "32226") and time_sep < 1:
                reply = pmb.confirm(
                    text=f"""Last colon performed less than one year ago {last_colon_date_printed}.
                                Check colon code with {pd.endoscopist}.""",
                    title="Colon Code Confirm",
                    buttons=["Proceed anyway", "Go Back to change"],
                )
                if reply == "Go Back to change":
                    raise BillingException
            elif (pd.colon == "32224") and time_sep < 3:
                reply = pmb.confirm(
                    text=f"""Last colon performed less than three years ago {last_colon_date_printed}.
                                Check colon code with {pd.endoscopist}.""",
                    title="Colon Code Confirm",
                    buttons=["Proceed anyway", "Go Back to change"],
                )
                if reply == "Go Back to change":
                    raise BillingException
            elif (pd.colon == "32223") and time_sep < 5:
                reply = pmb.confirm(
                    text=f"""Last colon performed less than five years ago {last_colon_date_printed}.
                                Check colon code with {pd.endoscopist}.""",
                    title="Colon Code Confirm",
                    buttons=["Proceed anyway", "Go Back to change"],
                )
                if reply == "Go Back to change":
                    raise BillingException

        s[pd.mrn] = today.date()

        if pd.colon == "32228":
            s = (
                epdata_path / "store_32228.csv"
            )  # mistakenly called a csv file - actually pickled set of mrn's who have had 32228's
            with s.open(mode="rb") as file:
                COLON_32228 = pickle.load(file)

            if pd.mrn in COLON_32228:
                reply = pmb.confirm(
                    text=f"""Patient previously billed 32228.
                                Check colon code with {pd.endoscopist}.""",
                    title="Colon Code Confirm",
                    buttons=["Proceed anyway", "Go Back to change"],
                )
                if reply == "Go Back to change":
                    raise BillingException
            else:
                COLON_32228.add(pd.mrn)
                with s.open(mode="wb") as file:
                    pickle.dump(COLON_32228, file)


def in_and_out_calculater(pd):
    """Calculate formatted in and out times given time in theatre.
    Don't overwrite if a resend"""

    global finish_time

    today_str = today.strftime("%Y-%m-%d")
    today_webshelf_path = epdata_path / "webshelf" / today_str

    try:
        with shelve.open(str(today_webshelf_path)) as s:
            data = s[pd.mrn]
            overwrite_flag = False
    except FileNotFoundError:
        overwrite_flag = False
    except KeyError:
        overwrite_flag = True

    if not overwrite_flag:
        in_formatted = data["in_theatre"]
        out_formatted = data["out_theatre"]
    else:
        time_in_theatre = int(pd.op_time)
        nowtime = datetime.datetime.now()
        outtime = nowtime + relativedelta(minutes=+1)
        intime = nowtime + relativedelta(minutes=-time_in_theatre)
        if finish_time and (finish_time > intime):
            intime = finish_time + relativedelta(minutes=+3)
        finish_time = outtime
        out_formatted = outtime.strftime("%H" + ":" + "%M")
        in_formatted = intime.strftime("%H" + ":" + "%M")

    pd.in_theatre = in_formatted
    pd.out_theatre = out_formatted
    return pd


def web_shelver(pd):
    """Write episode  data to a shelf.
    Used to write short and long web pages.
    """

    a_surname = pd.anaesthetist.split()[-1]
    e_surname = pd.endoscopist.split()[-1]
    sh_docs = e_surname + "/" + a_surname

    if not pd.consult:
        sh_consult = ""
    else:
        sh_consult = pd.consult
    if not pd.upper:
        sh_upper = ""
    else:
        sh_upper = pd.upper
    if not pd.colon:
        sh_colon = ""
    else:
        sh_colon = pd.colon
    if not pd.banding:
        sh_banding = ""
    else:
        sh_banding = pd.banding

    episode_dict = {
        "in_theatre": pd.in_theatre,
        "out_theatre": pd.out_theatre,
        "doctors": sh_docs,
        "name": pd.full_name,
        "asa": pd.asa,
        "consult": sh_consult,
        "upper": sh_upper,
        "colon": sh_colon,
        "polyp": pd.polyp,
        "banding": sh_banding,
        "nurse": pd.nurse,
        "varix_lot": pd.varix_lot,
        "message": pd.message,
        "billed": "",
    }

    today_str = today.strftime("%Y-%m-%d")
    today_path = epdata_path / "webshelf" / today_str
    try:
        with shelve.open(str(today_path)) as s:
            s[pd.mrn] = episode_dict
    except KeyError as e:
        pmb.alert("Try again. Program faulty.")
        logging.error(f"Trouble writing to web shelf: {e}")
        raise BillingException

    return today_path


def make_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for web page of today's patients
    from shelf data
    """
    today_str = today.strftime("%A" + "  " + "%d" + "-" + "%m" + "-" + "%Y")

    with shelve.open(str(today_path)) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x["out_theatre"], reverse=True)

    path_to_template = epdata_path
    loader = FileSystemLoader(path_to_template)
    env = Environment(loader=loader)
    template_name = "web_sec_template.html"
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open(sec_web_page, "w", encoding="utf-8") as f:
        f.write(a)


def make_long_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for complete info on today's patients
    """
    today_str = today.strftime("%A" + "  " + "%d" + "-" + "%m" + "-" + "%Y")

    with shelve.open(str(today_path)) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x["out_theatre"], reverse=True)

    path_to_template = epdata_path
    loader = FileSystemLoader(path_to_template)
    env = Environment(loader=loader)
    template_name = "web_sec_long_template.html"
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open(sec_long_web_page, "w", encoding="utf-8") as f:
        f.write(a)
    file_date = today.strftime("%Y" + "-" + "%m" + "-" + "%d") + ".html"
    file_str = epdata_path / "html-backup" / file_date
    with open(file_str, "w", encoding="utf-8") as f:
        f.write(a)


def day_surgery_shelver(pd):
    """Write episode  data to a shelf.
    Used by watcher.py to dump data in day surgery.
    """
    dumper_path = epdata_path / "dumper_data.db"
    try:
        with shelve.open(str(dumper_path)) as s:
            s[pd.mrn] = {
                "in_theatre": pd.in_theatre,
                "out_theatre": pd.out_theatre,
                "anaesthetist": pd.anaesthetist,
                "endoscopist": pd.endoscopist,
                "asa": pd.asa,
                "upper": pd.upper_for_daysurgery,
                "colon": pd.colon_for_daysurgery,
                "banding": pd.banding,
                "nurse": pd.nurse,
                "clips": pd.clips,
                "varix_lot": pd.varix_lot,
                "message": pd.message,
            }
    except ValueError as e:
        pmb.alert(
            text="""There was any error in the database. Try deleting the following files.
                  D:/JOHN TILLET/episode_data/dumper_data.db.dir
                  D:/JOHN TILLET/episode_data/dumper_data.db.dat
                  D:/JOHN TILLET/episode_data/dumper_data.db.bak"""
        )
        logging.error(f"Trouble writing to day surgery shelf: {e}")
        raise BillingException


def update_csv(
    filename, new_row, data_1, data_2, compare_1=0, compare_2=2, headers=False
):
    """updates a csv without creating duplicates.
    compares 2 pieces of date from new_row with their equivalents
    by position in the csv."""
    # Create temporary file
    temp_file = NamedTemporaryFile(mode="w", delete=False, newline="")

    found = False
    try:
        with open(filename, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, dialect="excel", lineterminator="\n")
            writer = csv.writer(temp_file)
            if headers:
                first_row = next(reader)
                writer.writerow(first_row)
            # Check each row
            for row in reader:
                if row[compare_1] == data_1 and row[compare_2] == data_2:
                    # Replace matching row with new data
                    writer.writerow(new_row)
                    found = True

                else:
                    writer.writerow(row)

            # Add new row if no match was found
            if not found:
                writer.writerow(new_row)
    except FileNotFoundError:
        writer = csv.writer(temp_file)
        writer.writerow(new_row)

    # Replace original file with updated temp file
    temp_file.close()
    shutil.move(temp_file.name, filename)


def update_episodes_csv(pd):
    today_str_for_ds = today.strftime("%d-%m-%Y")
    an = pd.anaesthetist.split()[-1]
    en = pd.endoscopist.split()[-1]
    asa = pd.asa
    if asa == "":
        asa = "0"
    else:
        asa = asa[-2]
    up = pd.upper
    if up != "":
        up = up.split("-")[0]
    nu = pd.nurse.split()[-1]

    if pd.pe_recall == 0:
        p_rec = ""
    else:
        weeks = pd.pe_recall * 52
        p_rec = today + datetime.timedelta(weeks=weeks)
        p_rec = p_rec.isoformat()

    if pd.col_recall == 0:
        c_rec = ""
    else:
        weeks = pd.col_recall * 52
        c_rec = today + datetime.timedelta(weeks=weeks)
        c_rec = c_rec.isoformat()

    new_row = [
        today_str_for_ds,
        pd.mrn,
        pd.in_theatre,
        pd.out_theatre,
        an,
        en,
        asa,
        up,
        pd.colon,
        pd.banding,
        nu,
        pd.clips,
        p_rec,
        c_rec,
        pd.caecum_reason_flag,
        pd.title,
        pd.first_name,
        pd.last_name,
        pd.dob,
        pd.email,
    ]

    csv_address = epdata_path / "episodes.csv"
    if not "test" in pd.message.lower():
        update_csv(
            csv_address,
            new_row,
            today_str_for_ds,
            pd.mrn,
            compare_1=0,
            compare_2=1,
            headers=True,
        )


def update_caecum_csv(pd):
    """Write whether scope got to caecum. For QPS"""
    today_str = today.strftime("%Y-%m-%d")
    doctor = pd.endoscopist.split()[-1]
    if pd.caecum_reason_flag != "success":
        caecum_flag = "fail"
    else:
        caecum_flag = "success"
    caecum_data = (today_str, doctor, pd.mrn, caecum_flag, pd.caecum_reason_flag)
    update_csv(
        caecum_csv_file, caecum_data, today_str, pd.mrn, compare_1=0, compare_2=2
    )


def update_medtitrust_csv(pd):
    """Turn raw data into stuff ready to go into meditrust csv file."""
    if (
        pd.insur_code in {"adf", "bill_given", "send_bill"}
        and pd.anaesthetist == "Dr J Tillett"
    ):
        return None

    phone = ""
    workcover_name = ""
    workcover_claim_no = ""
    veterans_no = ""
    if pd.asa == "92515-39":
        asa3 = True
    else:
        asa3 = False

    if pd.upper and not pd.colon and not asa3:
        procedure = "Panendoscopy"
    elif pd.upper and not pd.colon and asa3:
        procedure = "Panendoscopy, ASA3"
    elif pd.upper and pd.colon and not asa3:
        procedure = "Panendoscopy, Colonoscopy"
    elif pd.upper and pd.colon and asa3:
        procedure = "Panendoscopy, Colonoscopy, ASA3"
    elif not pd.upper and pd.colon and not asa3:
        procedure = "Colonoscopy"
    elif not pd.upper and pd.colon and asa3:
        procedure = "Panendoscopy, Colonoscopy, ASA3"

    if pd.insur_code == "bb":
        bill_type = "MEDICARE_FEE"
        med_fund = ""
        med_fund_number = ""
        med_mcn = pd.mcn
        med_ref = pd.ref

    elif pd.insur_code in {
        "adf",
        "send_bill",
        "bill_given",
        "va",
    }:
        bill_type = "NO_GAP_FEE"
        if pd.insur_code == "va":
            veterans_no = pd.mcn
        med_mcn = ""
        med_ref = ""
        med_fund = ""
        med_fund_number = ""
    elif pd.insur_code == "no_gap":
        bill_type = "NO_GAP_FEE"
        med_fund_number = pd.fund_number
        med_mcn = pd.mcn
        med_ref = pd.ref
        if pd.fund == "Bupa":
            med_fund = "BUPA - NO GAP"
        elif pd.fund == "Hcf":
            med_fund = "HCF (NG scheme)"
        else:
            med_fund = pd.fund

    meditrust_csv = (
        pd.title,
        pd.first_name,
        pd.last_name,
        pd.dob,
        pd.street,
        pd.suburb,
        pd.state,
        pd.postcode,
        phone,
        pd.email,
        procedure,
        med_mcn,
        med_ref,
        pd.in_theatre,
        pd.out_theatre,
        bill_type,
        med_fund,
        med_fund_number,
        workcover_name,
        workcover_claim_no,
        veterans_no,
    )

    endoscopist_surname = pd.endoscopist.split()[-1]
    endoscopist_lowered = endoscopist_surname.lower().title()
    today_str = today.strftime("%d-%m-%Y")
    a_surname = pd.anaesthetist.split()[-1]
    filename = today_str + "-" + endoscopist_lowered + ".csv"
    csvfile = epdata_path / "meditrust" / a_surname / filename
    update_csv(
        csvfile, meditrust_csv, pd.first_name, pd.last_name, compare_1=1, compare_2=2
    )


def get_time_code(pd):
    """Calculate medicare time code from time in theatre.
    op_time is an int
    returns time_code as a string"""
    op_time = int(pd.op_time)
    time_base = "230"
    time_last = "10"
    second_last_digit = 1 + op_time // 15
    if op_time % 15 == 0:
        second_last_digit -= 1

    if op_time > 15:
        time_last = "{}5".format(second_last_digit)
    time_code = time_base + time_last
    return time_code


def get_age_difference(pd):
    """Is patients 75 or older?"""
    dob = pd.dob
    dob = parse(dob, dayfirst=True)
    age_sep = relativedelta(today, dob)
    return age_sep.years


def update_anaesthetic_csv(pd):
    """Turn raw data into stuff ready to go into anaesthetic csv file."""
    today_for_invoice = today.strftime("%d" + "-" + "%m" + "-" + "%Y")
    age_diff = get_age_difference(pd)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = "No"

    if pd.upper:
        upper_done = "upper_Yes"  # this goes to jrt csv file
    else:
        upper_done = "upper_No"
    if pd.colon:
        lower_done = "lower_Yes"
    else:
        lower_done = "lower_No"
    if pd.asa[-2] == "3":
        asa_three = "asa3_Yes"
    elif pd.asa[-2] == "4":
        asa_three = "asa3_Four"
    elif pd.asa[-2] in {"1", "2"}:
        asa_three = "asa3_No"
    if age_diff >= 75:
        age_seventy = "age70_Yes"
    else:
        age_seventy = "age70_No"
    #    if insur_code == 'os':  # get rid of mcn in reciprocal mc patients
    #        mcn = ''

    time_code = get_time_code(pd)

    invoice = random.randint(0, 10000)
    invoice = "DEC" + str(invoice)

    ae_csv = (
        today_for_invoice,
        pd.full_name,
        pd.full_address,
        pd.dob,
        pd.mcn,
        pd.ref,
        pd.fund,
        pd.fund_number,
        pd.insur_code,
        pd.endoscopist,
        upper_done,
        lower_done,
        age_seventy,
        asa_three,
        time_code,
        invoice,
    )

    surname = pd.anaesthetist.split()[-1] + ".csv"
    filename = epdata_path / "sedation" / surname
    update_csv(
        filename, ae_csv, today_for_invoice, pd.full_name, compare_1=0, compare_2=1
    )
    return ae_csv


def render_anaesthetic_report(anaesthetist):
    """Make a web page if billing anaesthetist showing patients done today."""
    anaes_surname = anaesthetist.split()[-1]
    today_data = []
    count = 0
    csv_length = 0
    today_date = today.strftime("%d" + "-" + "%m" + "-" + "%Y")
    csvfile = epdata_path / "sedation" / f"{anaes_surname}.csv"
    with open(csvfile) as f:
        reader = csv.reader(f)
        for episode in reader:
            csv_length += 1
            if episode[0] == today_date:
                count += 1
                today_data.append(episode)
    path_to_template = epdata_path
    loader = FileSystemLoader(path_to_template)
    env = Environment(loader=loader)
    template_name = "anaesthetic_report_template.html"
    template = env.get_template(template_name)
    a = template.render(
        today_data=today_data,
        today_date=today_date,
        count=count,
        anaes_surname=anaes_surname,
        csv_length=csv_length,
    )

    report_file = epdata_path / "sedation" / f"{anaes_surname}.html"
    with open(report_file, "w") as f:
        f.write(a)


def print_receipt(anaesthetist, episode):
    """Print a receipt if overseas patient."""
    headers = [
        "date",
        "name",
        "address",
        "dob",
        "medicare_no",
        "ref",
        "fund_name",
        "fund_number",
        "fund_code",
        "doctor",
        "upper",
        "lower",
        "seventy",
        "asa_3",
        "time",
        "invoice",
    ]
    episode = dict(zip(headers, episode))

    (grand_total, consult_as_float, unit, time_fee, total_fee) = decbatches.process_acc(
        0.0, episode
    )

    doc = docx.Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Verdana"
    acc = decbatches.print_account(
        episode,
        doc,
        unit,
        consult_as_float,
        time_fee,
        total_fee,
        anaesthetist,
        page_break=False,
    )
    name = episode["name"]
    name = name.split()[-1]
    today_str = today.strftime("%Y-%m-%d")
    printfile = epdata_path / "sedation" / "accounts" / f"{name}_{today_str}.docx"
    acc.save(printfile)


class PersistentEntryDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)

        # Make this window stay on top
        self.transient(parent)
        self.grab_set()

        # Set window properties
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # Create and place widgets
        tk.Label(self, text=prompt).pack(padx=10, pady=10)

        # Use Entry widget for single-line input
        self.entry = tk.Entry(self, width=40)
        self.entry.pack(padx=10, pady=10)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(padx=10, pady=10)

        # OK and Restart buttons
        tk.Button(button_frame, text="OK", width=10, command=self.ok).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Restart", width=10, command=self.cancel).pack(
            side=tk.LEFT, padx=5
        )

        # Set focus to the entry
        self.entry.focus_set()

        # Center the window
        self.center_window()

        # Initialize result
        self.result = None

        # Wait for the window to be destroyed
        self.wait_window(self)

    def ok(self):
        # Get the text from the entry
        self.result = self.entry.get()
        if not self.result:
            self.result = ""
        self.destroy()

    def cancel(self):
        # Set result to "" and destroy the window
        self.result = ""
        self.destroy()

    def center_window(self):
        # Update to ensure the window size is calculated
        self.update_idletasks()

        # Get the window size and screen dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the window position
        self.geometry(f"{width}x{height}+{x}+{y}")


def get_manual_data(
    root, title="Manual Entry", prompt="Please enter the data manually:"
):
    """
    Show a dialog to get manual data entry from the user.
    Returns the entered data or None if cancelled.
    """
    dialog = PersistentEntryDialog(root, title, prompt)
    # if not dialog:
    #     raise BillingException
    # else:
    return dialog.result


def scraper(email=False):
    """Three goes at copying data. If fail return 'na'"""
    result = "na"
    pya.hotkey("ctrl", "c")
    result = pyperclip.paste()
    if email:
        result = re.split(r"[\s,:/;\\]", result)[0]
        if not is_email(result):
            result = ""

    return result


def postcode_to_state(sd):
    post_dic = {"3": "VIC", "4": "QLD", "5": "SA", "6": "WA", "7": "TAS"}
    postcode = sd.postcode
    try:
        if postcode[0] == "0":
            if postcode[:2] in {"08", "09"}:
                return "NT"
            else:
                return ""
        elif postcode[0] in {"0", "1", "8", "9"}:
            return ""
        elif postcode[0] == "2":
            if (2600 <= int(postcode) <= 2618) or postcode[:2] == 29:
                return "ACT"
            else:
                return "NSW"
        else:
            return post_dic[postcode[0]]
    except Exception:
        return ""


def patient_id_scrape(sd):
    """Scrape names, mrn, dob, email from blue chip."""
    pya.moveTo(TITLE_POS)
    # x1, y1 = TITLE_POS
    # fix_pos = x1, y1, x1 +1, y1 +1
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.doubleClick()
    sd.title = scraper()

    pya.press("tab")
    sd.first_name = scraper()

    pya.press("tab")
    pya.press("tab")
    time.sleep(1)
    sd.last_name = scraper()

    # enable_mouse()
    pya.moveTo(MRN_POS)
    # x1, y1 = MRN_POS
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.doubleClick()
    sd.mrn = scraper()

    # enable_mouse()
    pya.moveTo(DOB_POS)
    # x1, y1 = DOB_POS
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.doubleClick()
    sd.dob = scraper()

    pya.press("tab", presses=10)
    sd.email = scraper(email=True)

    return sd


def address_scrape(sd):
    """Scrape address from blue chip.
    Used if billing anaesthetist.
    """
    # need to work out how to click/tab here from email box
    pya.keyDown("shift")
    pya.press("tab", presses=8)
    pya.keyUp("shift")
    sd.street = scraper()
    sd.street = sd.street.replace(",", "")

    pya.press("tab")
    pya.press("tab")
    sd.suburb = scraper()

    # enable_mouse()
    pya.moveTo(POST_CODE_POS, duration=0.1)
    x1, y1 = POST_CODE_POS
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.doubleClick()
    sd.postcode = scraper()

    sd.state = postcode_to_state(sd)

    return sd


def scrape_mcn_and_ref(sd):
    """Scrape mcn from blue chip."""
    pya.press("tab", presses=11)
    sd.mcn = scraper()
    sd.mcn = sd.mcn.replace(" ", "")

    pya.press("tab", presses=2)
    sd.ref = scraper()

    return sd


def scrape_fund_number(sd):
    """Scrape fund number from blue chip."""
    # enable_mouse()
    pya.moveTo(FUND_NO_POS, duration=0.1)
    x1, y1 = FUND_NO_POS
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.doubleClick()
    sd.fund_number = scraper()
    # enable_mouse()

    return sd


def close_out(anaesthetist):
    """Close patient file with mouse click and display billing details
    if a billing anaesthetist."""
    # enable_mouse()
    pya.moveTo(CLOSE_POS[0], CLOSE_POS[1])
    # x1, y1 = CLOSE_POS[0], CLOSE_POS[1]
    # disable_mouse(x1, y1, x1 + 1, y1 + 1)
    pya.click()
    # time.sleep(0.25)
    pya.hotkey("alt", "n")
    # enable_mouse()
    pya.moveTo(x=780, y=110)
    if anaesthetist in BILLING_ANAESTHETISTS:
        anaes_surname = anaesthetist.split()[-1]
        webbrowser.open(
            f"d:\\john tillet\\episode_data\\sedation\\{anaes_surname}.html".format(
                anaesthetist.split()[-1]
            )
        )


# def add_recall(proc, pd):
#     print("recall", proc)


def add_recall(proc, pd):
    date = today.strftime("%d/%m/%Y")
    doc = pd.endoscopist.split()[-1].lower()
    if proc == "colon":
        years = pd.col_recall
    else:
        years = pd.pe_recall
    pya.click(100, 400)
    pya.press("up", presses=3)
    pya.press("enter")
    pya.hotkey("alt", "n")
    pya.hotkey("alt", "a")
    proc_num = RECALL_PROC[proc]
    pya.press("down", presses=proc_num)
    pya.press("tab")
    doc_num = DEC_ENDOSCOPISTS[doc]
    pya.press("down", presses=doc_num)
    pya.press("tab", presses=2)
    pya.write(YEARS_TO_WEEKS[years])
    pya.press("tab", presses=4)
    pya.write(pd.upper)
    pya.write("  ")
    pya.write(pd.colon)
    pya.write("  ")
    pya.write(date)
    pya.keyDown("shift")
    pya.press("tab", presses=2)
    pya.keyUp("shift")
    pya.press("enter")


def runner(*args):
    """Main program. Runs when button pushed."""
    global overide_endoscopist  # for future endoscopist check
    global finish_time
    global biller_anaesthetist_flag

    btn_txt.set("Sending...")
    feedback["text"] = "Sending data" + ("  " * 20)
    root.update_idletasks()
    try:
        # data from gui, then process it (inside the dataclass ProcedureData)
        proc_data = ProcedureData.from_string_vars(
            an, end, nur, up, co, ba, asc, po, caecum, con, mes, cl, ot
        )

        proc_data = patient_id_scrape(proc_data)

        # scraping checks

        if "na" in {
            proc_data.title,
            proc_data.first_name,
            proc_data.last_name,
            proc_data.dob,
            proc_data.mrn,
            proc_data.email,
        }:
            raise ScrapingException
        if proc_data.first_name == proc_data.last_name:
            # resp = pmb.confirm(text=f'Patient first name and second name are the same - {
            #                    proc_data.first_name} ? error', title='', buttons=['Continue', 'Go Back'])
            # if resp == "Go Back":
            #     raise BillingException
            raise ScrapingException

        if not proc_data.mrn.isdigit():
            raise ScrapingException
        try:
            parse(proc_data.dob, dayfirst=True)
        except Exception:
            raise ScrapingException

        # double check
        if (
            proc_data.mrn in double_set
            and not (proc_data.upper and proc_data.colon)
            and "cancelled" not in proc_data.message
        ):
            pya.alert(
                text="Patient booked for Double. Choose either a procedure or cancelled for both.",
                title="",
                button="OK",
            )
            raise BillingException

        # Doctor check

        # Time since last colon check
        try:
            update_and_verify_last_colon(proc_data)
        except ValueError:
            logging.error("?Corrupt last_colon_date database.", exc_info=True)
            raise BillingException

        proc_data.full_name = (
            proc_data.title + " " + proc_data.first_name + " " + proc_data.last_name
        )

        proc_data = in_and_out_calculater(proc_data)

        # make secretaries' web page
        today_path = web_shelver(proc_data)
        make_web_secretary_from_shelf(today_path)
        make_long_web_secretary_from_shelf(today_path)

        # make Blue Chip day surgery module dumper
        day_surgery_shelver(proc_data)

        # make episodes.csv
        update_episodes_csv(proc_data)

        # make caecum.csv
        if proc_data.caecum_reason_flag:
            update_caecum_csv(proc_data)

        # anaesthetic billing
        if proc_data.asa and proc_data.anaesthetist in BILLING_ANAESTHETISTS:
            proc_data = address_scrape(proc_data)
            if "na" in {
                proc_data.street,
                proc_data.suburb,
                proc_data.postcode,
            }:
                raise ScrapingException
            proc_data.full_address = (
                proc_data.street
                + " "
                + proc_data.suburb
                + " "
                + proc_data.state
                + " "
                + proc_data.postcode
            )

            if proc_data.insur_code in {"adf", "bill_given"}:
                proc_data.mcn = ""
            elif proc_data.insur_code in {"bb", "va"}:
                proc_data.fund_number = ""
                proc_data = scrape_mcn_and_ref(proc_data)
            elif proc_data.insur_code in {"send_bill"}:
                proc_data.mcn = ""
                proc_data = scrape_fund_number(proc_data)
            else:
                proc_data = scrape_mcn_and_ref(proc_data)
                proc_data = scrape_fund_number(proc_data)

            if proc_data.mcn == "na":
                proc_data.mcn = get_manual_data(
                    root, title="Manual Entry", prompt="Please enter the MCN."
                )

            if proc_data.ref == "na":
                proc_data.ref = get_manual_data(
                    root, title="Manual Entry", prompt="Please enter the REF."
                )

            if proc_data.fund_number == "na":
                proc_data.fund_number = get_manual_data(
                    root,
                    title="Manual Entry",
                    prompt="Please enter the Fund Number.",
                )

            # ? make patient ID database

            # anaesthetic_tuple used by print_receipt
            anaesthetic_tuple = update_anaesthetic_csv(proc_data)
            render_anaesthetic_report(proc_data.anaesthetist)

            update_medtitrust_csv(proc_data)

            if proc_data.insur_code == "bill_given":
                print_receipt(proc_data.anaesthetist, anaesthetic_tuple)

        # write recalls
        if proc_data.pe_recall == proc_data.col_recall and proc_data.pe_recall != 0:
            add_recall("double", proc_data)
        else:
            if proc_data.pe_recall != 0:
                add_recall("upper", proc_data)
            if proc_data.col_recall != 0:
                add_recall("colon", proc_data)

        # time.sleep(10)
        # close_out(proc_data.anaesthetist)

        # # alert secretaries of new patient
        # to_watched()
        # send_name = proc_data.full_name
        # requests.post(
        #     "https://ntfy.sh/dec601billing",
        #     data=f"{send_name} 😀".encode(encoding="utf-8"),
        # )
        pprint(proc_data)

    except ScrapingException:
        messagebox.showerror(message="Error in data. Try again.")
        btn_txt.set("Try Again")
        root.update_idletasks()
        logging.error("Scraping error")
        return

    except BillingException:
        btn_txt.set("Try Again")
        root.update_idletasks()
        logging.error("Billing error")
        return

    except Exception as e:
        messagebox.showerror(message="Error in data. Try again.")
        logging.error("Error in main loop", exc_info=True)
        btn_txt.set("Try Again")
        feedback["text"] = f"{e}"
        root.update_idletasks()
        requests.post(
            "https://ntfy.sh/dec601doclog", data=f"{e}".encode(encoding="utf-8")
        )
        return

    asc.set("ASA")
    up.set("No Upper")
    co.set("No Lower")
    po.set("Colon Pathology")
    ba.set("No Anal Procedure")
    cl.set("0")
    caecum.set("")
    mes.set("")
    ot.set("-3")
    fu.set("")
    fail_text_label.set("")
    caecum_box.grid_remove()
    ba_box.grid_remove()
    path_box.grid_remove()
    btn.config(text="Send!")
    per.set("? Pe recall")
    pe_recall.grid_remove()
    colr.set("? Col recall")
    col_recall.grid_remove()
    mess_box.grid_remove()
    if proc_data.endoscopist in BILLING_ENDOSOSCOPISTS:
        con_label.grid()
        con_button1.grid()
        con_button2.grid()
        con.set("None")
    else:
        con.set("No need")
    if biller_anaesthetist_flag:
        fund_box.grid()
        fu.set("Fund")
    btn_txt.set("Select Procedure")
    btn.config(state="disabled")
    feedback["text"] = "Select Procedure"
    # end of runner


# with concurrent.futures.ThreadPoolExecutor() as executor:
#     print("starting download")
#     future = executor.submit(download_and_process)

thread = threading.Thread(target=download_and_process)
thread.start()
print("starting download")

print("starting gui")
root = Tk()
root.title(today.strftime("%A  %d/%m/%Y"))

if user == "John2":
    root.geometry("470x600+840+50")
elif user == "John":
    root.geometry("600x630+1160+100")
else:  #
    root.geometry("650x480+660+100")
root.option_add("*tearOff", FALSE)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

menubar = Menu(root)
root.config(menu=menubar)
# force menubar to windows style on mac remove the following in production
try:
    root.tk.call("::tk::unsupported::MacWindowStyle", "useGuiMenus", 0)
except tk.TclError:
    pass
menu_message = Menu(menubar)
menu_extras = Menu(menubar)
menu_admin = Menu(menubar)
menu_accounts = Menu(menubar)

menubar.add_cascade(menu=menu_message, label="Message")
menu_message.add_command(label="Add Message", command=add_message)

menubar.add_cascade(menu=menu_extras, label="Extras")
menu_extras.add_command(label="Roster", command=open_roster)
menu_extras.add_command(label="Patients Done Today", command=open_today)
menu_extras.add_command(label="Dox", command=open_dox)
menu_extras.add_command(label="Anaesthetists Details", command=open_weekends)

menubar.add_cascade(menu=menu_admin, label="Admin")
menu_admin.add_command(label="Delete Record", command=delete_record)
menu_admin.add_command(label="Error Log", command=error_log)
menu_admin.add_command(label="Add Staff", command=add_staff)

menubar.add_cascade(menu=menu_accounts, label="Accounts")
menu_accounts.add_command(label="receipts folder", command=open_receipt)
menu_accounts.add_command(label="meditrust folder", command=open_sedation)
menu_accounts.add_command(label="Start batches print", command=start_decbatches)
menu_accounts.add_command(label="Meditrust Website", command=open_meditrust)


an = StringVar()
an.trace("w", button_enable)
end = StringVar()
end.trace("w", button_enable)
nur = StringVar()
nur.trace("w", button_enable)
pat = StringVar()
pat.trace("w", button_enable)
asc = StringVar()
asc.trace("w", button_enable)
up = StringVar()
up.trace("w", button_enable)
co = StringVar()
co.trace("w", button_enable)
po = StringVar()
po.trace("w", button_enable)
caecum = StringVar()
caecum.trace("w", button_enable)
ba = StringVar()
cl = StringVar()
con = StringVar()
con.trace("w", button_enable)
per = StringVar()
per.trace("w", button_enable)
colr = StringVar()
colr.trace("w", button_enable)
mes = StringVar()
ot = StringVar()
fu = StringVar()
fu.trace("w", button_enable)
fail_text_label = StringVar()
btn_txt = StringVar()

topframe = Frame(mainframe, bg="green", pady=7)
topframe.grid(column=0, row=0, sticky=(N, W, E, S))
topframe.columnconfigure(0, weight=1)
topframe.rowconfigure(0, weight=1)

midframe = Frame(mainframe)
midframe.grid(column=0, row=2, sticky=(N, W, E, S))
midframe.columnconfigure(0, weight=1)
midframe.rowconfigure(0, weight=1)

bottomframe = Frame(mainframe)
bottomframe.grid(column=0, row=3, sticky=(N, W, E, S))
bottomframe.columnconfigure(0, weight=1)
bottomframe.rowconfigure(0, weight=1)

ana_box = ttk.Combobox(topframe, textvariable=an)
ana_box["values"] = ANAESTHETISTS
ana_box["state"] = "readonly"
ana_box.grid(column=0, row=0, sticky=W)
ana_box.bind("<<ComboboxSelected>>", is_biller_anaesthetist)

end_box = ttk.Combobox(topframe, textvariable=end)
end_box["values"] = ENDOSCOPISTS
end_box["state"] = "readonly"
end_box.grid(column=1, row=0, sticky=W)
end_box.bind("<<ComboboxSelected>>", is_biller_endoscopist)

nur_box = ttk.Combobox(topframe, textvariable=nur)
nur_box["values"] = NURSES
nur_box["state"] = "readonly"
nur_box.grid(column=2, row=0, sticky=W)


space = "              " * 3
ttk.Label(midframe, text=space).grid(column=2, row=0, sticky=E)  # place holder

up_box = ttk.Combobox(midframe, textvariable=up, width=20)
up_box["values"] = UPPERS
up_box["state"] = "readonly"
up_box.bind("<<ComboboxSelected>>", upper_combo_click)
up_box.grid(column=0, row=1, sticky=W)

col_box = ttk.Combobox(midframe, textvariable=co, width=20)
col_box["values"] = COLONS
col_box["state"] = "readonly"
col_box.bind("<<ComboboxSelected>>", colon_combo_click)
col_box.grid(column=1, row=1, sticky=W)

ba_box = ttk.Combobox(midframe, textvariable=ba, width=20)
ba_box["values"] = BANDING
ba_box["state"] = "readonly"
ba_box.grid(column=2, row=1, sticky=W)


# fontExample = ("Courier", 16, "bold")
asa_box = ttk.Combobox(midframe, textvariable=asc, width=14)
asa_box["values"] = ASA
asa_box["state"] = "readonly"
asa_box.bind("<<ComboboxSelected>>", asa_click)
asa_box.grid(column=0, row=2, sticky=W)

ttk.Label(midframe, text="     ").grid(column=1, row=2, sticky=W)

con_label = ttk.Label(midframe, text="Consult")
con_label.grid(column=1, row=2, sticky=W)

con_button1 = ttk.Radiobutton(midframe, text="Yes", variable=con, value="Consult")
con_button1.grid(column=1, row=2)

con_button2 = ttk.Radiobutton(midframe, text="No", variable=con, value="No Consult")
con_button2.grid(column=1, row=2, sticky=E)

path_box = ttk.Combobox(midframe, textvariable=po, width=20)
path_box["values"] = ["No colon pathology", "Biopsy", "Polypectomy"]
path_box["state"] = "readonly"
path_box.grid(column=2, row=2)

lti = ttk.Label(midframe, text="Time")
lti.grid(column=0, row=3, sticky=W)

ti = Spinbox(midframe, from_=0, to=120, textvariable=ot, width=5)
ti.grid(column=0, row=3)
lti2 = ttk.Label(midframe, text="    ")
lti2.grid(column=0, row=3, sticky=E)

ttk.Label(midframe, text="Clips").grid(column=1, row=3, sticky=W)

s_box = Spinbox(midframe, from_=0, to=30, textvariable=cl, width=5)
s_box.grid(column=1, row=3)
ttk.Label(midframe, text="     ").grid(column=1, row=3, sticky=E)

# recalls
pe_recall = ttk.Combobox(midframe, textvariable=per, width=20)
pe_recall["values"] = ["No Pe recall", "1 year", "2 years", "3 years", "5 years"]
pe_recall["state"] = "readonly"
pe_recall.grid(column=0, row=4, sticky=W)

col_recall = ttk.Combobox(midframe, textvariable=colr, width=20)
col_recall["values"] = ["No colon recall", "1 year", "2 years", "3 years", "5 years"]
col_recall["state"] = "readonly"
col_recall.grid(column=1, row=4, sticky=W)


# failure to reach caecum label
boldStyle = ttk.Style()
boldStyle.configure("Bold.TLabel", size=20, weight="bold")
fail_label = ttk.Label(midframe, textvariable=fail_text_label, style="Bold.TLabel")
fail_label.grid(column=2, row=3, sticky=W)

caecum_box = ttk.Combobox(midframe, textvariable=caecum, width=20)
caecum_box["values"] = [
    "Poor Prep",
    "Loopy",
    "Obstruction",
    "Diverticular Disease",
    "Other",
]
caecum_box["state"] = "readonly"
caecum_box.grid(column=2, row=4)


mess_box = ttk.Entry(bottomframe, textvariable=mes, width=30)
mess_box.grid(column=0, row=0, sticky=W)

fund_box = ttk.Combobox(bottomframe, textvariable=fu, width=30)
fund_box["values"] = FUNDS
fund_box.grid(column=0, row=1, sticky=W)

btn = ttk.Button(bottomframe, textvariable=btn_txt, command=runner)
btn.grid(column=0, row=2, sticky=W)
btn_txt.set("Missimg data")
btn.config(state="disabled")
# orig_color = btn.cget("bg")

space = "              " * 3
ttk.Label(bottomframe, text=space).grid(column=2, row=3, sticky=E)  # place holder

feedback = ttk.Label(bottomframe, text="Missing staff  data")
feedback.grid(column=0, row=4, sticky=W)


for child in topframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

for child in midframe.winfo_children():
    child.grid_configure(padx=5, pady=15)

for child in bottomframe.winfo_children():
    child.grid_configure(padx=5, pady=15)

an.set("Anaesthetist")
end.set("Endoscopist")
nur.set("Nurse")
asc.set("ASA")
up.set("No Upper")
co.set("No Lower")
po.set("Colon Pathology")
ba.set("No Anal Procedure")
caecum.set("")
cl.set("0")
per.set("? Pe recall")
colr.set("? Col recall")
con.set("None")
ot.set("0")
fail_text_label.set("")
path_box.grid_remove()
con_label.grid_remove()
con_button1.grid_remove()
con_button2.grid_remove()
caecum_box.grid_remove()
ba_box.grid_remove()
pe_recall.grid_remove()
col_recall.grid_remove()
mess_box.grid_remove()
fund_box.grid_remove()

update_spin()
root.attributes("-topmost", True)
root.mainloop()
