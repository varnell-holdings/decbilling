# -*- coding: utf-8 -*-
"""
Created on Wed May  6 13:10:40 2020

@author: John2
"""

# -*- coding: utf-8 -*-
"""Gui for dec billing."""

from configparser import ConfigParser
import concurrent.futures
import csv
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import logging
import os
import pickle
import shelve
import sys
import time
import webbrowser

from tkinter import ttk, StringVar, Tk, W, E, N, S, Spinbox, FALSE, Menu, Frame

# need this for boto3
sys.path.append("C:\\Users\\John2\\Miniconda3\\lib\\site-packages\\urllib3\\util\\")

import boto3
import docx
from jinja2 import Environment, FileSystemLoader
import pyautogui as pya
import pyperclip

from awsenv import aws_access_key_id, aws_secret_access_key

import decbatches

pya.PAUSE = 0.4
pya.FAILSAFE = False


class BillingException(Exception):
    pass


class MissingProcedureException(BillingException):
    pass


class NoBlueChipException(BillingException):
    pass


class TestingException(BillingException):
    pass


class NoNameException(BillingException):
    pass


class WrongDocException(BillingException):
    pass


class NoDoubleException(BillingException):
    pass

class TooSoonException(BaseException):
    pass


logging.basicConfig(
    filename="D:\\JOHN TILLET\\episode_data\\doclog.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)


today = datetime.datetime.today()

config_parser = ConfigParser(allow_no_value=True)
config_parser.read("d:\\john tillet\\episode_data\\STAFF.ini")

NURSES = config_parser.options("nurses")
NURSES = [a.title() for a in NURSES]
ENDOSCOPISTS = config_parser.options("endoscopists")
ENDOSCOPISTS = [a.title() for a in ENDOSCOPISTS]
ANAESTHETISTS = config_parser.options("anaesthetists")
ANAESTHETISTS = [a.title() for a in ANAESTHETISTS]

PATIENTS = []
selected_name = "error!"
manual_mrn = ""
manual_flag = False
equip_flag = False
overide_endoscopist = False
finish_time = False


BILLING_ANAESTHETISTS = ["Dr S Vuong", "Dr J Tillett"]

ASA = ["No Sedation", "ASA 1", "ASA 2", "ASA 3"]

ASA_DIC = {
    "No Sedation": None,
    "ASA 1": "92515-19",
    "ASA 2": "92515-29",
    "ASA 3": "92515-39",
}

UPPERS = [
    "No Upper",
    "Pe",
    "Pe with Bx",
    "Oesophageal diatation",
    "Pe with APC",
    "Pe with polypectomy",
    "Pe with varix banding",
    "BRAVO",
    "HALO",
    "Cancelled",
]

UPPER_DIC = {
    "No Upper": None,
    "Cancelled": None,
    "Pe": "30473-00",
    "Pe with Bx": "30473-01",
    "Oesophageal diatation": "30475-00",
    "Pe with APC": "30478-20",
    "HALO": "30478-20",
    "Pe with polypectomy": "30478-04",
    "Pe with varix banding": "30478-20",
    "BRAVO": "30490-00",
}

COLONS = [
    "No Lower",
    "Planned Short Colon",
    "Exam via stoma",
    "Failure to reach caecum",
    "Cancelled",
    "32222",
    "32223",
    "32224",
    "32225",
    "32226",
    "32227",
    "32228",
]

COLON_DIC = {
    "No Lower": None,
    "Planned Short Colon": "32084-00",
    "Exam via stoma": "32095-00",
    "Failure to reach caecum": "32084-00",
    "Cancelled": None,
    "32222": "32222",
    "32223": "32223",
    "32224": "32224",
    "32225": "32225",
    "32226": "32226",
    "32227": "32227",
    "32228": "32228",
}

BANDING = ["No Anal Procedure", "Banding", "Banding + Pudendal", "Anal dilatation"]

BANDING_DIC = {
    "No Anal Procedure": None,
    "Banding": "32135-00",
    "Banding + Pudendal": "32135-00",
    "Anal dilatation": "32153-00",
}

CONSULT_DIC = {"No Consult": None, "Consult": "110", "No need": None}

FUND_TO_CODE = {
    "HCF": "hcf",
    "BUPA": "bup",
    "Medibank Private": "mpl",
    "NIB": "nib",
    "Doctor's Health Fund": "ama",
    "Australian Health Management": "ahm",
    "Bulk Bill": "bb",
    "Pay Today NG": "paid",
    "Pay Today AMA": "paid_ama",
    "Veterans Affairs": "va",
    "Pay Later": "send_bill",
    "ADF HSC": "adf",
    "Grand United Corporate Health": "gu",
    "Latrobe Health": "lt",
    "Cessnock District or Hunter Health": "hh",
    "stlukeshealth": "sl",
}

FUNDS = [
    "Pay Later",
    "Pay Today NG",
    "Pay Today AMA",
    "Bulk Bill",
    "Veterans Affairs",
    "HCF",
    "BUPA",
    "Medibank Private",
    "NIB",
    "Australian Health Management",
    "ADF HSC",
    "Grand United Corporate Health",
    "Doctor's Health Fund",
    "+++++ ahsa funds ++++++++",
    "ACA Health",
    "AIA Health",
    "Australian Unity Health",
    "CBHS Health",
    "CUA Health",
    "Defence Health",
    "Emergency Services Health",
    "Frank Health",
    "GMHBA",
    "Health Insurance Fund of Australia",
    "Health Partners",
    "Health Care Insurance",
    "HBF",
    "myOwn Health",
    "Navy Health Ltd",
    "Onemedifund",
    "Peoplecare Health",
    "Pheonix Health",
    "Police Health",
    "Railway & Transport Health",
    "Reserve Bank",
    "Teachers Health Fund",
    "Teachers Union or QTH",
    "UniHealth",
    "Westfund",
    "++++ regional funds ++++",
    "Latrobe Health",
    "Cessnock District or Hunter Health",
    "stlukeshealth",
    "Queensland Country Health",
]

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


def pats_from_aws(date):
    try:
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ap-southeast-2",
        )

        s3.Object("dec601", "patients.csv").download_file("aws_data.csv")
    except Exception:
        logging.error("Failed to get patients list.", exc_info=False)
        bookings_dic = {}
        mrn_dic = {}
        pya.alert("Failed to get patients list.")
        return bookings_dic, mrn_dic

    #  bookings_dic maps endoscopists to a list of tuples of patient names and datestamps of data entry
    bookings_dic = {}
    mrn_dic = {}  #  this will map patient name to mrn
    double_dic = {}  # this will map mrn to double flag
    pat_doc_dic = (
        {}
    )  # map patient mrn  to doctor for check if correct doctor selected in combobox
    with open("aws_data.csv", encoding="utf-8") as h:
        reader = csv.reader(h)
        for patient in reader:
            doc = patient[1].lower()
            this_day = patient[0]

            if len(this_day) == 9:
                this_day = "0" + this_day

            if (this_day == date) or (this_day == "error"):
                #                print(patient)
                if doc in bookings_dic:
                    bookings_dic[doc].append((patient[3], patient[6]))
                else:
                    bookings_dic[doc] = []
                    bookings_dic[doc].append((patient[3], patient[6]))

                mrn_dic[patient[3]] = patient[2]
                double_dic[patient[2]] = patient[5]
                name_for_doc_dic = patient[3].split(", ")[0]
                name_for_doc_dic = name_for_doc_dic.split()[-1].lower()
                #                print(name_for_doc_dic)
                pat_doc_dic[patient[2]] = patient[1]
    return bookings_dic, mrn_dic, double_dic, pat_doc_dic


def in_and_out_calculater(time_in_theatre, mrn):
    """Calculate formatted in and out times given time in theatre.
    Don't overwrite if a resend"""

    global finish_time

    today_str = today.strftime("%Y-%m-%d")
    today_path = os.path.join(
        "d:\\JOHN TILLET\\episode_data\\webshelf\\" + today_str + "_19"
    )

    try:
        with shelve.open(today_path) as s:
            data = s[mrn]
            overwrite_flag = False
    except FileNotFoundError:
        overwrite_flag = False
    except KeyError:
        overwrite_flag = True

    if not overwrite_flag:
        in_formatted = data["in_theatre"]
        out_formatted = data["out_theatre"]
    else:
        time_in_theatre = int(time_in_theatre)
        nowtime = datetime.datetime.now()
        outtime = nowtime + relativedelta(minutes=+1)
        intime = nowtime + relativedelta(minutes=-time_in_theatre)
        if finish_time and (finish_time > intime):
            intime = finish_time + relativedelta(minutes=+3)
        finish_time = outtime
        out_formatted = outtime.strftime("%H" + ":" + "%M")
        in_formatted = intime.strftime("%H" + ":" + "%M")

    return (in_formatted, out_formatted)


def postcode_to_state(postcode):
    post_dic = {'3': 'VIC', '4': 'QLD', '5': 'SA', '6': 'WA', '7': 'TAS'}
    try:
        if postcode[0] == '0':
            if postcode[:2] in {'08', '09'}:
                return 'NT'
            else:
                return ''
        elif postcode[0] in {'0', '1', '8', '9'}:
            return ''
        elif postcode[0] == '2':
            if (2600 <= int(postcode) <= 2618) or postcode[:2] == 29:
                return 'ACT'
            else:
                return 'NSW'
        else:
            return post_dic[postcode[0]]
    except:
        return ''


def front_scrape():
    """Scrape name and mrn from blue chip.
    return tiltle, first_name, last_name for meditrust and printname for printed accounts"""

    pya.moveTo(TITLE_POS, duration=0.1)
    pya.doubleClick()
    title = pyperclip.copy("na")
    pya.hotkey("ctrl", "c")
    title = pyperclip.paste()

    if title == "na":
        pya.alert("Error reading Blue Chip.\nTry again\n?Logged in with AST")
        btn_txt.set("Try Again!")
        raise NoBlueChipException

    pya.press("tab")

    first_name = pyperclip.copy("na")
    pya.hotkey("ctrl", "c")
    first_name = pyperclip.paste()

    if first_name == "na":
        first_name = pya.prompt(
            text="Please enter patient first name", title="First Name", default=""
        )

    pya.press("tab")
    pya.press("tab")
    last_name = pyperclip.copy("na")
    pya.hotkey("ctrl", "c")
    last_name = pyperclip.paste()
    if last_name == "na":
        last_name = pya.prompt(
            text="Please enter patient surname", title="Surame", default=""
        )
    try:
        print_name = title + " " + first_name + " " + last_name
        print(print_name)
    except TypeError:
        pya.alert("Problem getting the name. Try again!")
        raise BillingException

    mrn = pyperclip.copy("na")
    pya.moveTo(MRN_POS, duration=0.1)

    pya.doubleClick()
    pya.hotkey("ctrl", "c")
    mrn = pyperclip.paste()
    print(mrn)

    mrn = pyperclip.paste()
    if not mrn.isdigit():
        mrn = pya.prompt("Please enter this patient's MRN")
    logging.info(f"Data returned by front_scrape {mrn}, {print_name}, {title}, {first_name}, {last_name}")

    return (mrn, print_name, title, first_name, last_name)



# def front_scrape():
#     """Scrape name and mrn from blue chip."""

#     pya.moveTo(TITLE_POS, duration=0.1)
#     pya.doubleClick()
#     title = pyperclip.copy("na")
#     pya.hotkey("ctrl", "c")
#     title = pyperclip.paste()

#     if title == "na":
#         pya.alert("Error reading Blue Chip.\nTry again\n?Logged in with AST")
#         btn_txt.set("Try Again!")
#         raise NoBlueChipException

#     pya.press("tab")

#     first_name = pyperclip.copy("na")
#     pya.hotkey("ctrl", "c")
#     first_name = pyperclip.paste()

#     if first_name == "na":
#         first_name = pya.prompt(
#             text="Please enter patient first name", title="First Name", default=""
#         )

#     pya.press("tab")
#     pya.press("tab")
#     last_name = pyperclip.copy("na")
#     pya.hotkey("ctrl", "c")
#     last_name = pyperclip.paste()
#     if last_name == "na":
#         last_name = pya.prompt(
#             text="Please enter patient surname", title="Surame", default=""
#         )
#     try:
#         print_name = title + " " + first_name + " " + last_name
#         print(print_name)
#     except TypeError:
#         pya.alert("Problem getting the name. Try again!")
#         raise BillingException

#     mrn = pyperclip.copy("na")
#     pya.moveTo(MRN_POS, duration=0.1)

#     pya.doubleClick()
#     pya.hotkey("ctrl", "c")
#     mrn = pyperclip.paste()
#     print(mrn)

#     mrn = pyperclip.paste()
#     if not mrn.isdigit():
#         mrn = pya.prompt("Please enter this patient's MRN")

#     return (mrn, print_name)


def address_scrape():
    """Scrape address and dob from blue chip.
    Used if billing anaesthetist.
    """
    dob = pyperclip.copy("na")
    pya.moveTo(DOB_POS, duration=0.1)

    pya.doubleClick()
    pya.hotkey("ctrl", "c")
    dob = pyperclip.paste()
    if len(dob) == 9:
        short = dob
        dob = '0' + short

    pya.press("tab")
    pya.press("tab")
    street = pyperclip.copy("na")

    pya.hotkey("ctrl", "c")
    street = pyperclip.paste()

    pya.press("tab")
    pya.press("tab")
    suburb = pyperclip.copy("na")

    pya.hotkey("ctrl", "c")
    suburb = pyperclip.paste()

    postcode = pyperclip.copy("na")
    pya.moveTo(POST_CODE_POS, duration=0.1)

    pya.doubleClick()

    pya.hotkey("ctrl", "c")
    postcode = pyperclip.paste()

    address = street + " " + suburb + " " + postcode
    state = postcode_to_state(postcode)
    logging.info(f"Data returned by address_scrape {address}, {dob}, {street}, {state}, {postcode}")
    return (address, dob, street, suburb, state, postcode)



# def address_scrape():
#     """Scrape address and dob from blue chip.
#     Used if billing anaesthetist.
#     """
#     dob = pyperclip.copy("na")
#     pya.moveTo(DOB_POS, duration=0.1)

#     pya.doubleClick()
#     pya.hotkey("ctrl", "c")
#     dob = pyperclip.paste()

#     pya.press("tab")
#     pya.press("tab")
#     street = pyperclip.copy("na")

#     pya.hotkey("ctrl", "c")
#     street = pyperclip.paste()

#     pya.press("tab")
#     pya.press("tab")
#     suburb = pyperclip.copy("na")

#     pya.hotkey("ctrl", "c")
#     suburb = pyperclip.paste()

#     postcode = pyperclip.copy("na")
#     pya.moveTo(POST_CODE_POS, duration=0.1)

#     pya.doubleClick()

#     pya.hotkey("ctrl", "c")
#     postcode = pyperclip.paste()

#     address = street + " " + suburb + " " + postcode

#     return (address, dob)


def episode_get_mcn_and_ref():
    """Scrape mcn from blue chip."""
    mcn = pyperclip.copy("na")
    pya.press("tab", presses=11)
    pya.hotkey("ctrl", "c")
    mcn = pyperclip.paste()
    mcn = mcn.replace(" ", "")

    ref = pyperclip.copy("na")
    pya.press("tab", presses=2)
    pya.hotkey("ctrl", "c")
    ref = pyperclip.paste()
    return mcn, ref


def episode_get_fund_number():
    """Scrape fund number from blue chip."""
    fund_number = pyperclip.copy("na")
    pya.moveTo(FUND_NO_POS, duration=0.1)

    pya.doubleClick()
    pya.hotkey("ctrl", "c")
    fund_number = pyperclip.paste()

    if fund_number == "na":
        fund_number = pya.prompt(
            text="Please enter fund number!", title="Fund Number", default=""
        )
    return fund_number


def episode_getfund(insur_code, fund, fund_number, ref):
    """Controller function for scraping fund and medicare details.
    ref may contain ADF episode id.
    """

    if insur_code in {"ga", "adf"}:
        mcn = ""
    elif insur_code in {"bb", "paid", "bill", "va"}:
        fund_number = ""
        mcn, ref = episode_get_mcn_and_ref()
    else:
        mcn, ref = episode_get_mcn_and_ref()
        fund_number = episode_get_fund_number()

    return (mcn, ref, fund, fund_number)


def day_surgery_to_csv(
    mrn,
    in_theatre,
    out_theatre,
    anaesthetist,
    endoscopist,
    asa,
    upper,
    colon,
    banding,
    nurse,
    clips,
    varix_lot,
    message,
):
    """Write day surgery data to csv."""

    today_str = today.strftime("%d-%m-%Y")
    data = (
        today_str,
        mrn,
        in_theatre,
        out_theatre,
        anaesthetist,
        endoscopist,
        asa,
        upper,
        colon,
        banding,
        nurse,
        clips,
        varix_lot,
        message,
    )
    with open("d:\\Nobue\\day_surgery.csv", mode="at") as handle:
        datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
        datawriter.writerow(data)


def day_surgery_shelver(
    mrn,
    in_theatre,
    out_theatre,
    anaesthetist,
    endoscopist,
    asa,
    upper,
    colon,
    banding,
    nurse,
    clips,
    varix_lot,
    message,
):
    """Write episode  data to a shelf.
    Used by watcher.py to dump data in day surgery.
    """
    with shelve.open("d:\\JOHN TILLET\\episode_data\\dumper_data.db") as s:
        s[mrn] = {
            "in_theatre": in_theatre,
            "out_theatre": out_theatre,
            "anaesthetist": anaesthetist,
            "endoscopist": endoscopist,
            "asa": asa,
            "upper": upper,
            "colon": colon,
            "banding": banding,
            "nurse": nurse,
            "clips": clips,
            "varix_lot": varix_lot,
            "message": message,
        }


# Utility fucntions for bill processing


def get_age_difference(dob):
    """Is patients 75 or older?"""
    dob = parse(dob, dayfirst=True)
    age_sep = relativedelta(today, dob)
    return age_sep.years


def get_invoice_number():
    """Get pickled invoice, increment and repickle."""
    s = "d:\\JOHN TILLET\\episode_data\\invoice_store.py"
    with open(s, "r+b") as handle:
        invoice = pickle.load(handle)
        invoice += 1
        handle.seek(0)
        pickle.dump(invoice, handle)
        handle.truncate()
    return invoice


def get_time_code(op_time):
    """Calculate medicare time code from time in theatre.
    op_time is an int
    returns time_code as a string"""
    time_base = "230"
    time_last = "10"
    second_last_digit = 1 + op_time // 15
    if op_time % 15 == 0:
        second_last_digit -= 1

    if op_time > 15:
        time_last = "{}5".format(second_last_digit)
    time_code = time_base + time_last
    return time_code


def medtitrust_process(
    title,
    first_name,
    last_name,
    dob,
    street,
    suburb,
    state,
    postcode,
    upper,
    colon,
    asa,
    mcn,
    ref,
    in_formatted,
    out_formatted,
    insur_code,
    fund,
    fund_number,
    anaesthetist,
):
    """Turn raw data into stuff ready to go into meditrust csv file."""
    if insur_code in {'adf', 'paid', 'send_bill'} and anaesthetist == "Dr J Tillett":
        return None

    phone = ""
    email = ""
    workcover_name = ""
    workcover_claim_no = ""
    veterans_no = ""
    if asa == "92515-39":
        asa3 = True
    else:
        asa3 = False

    if fund == "BUPA":
        fund = "BUPA - NO GAP"
    elif fund == "HCF":
        fund = "HCF (NG scheme)"


    if upper and not colon and not asa3:
        procedure = 'Panendoscopy'
    elif upper and not colon and asa3:
        procedure = 'Panendoscopy, ASA3'
    elif upper and  colon and not asa3:
        procedure = 'Panendoscopy, Colonoscopy'
    elif upper and  colon and asa3:
        procedure = 'Panendoscopy, Colonoscopy, ASA3'
    elif not upper and  colon and not asa3:
        procedure = 'Colonoscopy'
    elif not upper and  colon and asa3:
        procedure = 'Panendoscopy, Colonoscopy, ASA3'


    if insur_code == 'bb':
        bill_type = 'MEDICARE_FEE'
        fund = ''
        fund_number =''

    elif insur_code in {'adf', 'paid', 'send_bill', 'va'}: # unsure about adf - meditrust wants mcn but I don't have it
        if insur_code == 'va':
            veterans_no = mcn
        bill_type = 'NO_GAP_FEE'
        mcn = ''
        ref = ''
        fund = ''
        fund_number =''
        
    else:
        bill_type = 'NO_GAP_FEE'

    meditrust_csv = (
        title,
        first_name,
        last_name,
        dob,
        street,
        suburb,
        state,
        postcode,
        phone,
        email,
        procedure,
        mcn,
        ref,
        in_formatted,
        out_formatted,
        bill_type,
        fund,
        fund_number,
        workcover_name,
        workcover_claim_no,
        veterans_no,
)

    return meditrust_csv



def bill_process(
    dob,
    upper,
    lower,
    asa,
    mcn,
    insur_code,
    op_time,
    patient,
    address,
    ref,
    fund,
    fund_number,
    endoscopist,
    anaesthetist,
):
    """Turn raw data into stuff ready to go into anaesthetic csv file."""
    today_for_invoice = today.strftime("%d" + "-" + "%m" + "-" + "%Y")
    age_diff = get_age_difference(dob)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = "No"

    if upper:
        upper_done = "upper_Yes"  # this goes to jrt csv file
    else:
        upper_done = "upper_No"
    if lower:
        lower_done = "lower_Yes"
    else:
        lower_done = "lower_No"
    if asa[-2] == "3":
        asa_three = "asa3_Yes"
    elif asa[-2] == "4":
        asa_three = "asa3_Four"
    elif asa[-2] in {"1", "2"}:
        asa_three = "asa3_No"
    if age_diff >= 75:
        age_seventy = "age70_Yes"
    else:
        age_seventy = "age70_No"
    #    if insur_code == 'os':  # get rid of mcn in reciprocal mc patients
    #        mcn = ''

    time_code = get_time_code(op_time)

    invoice = get_invoice_number()
    invoice = "DEC" + str(invoice)

    ae_csv = (
        today_for_invoice,
        patient,
        address,
        dob,
        mcn,
        ref,
        fund,
        fund_number,
        insur_code,
        endoscopist,
        upper_done,
        lower_done,
        age_seventy,
        asa_three,
        time_code,
        invoice,
    )

    return ae_csv


def message_parse(message):
    """Put line breaks into message string."""
    message = message.rstrip(".")
    message = message.replace(".", "<br>")
    return message


def equip_write(proc, endoscopist, mrn):
    """takes procedure as a string and writes it and date to equipment file
    for Nobue"""
    today_str = today.strftime("%d-%m-%Y")
    data = (today_str, proc, endoscopist, mrn)
    with open("d:\\Nobue\\equipment.csv", mode="at") as handle:
        datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
        datawriter.writerow(data)


def update_and_verify_last_colon(mrn, colon, endoscopist):
    """
    If no long colon done it just returns None
    check if dates and codes are in conflict with Medicare rules - note exact date 1,3,5 years ago passes
    update shelf  record to today's date and return None
    note: shelf is a dictionary of keys - mrn as string, values - date of last colon as datetime.date object
    note: in docbill the global 'today' is a datetime.datetime object and has to be converted to a datetime.date object 
    for comparisons to work properly
    """
    if not colon:
        return
    if colon[0:3] != '322':
        return
    address = "D:\\Nobue\\last_colon_date"
    with shelve.open(address) as s:
        try:
            last_colon_date = s[mrn]  #this is a datetime.date object
        except KeyError:
            last_colon_date = None

        if last_colon_date and (last_colon_date != today.date()):  # second test is in case this is a resend today

            time_sep = relativedelta(today.date(), last_colon_date).years
            last_colon_date_printed = last_colon_date.strftime('%d-%m-%Y')

            if (colon == '32226') and time_sep < 1:
                reply = pya.confirm(text=f'Last colon performed less than one year ago ({last_colon_date_printed}).\nCheck colon code with {endoscopist}.', title='Colon Code Confirm', buttons=['Proceed anyway', 'Go Back to change'])
                if reply == "Go Back to change":
                    raise TooSoonException
            elif (colon == '32224') and time_sep < 3:
                reply = pya.confirm(text=f'Last colon performed less than three years ago ({last_colon_date_printed}).\nCheck colon code with {endoscopist}.', title='Colon Code Confirm', buttons=['Proceed anyway', 'Go Back to change'])
                if reply == "Go Back to change":
                    raise TooSoonException
            elif (colon == '32223') and time_sep < 5:
                reply = pya.confirm(text=f'Last colon performed less than five years ago ({last_colon_date_printed}).\nCheck colon code with {endoscopist}.', title='Colon Code Confirm', buttons=['Proceed anyway', 'Go Back to change'])
                if reply == "Go Back to change":
                    raise TooSoonException

        s[mrn] = today.date()


def caecum_data(doctor, mrn, caecum_flag):
    """Write whether scope got to caecum."""
    doctor = doctor.split()[-1]
    today_str = today.strftime("%Y-%m-%d")
    if caecum_flag == "":
        caecum_flag = "success"
        reason = ""
    else:
        reason = caecum_flag
        caecum_flag = "fail"
    caecum_data = (today_str, doctor, mrn, caecum_flag, reason)
    csvfile = "d:\\JOHN TILLET\\source\\caecum\\caecum.csv"
    with open(csvfile, "a") as handle:
        datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
        datawriter.writerow(caecum_data)


def meditrust_writer(anaesthetist, endoscopist_lowered, today, meditrust_csv):
        today_str = today.strftime("%d-%m-%Y")
        a_surname = anaesthetist.split()[-1]
        filename = today_str + "-" + endoscopist_lowered
        csvfile = "d:\\JOHN TILLET\\episode_data\\meditrust\\{}\\{}.csv".format(a_surname, filename)
        temp_list = []
        try:
            with open(csvfile, mode="r") as handle:
                datareader = csv.reader(handle, dialect="excel", lineterminator="\n")
                for old_data in datareader:
                    if old_data[11] == meditrust_csv[11]:
                        continue
                    else:
                        temp_list.append(old_data)
                temp_list.append(meditrust_csv)
        except:
            temp_list.append(meditrust_csv)

        with open(csvfile, "w") as handle:
            datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
            for ep_data in temp_list:
                datawriter.writerow(ep_data)


def to_anaesthetic_csv(new_ep_data, anaesthetist):
    """Write tuple of anaesthetic billing data to csv
    for billing anaesthetists"""
    surname = anaesthetist.split()[-1]
    csvfile = "d:\\JOHN TILLET\\episode_data\\sedation\\{}.csv".format(surname)
    temp_list = []
    try:
        with open(csvfile, mode="r") as handle:
            datareader = csv.reader(handle, dialect="excel", lineterminator="\n")
            for old_data in datareader:
                if old_data[0] == new_ep_data[0] and old_data[1] == new_ep_data[1]:
                    continue
                else:
                    temp_list.append(old_data)
            temp_list.append(new_ep_data)
    except:
        temp_list.append(new_ep_data)
    with open(csvfile, mode="w") as handle:
        datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
        for ep_data in temp_list:
            datawriter.writerow(ep_data)


def web_shelver(
    outtime,
    endoscopist,
    anaesthetist,
    patient,
    consult,
    upper,
    colon,
    polyp,
    message,
    intime,
    nurse,
    asa,
    banding,
    varix_lot,
    mrn,
):
    """Write episode  data to a shelf.
    Used to write short and long web pages.
    """

    a_surname = anaesthetist.split()[-1]
    e_surname = endoscopist.split()[-1]
    docs = e_surname + "/" + a_surname

    if not consult:
        consult = ""
    if not upper:
        upper = ""
    if not colon:
        colon = ""

    today_str = today.strftime("%Y-%m-%d")
    today_path = os.path.join(
        "d:\\JOHN TILLET\\episode_data\\webshelf\\" + today_str + "_19"
    )
    episode_dict = {
        "in_theatre": intime,
        "out_theatre": outtime,
        "doctors": docs,
        "name": patient,
        "asa": asa,
        "consult": consult,
        "upper": upper,
        "colon": colon,
        "polyp": polyp,
        "banding": banding,
        "nurse": nurse,
        "varix_lot": varix_lot,
        "message": message,
        "billed": "",
    }
    with shelve.open(today_path, writeback=False) as s:
        s[mrn] = episode_dict

        return today_path


def make_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for web page of today's patients
    from shelf data
    """
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


def make_long_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for complete info on today's patients
    """
    today_str = today.strftime("%A" + "  " + "%d" + "-" + "%m" + "-" + "%Y")
    with shelve.open(today_path) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x["out_theatre"], reverse=True)

    path_to_template = (
        "D:\\JOHN TILLET\\episode_data\\today_long_sec_shelf_template_19.html"
    )
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = "today_long_sec_shelf_template_19.html"
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open("d:\\Nobue\\today_long.html", "w", encoding="utf-8") as f:
        f.write(a)
    file_date = today.strftime("%Y" + "-" + "%m" + "-" + "%d")
    file_str = "D:\\JOHN TILLET\\episode_data\\html-backup\\" + file_date + ".html"
    with open(file_str, "w", encoding="utf-8") as f:
        f.write(a)


def colon_to_csv(mrn, colon):
    """Record evry patient who has colon with teir mrn date and colon code.
    Possible basis for app later on to see if patient eligible for code."""
    today_str = today.strftime("%d" + "-" + "%m" + "-" + "%Y")
    data = (today_str, mrn, colon)
    with open("D:\\JOHN TILLET\\episode_data\\colon_csv", mode="at") as handle:
        datawriter = csv.writer(handle, dialect="excel", lineterminator="\n")
        if colon:
            datawriter.writerow(data)


def to_watched():
    """Write dummy text to a folder. Watchdog in watcher.py watches this."""
    with open("D:\\JOHN TILLET\\episode_data\\watched\\watched.txt", mode="wt") as f:
        f.write("Howdy, watcher")


def render_anaesthetic_report(anaesthetist):
    """Make a web page if billing anaesthetist showing patients done today."""
    anaes_surname = anaesthetist.split()[-1]
    today_data = []
    count = 0
    csv_length = 0
    today_date = today.strftime("%d" + "-" + "%m" + "-" + "%Y")
    csvfile = "d:\\JOHN TILLET\\episode_data\\sedation\\{}.csv".format(anaes_surname)
    with open(csvfile) as handle:
        reader = csv.reader(handle)
        for episode in reader:
            csv_length += 1
            if episode[0] == today_date:
                count += 1
                today_data.append(episode)
    path_to_template = "D:\\JOHN TILLET\\episode_data\\today_anaesthetic_template.html"
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = "today_anaesthetic_template.html"
    template = env.get_template(template_name)
    a = template.render(
        today_data=today_data,
        today_date=today_date,
        count=count,
        anaes_surname=anaes_surname,
        csv_length=csv_length,
    )
    with open("d:\\Nobue\\report_{}.html".format(anaes_surname), "w") as f:
        f.write(a)


def close_out(anaesthetist):
    """Close patient file with mouse click and display billing details
    if a billing anaesthetist."""
    time.sleep(0.5)
    pya.moveTo(CLOSE_POS[0], CLOSE_POS[1])
    pya.click()
    time.sleep(0.5)
    pya.hotkey("alt", "n")
    pya.moveTo(x=780, y=110)
    if anaesthetist in BILLING_ANAESTHETISTS:
        webbrowser.open("d:\\Nobue\\report_{}.html".format(anaesthetist.split()[-1]))


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
    printfile = "d:\\JOHN TILLET\\episode_data\\sedation\\accounts\\{}_{}.docx".format(
        name, today_str
    )
    acc.save(printfile)


# menu bar programs
def open_roster():
    webbrowser.open("d:\\Nobue\\anaesthetic_roster.html")


def open_today():
    nob_today = "d:\\Nobue\\today_new.html"
    webbrowser.open(nob_today)


def open_weekends():
    weekends = "https://docs.google.com/spreadsheets/d/10FAfIu_mkRA-cmABNz4nhK-i_VuSVNrPs55zpOTTbcs/edit?usp=sharing"
    webbrowser.open(weekends)


def error_log():
    webbrowser.open("d:\\JOHN TILLET\\episode_data\\doclog.log")


def add_message():
    mess_box.grid()
    mess_box.focus()


def open_dox():
    pya.hotkey("ctrl", "w")


def change_fees():
    os.startfile("d:\\john tillet\\episode_data\\fees.ini")


def add_staff():
    os.startfile("d:\\JOHN TILLET\\episode_data\\STAFF.ini")


def delete_record():
    """Delete patient from web page. Does not delete from billing csv."""
    today_str = today.strftime("%Y-%m-%d")
    today_path = os.path.join("d:\\JOHN TILLET\\episode_data\\webshelf\\" + today_str)
    mrn = pya.prompt(text="Enter mrn of record to delete.", title="", default="")
    if not mrn:
        return
    with shelve.open(today_path) as s:
        try:
            del s[mrn]
        except Exception:
            pya.alert(text="Already deleted!", title="", button="OK")
    make_web_secretary_from_shelf(today_path)
    make_long_web_secretary_from_shelf(today_path)


def start_decbatches():
    """Because system is set to use pythonw need to write cmd file
    to fire up python for terminal programs"""
    user = os.getenv("USERNAME")
    if user == "John":
        os.startfile("c:\\Users\\John\\Miniconda3\\bccode\\start_decbatches.cmd")
    elif user == "John2":
        os.startfile("c:\\Users\\John2\\Miniconda3\\bccode\\start_decbatches.cmd")


def open_receipt():
    path = "d:/john tillet/episode_data/sedation/accounts"
    path = os.path.realpath(path)
    os.startfile(path)


def open_sedation():
    path = "d:/john tillet/episode_data/sedation"
    path = os.path.realpath(path)
    os.startfile(path)


def asa_click(event):
    as1 = asc.get()
    if as1 == "No Sedation":
        fund_box.grid_remove()
    else:
        if biller_anaesthetist_flag:
            fund_box.grid()


def colon_combo_click(event):
    colon_proc = co.get()
    if colon_proc not in {"No Lower", "Cancelled"}:
        path_box.grid()
        ba_box.grid()
    else:
        po.set("Colon Pathology")
        ba.set("No Anal Procedure")
        path_box.grid_remove()
        ba_box.grid_remove()

    if colon_proc != "Failure to reach caecum":
        caecum_box.grid_remove()
        fail_text.set("")
    else:
        caecum_box.grid()
        fail_text.set("Reason for Failure")


def is_biller_endoscopist(event):
    global biller_endo_flag
    global PATIENTS
    biller_endo = end.get()

    doctor = biller_endo.split()[-1].lower()
    PATIENTS = get_list_from_dic(doctor, booking_dic)
    #    print(PATIENTS)

    if biller_endo in {
        "Dr A Wettstein",
        "A/Prof R Feller",
        "Dr C Vickers",
        "Dr S Vivekanandarajah",
    }:
        biller_endo_flag = True
        con.set("None")
        con_label.grid()
        con_button1.grid()
        con_button2.grid()
    else:
        biller_endo_flag = False
        con.set("No need")
        con_label.grid_remove()
        con_button1.grid_remove()
        con_button2.grid_remove()


def pat_box_selected(event):
    global selected_name
    global manual_mrn
    global manual_flag
    selected_name = pat.get()
    if selected_name == "Enter Manually":
        manual_flag = True
        while True:
            selected_name = pya.prompt(
                text="Enter Patient Name - no problem if slight error!",
                title="Patient Name",
                default="Jane Doe",
            )
            if selected_name is None:
                raise BillingException
            elif selected_name == "Jane Doe":
                continue
            else:
                pat.set(selected_name)
                break
        while True:
            manual_mrn = pya.prompt(
                text="Enter MRN - MUST BE ACCURATE!", title="MRN", default="00000"
            )
            if manual_mrn is None:
                raise BillingException
            elif manual_mrn == "00000":
                continue
            else:
                break

    else:
        manual_flag = False


def is_biller_anaesthetist(event):
    global biller_anaesthetist_flag
    biller_anaesthetist = an.get()
    if biller_anaesthetist in {"Dr J Tillett", "Dr S Vuong"}:
        biller_anaesthetist_flag = True
        fund_box.grid()
        fu.set("Fund")
        pat_box.grid_remove()
    else:
        biller_anaesthetist_flag = False
        fund_box.grid_remove()
        pat_box.grid()


def get_list_from_dic(doctor, booking_dic):
    if doctor not in booking_dic:
        return ["Enter Manually", ""]
    else:
        lop = list(set(booking_dic[doctor]))
        lop = sorted(lop, key=lambda x: x[1])
        return_list = ["Enter Manually", ""]
        for p in lop:
            return_list.append(p[0])
        return return_list


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
    nurs = nur.get()
    patient = pat.get()

    asa = asc.get()
    consult = con.get()
    print("cnosult {}".format(consult))
    upper = up.get()
    col = co.get()
    failure = caecum.get()
    path = po.get()
    fund = fu.get()
    top_line = anas != "Anaesthetist" and endo != "Endoscopist" and nurs != "Nurse"
    if not top_line:
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Missing staff  data"
        root.update_idletasks()
        return
    if patient == "Click for patients" and anas not in BILLING_ANAESTHETISTS:
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Select patient"
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
    if consult == "None":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Consult ?"
        root.update_idletasks()
        return

    if (anas in BILLING_ANAESTHETISTS) and (fund == "Fund") and (asa != "No Sedation"):
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
    if col != "No Lower" and path == "Colon Pathology":
        btn.config(state="disabled")
        btn_txt.set("")
        feedback["text"] = "Colon path?"
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


def runner(*args):
    """Main program. Runs when button pushed."""
    global selected_name
    global manual_flag
    global manual_mrn
    global equip_flag
    global overide_endoscopist
    global finish_time

    logging.debug("started")
    btn_txt.set("Sending...")
    feedback["text"] = "Sending data" + ("  " * 20)
    root.update_idletasks()
    try:
        insur_code, fund, ref, fund_number, message = "", "", "", "", ""
        varix_lot = ""

        anaesthetist = an.get()
        endoscopist = end.get()
        nurse = nur.get()

        upper = up.get()
        if upper == "Cancelled":
            message += "Upper cancelled."
        if upper == "Pe with varix banding":
            message += "Bill varix bander. BS225"
            varix_lot += "v"
        if upper == "HALO":
            halo = pya.prompt(
                text='Type either "90" or "ultra".', title="Halo", default="90"
            )
            message += halo + "."

        if upper in {
            "Oesophageal diatation",
            "Pe with APC",
            "Pe with varix banding",
            "BRAVO",
            "HALO",
        }:
            equip_flag = True
            proc = upper

        upper = UPPER_DIC[upper]

        if upper == "30475-00":
            upper_for_daysurgery = "41819-00"
        else:
            upper_for_daysurgery = upper

        colon = co.get()

        if colon == "Cancelled":
            message += "Colon cancelled."
        if colon == "Failure to reach caecum":
            caecum_flag = "fail"
            message += "Short colon only"
        else:
            caecum_flag = "success"
        colon = COLON_DIC[colon]



        banding = ba.get()

        if banding in {"Banding", "Banding + Pudendal"}:
            message += "Banding haemorrhoids 32135."
            equip_flag = True
            proc = "Banding of haemorrhoids"
        if banding == "Banding + Pudendal":
            message += "Bill Pudendal Block."
        if banding == "Anal dilatation":
            message += "Anal dilatation"

        banding = BANDING_DIC[banding]

        asa = asc.get()
        if asa == "No Sedation":
            message += "No sedation."
        try:
            asa = ASA_DIC[asa]
        except KeyError:
            asa = "92515-19"

        polyp = po.get()

        if polyp == "Biopsy" and colon == "32084-00":
            colon = "32084-01"
        elif polyp == "Polypectomy":
            polyp = "32229"
        elif polyp == "emr":
            polyp = "32230"

        if colon == "32084-00" and polyp == "32229":
            colon = "32087-00"
            polyp = ""

        #        day surgery uses the old style codes
        if colon in {"32084-00", "32084-01", "32087-00", "32095-00"}:
            colon_for_daysurgery = colon
        elif colon == "32227":
            dil_flag = pya.confirm(
                text="Was that a colonic dilatation?", buttons=["Dilatation", "Other"]
            )
            if dil_flag == "Dilatation":
                colon_for_daysurgery = "32094-00"
                equip_flag = True
                proc = "Colonic dilatation"
            #                equip_write("Colonic dilatation", endoscopist)
            elif polyp in {"32229", "32230"}:
                colon_for_daysurgery = "32093"
            else:
                colon_for_daysurgery = "32090-00"
        elif colon and polyp == "32229":
            colon_for_daysurgery = "32093-00"
        elif colon and polyp == "Biopsy":
            colon_for_daysurgery = "32090-01"
        elif colon and polyp == "No colon pathology":
            colon_for_daysurgery = "32090-00"
        else:
            colon_for_daysurgery = None

        if polyp in {"Colon Pathology", "No colon pathology", "Biopsy"}:
            polyp = ""

        caecum_flag = caecum.get()

        consult = con.get()
        consult = CONSULT_DIC[consult]

        formal_message = mes.get()
        if formal_message:
            message += formal_message + "."

        clips = cl.get()
        clips = int(clips)
        if clips != 0:
            message += "clips * {}. BS299".format(clips)

        op_time = ot.get()
        try:
            op_time = int(op_time)
        except:
            pya.alert(text="There was any error with the time in theatre.")
            btn_txt.set("Try Again!")
            raise BillingException

        if anaesthetist in BILLING_ANAESTHETISTS and asa:
            fund = fu.get()

            insur_code = FUND_TO_CODE.get(fund, "ahsa")
            if insur_code == "send_bill":
                fund = pya.prompt(
                    text="Enter Fund Name", title="Pay Later", default=None
                )
            if insur_code in {"ga", "adf"}:
                ref = pya.prompt(text="Enter Episode Id", title="Ep Id", default=None)
                fund_number = pya.prompt(
                    text="Enter Approval Number", title="Approval Number", default=None
                )
            if insur_code == "bb":
                message += "sedation bulk bill"
            if insur_code in {"bb", "paid", "bill"}:
                fund = "no fund"

        if anaesthetist in BILLING_ANAESTHETISTS:
            pya.click(TITLE_POS)
            mrn, name, title, first_name, last_name = front_scrape()

        elif selected_name == "error!":
            pya.alert(text="Error with patient name.")
            btn_txt.set("Try Again!")
            raise NoNameException
        elif manual_flag is False:
            name = selected_name
            mrn = mrn_dic[selected_name]
            print(mrn)
        elif manual_flag is True:
            name = selected_name
            mrn = manual_mrn

        #       check that correct doctor and patient is selected
        #       needed for billing anaesthetists using blue chip
        if anaesthetist in BILLING_ANAESTHETISTS:
            endoscopist_surname = endoscopist.split()[-1]
            endoscopist_lowered = endoscopist_surname.lower().title()
            endobase_endoscopist = pat_doc_dic.get(mrn, "absent")
            endo_endoscopist_lowered = endobase_endoscopist.lower().title()

            if (
                endobase_endoscopist == "Absent"
            ):  #  an absent mrn means patient not in list from endobase
                no_mrn_string = "CAREFUL!! /nThis patient not in the booked list. Click OK to continue or Cancel to go back"
                mrn_check = pya.confirm(
                    text=no_mrn_string,
                    title="Patient not in list",
                    buttons=["OK", "Cancel"],
                )
                if mrn_check != "OK":
                    raise NoNameException
            endoscopist_check = overide_endoscopist or (
                endo_endoscopist_lowered == endoscopist_lowered
            )
            if not endoscopist_check:
                wrong_doc_string = (
                    "This patint was booked with Dr  %s, click OK to continue with Dr %s or cancel to change."
                    % (endo_endoscopist_lowered, endoscopist_lowered)
                )
                doc_check = pya.confirm(
                    text=wrong_doc_string,
                    title="? Wrong endoscopist",
                    buttons=["OK", "Cancel"],
                )
                if doc_check == "OK":
                    overide_endoscopist = True
                else:
                    raise WrongDocException

        #        print(upper is None and (double_dic[mrn] == "True"))
        if ((upper is None or colon is None) and "cancelled." not in message) and (
            double_dic.get(mrn) == "True"
        ):
            pya.alert(
                text="Patient booked for double. Choose Cancelled or a procedure in the upper list.",
                title="",
                button="OK",
            )
            btn_txt.set("Try Again!")
            raise NoDoubleException

        update_and_verify_last_colon(mrn, colon, endoscopist)
        
        if equip_flag:
            equip_write(proc, endoscopist, mrn)

        time.sleep(2)
        logging.debug(anaesthetist)

        (in_theatre, out_theatre) = in_and_out_calculater(op_time, mrn)

        day_surgery_shelver(
            mrn,
            in_theatre,
            out_theatre,
            anaesthetist,
            endoscopist,
            asa,
            upper_for_daysurgery,
            colon_for_daysurgery,
            banding,
            nurse,
            clips,
            varix_lot,
            message,
        )

        day_surgery_to_csv(
            mrn,
            in_theatre,
            out_theatre,
            anaesthetist,
            endoscopist,
            asa,
            upper,
            colon,
            banding,
            nurse,
            clips,
            varix_lot,
            message,
        )

        message = message_parse(message)

        to_watched()

        today_path = web_shelver(
            out_theatre,
            endoscopist,
            anaesthetist,
            name,
            consult,
            upper,
            colon,
            polyp,
            message,
            in_theatre,
            nurse,
            asa,
            banding,
            varix_lot,
            mrn,
        )

        time.sleep(1)
        # test for existence of mrn in shelve
        with shelve.open(today_path) as s:
            s[mrn]

        make_web_secretary_from_shelf(today_path)

        make_long_web_secretary_from_shelf(today_path)

        colon_to_csv(mrn, colon)

        #        anaesthetic billing
        if asa is not None and anaesthetist in BILLING_ANAESTHETISTS:
            address, dob, street, suburb, state, postcode = address_scrape()
            (mcn, ref, fund, fund_number) = episode_getfund(
                insur_code, fund, fund_number, ref
            )

            time.sleep(2)
            meditrust_csv = medtitrust_process(
                title,
                first_name,
                last_name,
                dob,
                street,
                suburb,
                state,
                postcode,
                upper,
                colon,
                asa,
                mcn,
                ref,
                in_theatre,
                out_theatre,
                insur_code,
                fund,
                fund_number,
                anaesthetist,
            )
            if meditrust_csv:
                meditrust_writer(anaesthetist, endoscopist_lowered, today, meditrust_csv)
            
            anaesthetic_tuple = bill_process(
                dob,
                upper,
                colon,
                asa,
                mcn,
                insur_code,
                op_time,
                name,
                address,
                ref,
                fund,
                fund_number,
                endoscopist,
                anaesthetist,
            )
            to_anaesthetic_csv(anaesthetic_tuple, anaesthetist)
            render_anaesthetic_report(anaesthetist)
            if insur_code in {"paid", "paid_ama"}:
                print_receipt(anaesthetist, anaesthetic_tuple)

        time.sleep(0.5)
        if colon:
            caecum_data(endoscopist, mrn, caecum_flag)
        if anaesthetist in BILLING_ANAESTHETISTS:
            close_out(anaesthetist)


    except MissingProcedureException:
        logging.error("MissingProcedureException raised by %s", anaesthetist)
        return
    except TooSoonException:
        logging.error("TooSoonException raised by %s", anaesthetist)
        return
    except NoBlueChipException:
        logging.error("NoBlueChipException raised by %s", anaesthetist)
        return
    except TestingException:
        logging.error("TestingException raised by %s", anaesthetist)
        return
    except NoNameException:
        logging.error("BillingException raised by %s", anaesthetist)
        return
    except NoDoubleException:
        logging.error("NoDoubleException raised by %s", anaesthetist)
        # btn_txt.set("Resend")
        # feedback["text"] = "Choose Cancelled or a procedure from the upper list."
        return
    except WrongDocException:
        logging.error("WrongDocException raised by %s", anaesthetist)
        return
    except BillingException:
        logging.error("BillingException raised by %s", anaesthetist)
        return
    except Exception:
        logging.error("Fatal error in main loop", exc_info=True)
        pya.alert(text="Something went wrong!!", title="", button="OK")
        return

    # reset variables in gui

    pat.set("Click for patients")
    selected_name = "error!"

    manual_flag = False
    equip_flag = False
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
    fail_text.set("")

    caecum_box.grid_remove()
    ba_box.grid_remove()
    path_box.grid_remove()
    btn.config(text="Send!")
    mess_box.grid_remove()
    if biller_endo_flag:
        con_label.grid()
        con_button1.grid()
        con_button2.grid()
        con.set("None")
    else:
        con.set("No need")
    if biller_anaesthetist_flag:
        fund_box.grid()
        fu.set("Fund")
    btn_txt.set("Select patient")
    btn.config(state="disabled")
    feedback["text"] = "Select patient"

with concurrent.futures.ThreadPoolExecutor() as executor:
    future = executor.submit(pats_from_aws, today.strftime("%d/%m/%Y"))
    booking_dic, mrn_dic, double_dic, pat_doc_dic = future.result()
    
    
root = Tk()
root.title(datetime.datetime.today().strftime("%A  %d/%m/%Y"))
if user == "John2":
    root.geometry("470x500+840+100")
elif user == "John":
    root.geometry("600x630+1160+180")
root.option_add("*tearOff", FALSE)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

menubar = Menu(root)
root.config(menu=menubar)
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
menu_extras.add_command(label="Saturdays", command=open_weekends)

menubar.add_cascade(menu=menu_admin, label="Admin")
menu_admin.add_command(label="Delete Record", command=delete_record)
menu_admin.add_command(label="Error Log", command=error_log)
menu_admin.add_command(label="Add Staff", command=add_staff)
menu_admin.add_command(label="Change Fees", command=change_fees)

menubar.add_cascade(menu=menu_accounts, label="Accounts")
menu_accounts.add_command(label="receipts folder", command=open_receipt)
menu_accounts.add_command(label="sedation folder", command=open_sedation)
menu_accounts.add_command(label="Start batches print", command=start_decbatches)

# menubar.add_cascade(menu=menu_help, label="Help")
# menu_help.add_command(label="Help Page", command=open_help)

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
mes = StringVar()
ot = StringVar()
fu = StringVar()
fu.trace("w", button_enable)
fail_text = StringVar()
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

pat_box = ttk.Combobox(
    topframe, textvariable=pat, postcommand=lambda: pat_box.configure(values=PATIENTS)
)
pat_box["state"] = "readonly"
pat_box.grid(column=0, row=1, sticky=W)
pat_box.bind("<<ComboboxSelected>>", pat_box_selected)

space = "              " * 3
ttk.Label(midframe, text=space).grid(column=2, row=0, sticky=E)  # place holder

up_box = ttk.Combobox(midframe, textvariable=up, width=20)
up_box["values"] = UPPERS
up_box["state"] = "readonly"
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
path_box["values"] = ["No colon pathology", "Biopsy", "Polypectomy", "emr"]
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

boldStyle = ttk.Style()
boldStyle.configure("Bold.TLabel", size=20, weight="bold")
fail_label = ttk.Label(midframe, textvariable=fail_text, style="Bold.TLabel")
fail_label.grid(column=2, row=3, sticky=W)

caecum_box = ttk.Combobox(midframe, textvariable=caecum, width=20)
caecum_box["values"] = [
    "",
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
pat.set("Click for patients")
pat_box.grid_remove()
asc.set("ASA")
up.set("No Upper")
co.set("No Lower")
po.set("Colon Pathology")
ba.set("No Anal Procedure")
caecum.set("")
cl.set("0")
con.set("None")
ot.set("0")
fail_text.set("")
path_box.grid_remove()
con_label.grid_remove()
con_button1.grid_remove()
con_button2.grid_remove()
caecum_box.grid_remove()
ba_box.grid_remove()
mess_box.grid_remove()
fund_box.grid_remove()

update_spin()
root.attributes("-topmost", True)
root.mainloop()
