"""Printing module."""

import configparser
import csv
from collections import defaultdict
import datetime
import math
import os
import shutil
import sys
import time
import zipfile
import colorama

import docx
from docx.shared import Mm
from docx.shared import Pt

import pyautogui as pya

import yagmail

colorama.init()
pya.FAILSAFE = True


fees_config = configparser.ConfigParser()
fees_config.read("d:\\john tillet\\episode_data\\FEES.ini")

# value is a list of  two numbers - the consult fee and the unit fee
# mbs july 2019 17610 $44.35   23010  $20.10
FUND_FEES = {
    "hcf": [72.90, 34.70],
    "bup": [74.40, 33.60],
    "mpl": [71.05, 32.70],
    "adf": [90.56, 55.00],
    "ahsa": [71.00, 36.00],
    "ahm": [71.05, 32.70],
    "nib": [74.40, 33.65],
    "ama": [150.00, 84.00],
    "ga": [82.60, 45.00],
    "gu": [70.00, 35.50],
    "lt": [55.44, 25.13],
    "sl": [74.05, 34.80],
    "hh": [55.44, 30.15],
    "va": [69.45, 32.70],
    "bb": [33.30, 15.10],
    "os": [70.00, 30.00],
    "u": [70.00, 35.00],
    "p": [33.30, 15.10],
    "send_bill": [74.40, 33.60],
    "paid": [70.00, 35.00],
    "paid_ama": [160.00, 80.00]
}


FUND_ADDRESSES = {
    "hcf": ["HCF", "GPO Box 4242", "Sydney", "NSW", "2001"],
    "bup": ["Bupa Medical Claims", "GPO Box 9809", "BRISBANE", "QLD", "4001"],
    "mpl": ["Medibank Private GapCover", "GPO Box 1288K", "Melbourne", "VIC", "3001"],
    "nib": ["nib MediGap Department", "Reply Paid 62208", "NEWCASTLE", "NSW", "2300"],
    "ahm": ["ahm GapCover", "Locked Bag 4", "Wetherill Park BC", "NSW", "2164"],
    "adf": ["ADF HSC", "Unknown", "", "", ""],
    "ga": [
        "Garrison Health Services\nC/- Medibank Health Solutions",
        "PO Box 9999",
        "MELBOURNE",
        "VIC",
        "3001",
    ],
    "gu": ["GU Health", "Reply Paid 2988", "Melbourne", "Vic", "8060"],
    "ama": [
        "The Doctors Health Fund",
        "PO Box Q1749",
        "Queen Victoria Building",
        "NSW",
        "1230",
    ], 
    "Australian Unity Health": [
        "Australian Unity Health Ltd",
        "114 Albert Rd",
        "South Melbourne",
        "VIC",
        "3205",
    ],
    "CBHS Health": [
        "CBHS Health Fund Limited",
        "Locked Bag 5014",
        "Parramatta",
        "NSW",
        "2124",
    ],
    "CUA Health": ["CUA Health Ltd", "GPO Box 100", "Brisbane", "QLD", "4001"],
    "Defence Health": ["Defence Health Ltd", "PO Box 7518", "Melbourne", "VIC", "3004"],
    "GMHBA": ["GMHBA Limited", "PO Box 761", "Geelong", "Vic", "3220"],
    "health.com.au": ["health.com.au", "Locked Bag 423", "Abbotsford", "VIC", "3067"],
    "Health Insurance Fund of Australia": [
        "Health Insurance Fund of Australia",
        "GPO Box X2221",
        "Perth",
        "WA",
        "6847",
    ],
    "Health Partners": ["Health Partners", "GPO Box 1493", "Adelaide", "SA", "5001"],
    "HBF": ["HBF Health Limited", "GPO Box S1440", "Perth", "WA", "6845"],
    "myOwn Health": ["myOwn", "PO Box 7302", "Melbourne", "VIC", "3004"],
    "Navy Health Ltd": ["Navy Health Ltd", "PO Box 172", "Box Hill", "VIC", "3128"],
    "Onemedifund": ["Onemedifund", "Locked Bag 25", "Wollongong DC", "NSW", "2500"],
    "Peoplecare Health": [
        "Peoplecare Health",
        "Locked Bag 33",
        "Wollongong DC",
        "NSW",
        "2500",
    ],
    "Pheonix Health": ["Pheonix Health Fund", "PO Box 156", "Newcastle", "NSW", "2300"],
    "Railway & Transport Health": [
        "rt health fund",
        "PO Box 545",
        "Strawberry Hills",
        "NSW",
        "2012",
    ],
    "Reserve Bank": [
        "Reserve Bank Health Society",
        "Locked Bag 23",
        "Wollongong DC",
        "NSW",
        "2500",
    ],

    "Teachers Health Fund": [
        "Teachers Health Fund",
        "GPO Box 9812",
        "Sydney",
        "NSW",
        "2001",
    ],
    "Nurses & Midwives Health":["Nurses & Midwives Health", "Level 4/260 Elizabeth St", "Sydney", "NSW", "2000"],
    "healthcare insurance": ["healthcare insurance", "PO Box 931", "Burnie", "TAS", "7320"],
    "Teachers Union or QTH": ["TUH  ", "PO Box 265", "Fortitude Valley", "QLD", "4006"],
    "Westfund": ["Westfund", "PO Box 235", "Lithgow", "NSW", "2790"],
    "lt": ["Latrobe Health", "Reply Paid 41", "Morell", "VIC", "3840"],
    "hh": ["Hunter Health", "PO Box", "Cessnock", "NSW",  "2325"],
    "sl": ["stlukeshealth", "PO Box 915", "Launceston", "TAS", "7250"],
    "Queensland Country Health": ["Queensland Country Health", "1/333 Ross River Rd", "Aitkenvale", "QLD", "4814"],
    
}

BILLER = {
    "Dr J Tillett": {
        "name": "Dr John Tillett",
        "address": "7 Henry Lawson Drive, Villawood NSW 2163",
        "provider": "0307195H",
        "abn": "66 781 021 178",
        "contact": "Phone: 8382 6622 Email: john@endoscopy.stvincents.com.au",
        "email": "john.lamia@gmail.com",
    },
    "Dr S Vuong": {
        "name": "Dr Sabine Vuong",
        "address": "PO Box 169 Dulwich Hill 2203",
        "provider": "2349492F",
        "abn": "80 757 898 6622",
        "contact": "8382 3200",
        "email": "sabinevuong@fastmail.com.au",
    },
}


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


PAGE_NUMBER = 24

today = datetime.datetime.today()
FILE_STR = today.strftime("%y-%m-%d")


def clear():
    print("\033[2J")  # clear screen
    print("\033[1;1H")  # move to top left


def print_account(ep, doc, unit, consult_as_float, time_fee, total_fee, biller):
    """Prints a single accout to a docx document and returns it"""
    biller = BILLER[biller]

    if ep["fund_code"] == "paid":
        doc.add_heading("Tax Invoice for Anaesthetic Fees Paid", level=0)
    else:
        doc.add_heading("Account for Anaesthetic", level=0)

    doc.add_heading(biller["name"], level=2)
    doc.add_heading(biller["address"], level=4)

    if ep["fund_code"] in {"paid", "send_bill"}:
        abn_str = "ABN:  " + (biller["abn"])
        doc.add_heading(
            "Provider Number: " + biller["provider"] + "    " + abn_str, level=5
        )
    else:
        doc.add_heading("Provider Number: " + biller["provider"], level=5)
    doc.add_heading(biller["contact"], level=5)
    doc.add_paragraph("")

    h_head = doc.add_heading("Patient Details", level=4)
    inv_string = "%s%s%s" % (("  " * 20), "Invoice Number  ", ep["invoice"])
    h_head.add_run(inv_string)
    doc.add_paragraph("")
    a1 = doc.add_paragraph()
    a1.add_run("%s" % ep["name"]).bold = True
    doc.add_paragraph("%s" % ep["address"])
    doc.add_paragraph("Date of birth  %s" % ep["dob"])
    if ep["fund_code"] in {"ga", "adf"}:
        doc.add_paragraph(
            "Fund:  %s   Episode Number:  %s" % (ep["fund_name"], ep["ref"])
        )
        p_ga = doc.add_paragraph("Approval Number:")
        ga_str = "   %s" % ep["fund_number"]
        p_ga.add_run(ga_str)
    elif ep["fund_code"] == "send_bill":
        doc.add_paragraph(
            "Fund:  %s   " % (ep["ref"])
        )
        doc.add_paragraph("Patient not registered with Medicare for this service.")
    else:
        doc.add_paragraph(
            "Fund:  %s   Number:  %s" % (ep["fund_name"], ep["fund_number"])
        )
        p_mc = doc.add_paragraph("Medicare Number")
        mc_str = "   %s    ref  %s" % (ep["medicare_no"], ep["ref"])
        p_mc.add_run(mc_str)
    doc.add_paragraph("Date of Procedure:  %s" % ep["date"])
    doc.add_paragraph("Procedure performed by %s" % ep["doctor"])
    doc.add_paragraph("Diagnostic Endoscopy Centre, Darlinghurst, NSW 2010")
    doc.add_paragraph("Facility ID 657131A")

    doc.add_paragraph("Item Number%sFee" % (" " * 10))

    p_cons = doc.add_paragraph("17610")
    cons_str = "%.2f" % consult_as_float
    cons_str = cons_str.rjust(25)
    p_cons.add_run(cons_str)

    if ep["upper"] in {"Yes", "upper_Yes"}:
        p_endo = doc.add_paragraph("20740")
        endo_str = "%.2f" % (unit * 5)
        endo_str = endo_str.rjust(24)
        p_endo.add_run(endo_str)
        if ep["lower"] in {"Yes", "lower_Yes"}:
            p_col = doc.add_paragraph("20810")
            col_str = "%.2f" % 0.0
            col_str = col_str.rjust(26)
            p_col.add_run(col_str)
    if ep["upper"] in {"No", "upper_No"} and ep["lower"] in {"Yes", "lower_Yes"}:
        p_col = doc.add_paragraph("20810")
        col_str = "%.2f" % (unit * 4)
        col_str = col_str.rjust(24)
        p_col.add_run(col_str)
    if ep["seventy"] in {"Yes", "age70_Yes"}:
        p_age = doc.add_paragraph("25014")
        age_str = "%.2f" % unit
        age_str = age_str.rjust(25)
        p_age.add_run(age_str)
    if ep["asa_3"] in {"Yes", "asa3_Yes"}:
        p_sick = doc.add_paragraph("25000")
        sick_str = "%.2f" % unit
        sick_str = sick_str.rjust(25)
        p_sick.add_run(sick_str)
    if ep["asa_3"] in {"asa3_Four"}:
        p_sick = doc.add_paragraph("25005")
        sick_str = "%.2f" % unit
        sick_str = sick_str.rjust(25)
        p_sick.add_run(sick_str)

    p_time_fee = doc.add_paragraph(ep["time"])
    time_fee_str = "%.2f" % time_fee
    time_fee_str = time_fee_str.rjust(25)
    p_time_fee.add_run(time_fee_str)

    p_tot = doc.add_paragraph("Total Fee")
    tot_str = "$%.2f" % total_fee
    tot_str = tot_str.rjust(19)
    p_tot.add_run(tot_str).bold = True

    doc.add_paragraph("")
    p_gst = doc.add_paragraph("")
    p_gst.add_run("No item on this invoice attracts GST").italic = True
    doc.add_page_break()

    section = doc.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    return doc


def print_calc(n):
    """calculate number of invoices to print if there are more than 20."""
    divisor = math.ceil(n / 20)
    return math.floor(n / divisor)


def print_batch_header(
    doc, fund, number_printed, total, headers_datafile
):  # fund is fu in loop
    if fund[:4] == "ahsa":
        afund = fund[5:]
    else:
        afund = fund
    doc.add_heading("Batch Header", level=0)
    doc.add_paragraph("")
    if afund == "bb":
        doc.add_paragraph("Bulk Bill")
    elif afund == "va":
        doc.add_paragraph("Veterans's Affairs")
    elif afund == "paid":
        doc.add_paragraph("Paid on day")
    else:
        doc.add_paragraph("Fund:  %s" % (FUND_ADDRESSES.get(afund, list(afund))[0]))
    doc.add_paragraph("")
    doc.add_paragraph("Number in batch:  %d" % number_printed)
    doc.add_paragraph("")
    doc.add_paragraph("Total fees:  %.2f" % total)
    doc.add_paragraph("")
    if fund == "paid":
        doc.add_paragraph("These patients should have paid on the day of procedure.")
        doc.add_paragraph("The amounts on these invoices may not be correct.")
        doc.add_paragraph(
            "Correct invoices will be in sedation\\accounts folder on work computers"
        )
    elif fund == "send_bill":
        doc.add_paragraph("These patients have not paid")
    elif fund == "gu":
        doc.add_paragraph("GU nw has its own batch header.")
    elif fund == "hcf":
        doc.add_paragraph(
            "HCF does not require batch header form but wants less than 20 accounts per envelope."
        )
    elif fund == "ama":
        doc.add_paragraph("The Doctors Fund uses AHSA batch header form.")
    elif fund == "ga":
        doc.add_paragraph("Garrison does not require a batch header.")
        doc.add_paragraph("Either post to below address or fax to 1300 633 227")
    elif fund == "adf":
        doc.add_paragraph("Keep these accounts until BUPA tells us what to do.")

    doc.add_paragraph("")
    doc.add_paragraph("")

    address = FUND_ADDRESSES.get(afund, "na")
    if address == "na":
        pass
    else:
        run = doc.add_paragraph().add_run(address[0])
        font = run.font
        font.size = Pt(14)
        run = doc.add_paragraph().add_run(address[1])
        font = run.font
        font.size = Pt(14)
        run = doc.add_paragraph().add_run(
            address[2] + "  " + address[3] + "  " + address[4]
        )
        font = run.font
        font.size = Pt(14)

    doc.add_paragraph("")
    doc.add_paragraph("")
    if afund in {"gu", "lt"}:
        doc.add_heading("No stamp needed!", level=1)

    doc.add_page_break()

    with open(headers_datafile, mode="a") as handler:
        filewriter = csv.writer(handler, dialect="excel", lineterminator="\n")
        total = "%.2f" % total
        batch_data = (afund, str(number_printed), total)
        filewriter.writerow(batch_data)

    return doc


def makebb(datafile):
    """
    Write bb patients to a separate bb.csv file for hposentry
    """
    try:
        with open(datafile) as csvfile:
            reader = csv.DictReader(csvfile, headers)
            ep_list = [_ for _ in reader]

    except IOError:
        print("No datafile file found.")
        sys.exit(1)

    with open("d:\\john tillet\\episode_data\\bb.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for episode in ep_list:
            if episode["fund_code"] == "bb":
                writer.writerow(episode)


def batch_filler(name):
    surname = name.split()[-1]

    def print_save(newzip, counter):
        counter += 1
        pya.hotkey("ctrl", "shift", "s")
        time.sleep(3)
        pya.typewrite(str(counter))
        time.sleep(1)
        pya.press("enter")
        time.sleep(1)
        pya.hotkey("alt", "f4")
        #        time.sleep(1)
        #        pya.press("n")
        time.sleep(2)

        file = "d:\\Nobue\\headers\\{}.pdf".format(counter)
        newzip.write(file, compress_type=zipfile.ZIP_DEFLATED)
        time.sleep(1)
        os.remove(file)

        return newzip, counter

    today = datetime.datetime.today()
    ahsa_today_str = today.strftime("%d-%m-%Y")
    #    bup_today_str = today.strftime("%d%m%y")
    mpl_today_str_d = today.strftime("%d")
    mpl_today_str_m = today.strftime("%m")
    mpl_today_str_y = today.strftime("%Y")
#    gu_today_str = today.strftime("%d-%m-%Y")

    try:
        os.remove("d:\\Nobue\\headers.zip")

    except IOError:
        pass

    newzip = zipfile.ZipFile("d:\\Nobue\\headers.zip", "a")

    for folder_name, subfolders, filenames in os.walk("d:\\Nobue\\headers"):
        for filename in filenames:
            prefix = filename[:-4]
            if prefix.isdigit():
                try:
                    os.remove("d:\\Nobue\\headers\\" + filename)
                except:
                    pass

    with open("d:\\Nobue\\headers\\batches.csv") as h:
        reader = csv.reader(h)
        counter = 0
        for batch in reader:
            f = "d:\\Nobue\\headers\\{}_pre_{}.pdf".format(batch[0], surname)
            #            if batch[0] == 'bup':
            #                os.startfile(f)
            #                time.sleep(3)
            #                pya.typewrite(['tab'] * 6, interval= 0.4)
            #                time.sleep(2)
            #                pya.typewrite(bup_today_str, interval=0.1)
            #                pya.typewrite(['tab'] * 2, interval= 0.4)
            #                pya.typewrite(batch[1])
            #                pya.typewrite(['tab'] * 6, interval= 0.4)
            #                time.sleep(2)
            #                pya.typewrite(bup_today_str, interval=0.1)
            #                newzip, counter = print_save(newzip, counter)

            if batch[0] in {"mpl", "ahm"}:
                os.startfile(f)
                time.sleep(3)
                pya.typewrite(["tab"] * 4, interval=0.3)
                time.sleep(1)
                pya.typewrite(mpl_today_str_d, interval=0.4)
                time.sleep(1)
                pya.press("tab")
                pya.typewrite(mpl_today_str_m, interval=0.4)
                time.sleep(1)
                pya.press("tab")
                pya.typewrite(mpl_today_str_y, interval=0.4)
                time.sleep(1)
                pya.press("tab")
                pya.typewrite(batch[1])
                newzip, counter = print_save(newzip, counter)

            elif batch[0] in {"bup", "nib", "lt", "hh", "sl"}:
                os.startfile(f)
                time.sleep(4)
                newzip, counter = print_save(newzip, counter)
            
#            elif batch[0] in {"gu"}:
#                os.startfile(f)
#                time.sleep(12)
#                newzip, counter = print_save(newzip, counter)

#            elif batch[0] == "gu":
#                os.startfile(f)
#                time.sleep(15)
#                pya.typewrite(["tab"] * 10, interval=0.1)
#                time.sleep(2)
#                pya.typewrite(gu_today_str, interval=0.1)
#                time.sleep(1)
#                pya.press("tab")
#                pya.typewrite(batch[1])
#                time.sleep(1)
#                pya.press("tab")
#                pya.typewrite(batch[2])
#                time.sleep(3)
#                newzip, counter = print_save(newzip, counter)

            elif batch[0] not in [
                "send_bill",
                "paid",
                "bb",
                "va",
                "hcf",
                "bup",
                "mpl",
                "nib",
                "ahm",
                "ga",
                "gu",
                "adf",
            ]:
                f = "d:\\Nobue\\headers\\ahsa_pre_{}.pdf".format(surname)
                os.startfile(f)
                time.sleep(3)
                pya.typewrite(["tab"] * 2, interval=0.4)
                time.sleep(2)
                pya.typewrite(FUND_ADDRESSES[batch[0]][0], interval=0.1)
                time.sleep(1)
                pya.press("tab")

                pya.typewrite(
                    FUND_ADDRESSES[batch[0]][1] + " " + FUND_ADDRESSES[batch[0]][2],
                    interval=0.1,
                )
                time.sleep(1)
                pya.press("tab")
                #            add a space on back of state to avoid bug
                state = FUND_ADDRESSES[batch[0]][3]
                state = state + " "
                pya.typewrite(state, interval=0.4)

                pya.press("tab")
                pya.typewrite(FUND_ADDRESSES[batch[0]][4], interval=0.1)
                pya.typewrite(["tab"] * 5, interval=0.4)
                pya.typewrite(ahsa_today_str, interval=0.1)
                pya.press("tab")
                pya.typewrite(str(batch[2]))
                pya.press("tab")
                pya.typewrite(batch[1])
                pya.press("tab")
                pya.typewrite(str(batch[2]))
                newzip, counter = print_save(newzip, counter)

    newzip.close()


FUND_CODES = [
    "Pay Later",
    "paid",
    "send_bill",
    "va",
    "bb",
    "hcf",
    "bup",
    "mpl",
    "nib",
    "ahm",
    "ga",
    "gu",
    "ama",
    "ahsa",
]


def format_fixed_width(rows):
    """Taken from Trey Hunner's Python Morsels. Formats output for summary."""
    column_lengths = [max(len(cell) for cell in col) for col in zip(*rows)]
    output = ""
    for row in rows:
        for column, length in zip(row, column_lengths):
            output += column.ljust(length + 2)
        output = output.rstrip() + "\n"
    return output.rstrip()


def check_addresses(datafile):
    """Print a list of funds in csv that are not in FUND_ADDRESSES dictionary"""
    with open(datafile) as handler:
        csv_handler = csv.reader(handler)
        flag = False
        clear()
        print()
        print("***  Checking fund address list  ***")
        print("")
        for entry in csv_handler:
            if entry[8] == "ahsa" and entry[6] not in FUND_ADDRESSES:
                print("{} not in fund address list".format(entry[6]))
                flag = True
        if flag:
            print()
            print("The above funds need to be added to address book - ask JT")
            print()
            answer = input("Hit x to quit or any other key to continue")
            if answer == "x".lower():
                sys.exit(0)
        else:
            print("All Good!")
        


def mail_and_backup(anaesthetist, file_type):
    surname = anaesthetist.split()[-1]
    yag = yagmail.SMTP("john.lamia@gmail.com", "qayfyowgkhdnbwdz")
    to = BILLER[anaesthetist]["email"]

    body = "body test"
    if file_type == "summary":
        path = "d:/john tillet/episode_data/sedation/accts_summary.txt"
        subject = "DEC billing summary"
        body = "Attached is a summary of your acounts proccesed today"
        save_destination = "d:/john tillet/episode_data/sedation/backup/{}-{}-accts_summary.txt".format(
            FILE_STR, surname
        )
    elif file_type == "csv":
        path = "d:/john tillet/episode_data/sedation/{}.csv".format(surname)
        subject = "DEC billing csv"
        body = "Attached is the csv file of your acounts proccesed today"
        save_destination = "d:/john tillet/episode_data/sedation/backup/{}-{}-csv.csv".format(
            FILE_STR, surname
        )
    elif file_type == "docx":
        path = "d:/john tillet/episode_data/sedation/accts.docx".format(surname)
        subject = "DEC accounts"
        body = "Attached are your acounts proccesed today"
        save_destination = "d:/john tillet/episode_data/sedation/backup/{}-{}-accts.docx".format(
            FILE_STR, surname
        )
    elif file_type == "zip":
        path = "d:/Nobue/headers.zip"
        subject = "DEC batch headers"
        body = "Attached are your batch headers proccesed today"
        save_destination = "d:/john tillet/episode_data/sedation/backup/{}-{}-headers.zip".format(
            FILE_STR, surname
        )
    elif file_type == "bb":
        path = "d:/john tillet/episode_data/bb.csv"
        subject = "Bulk Bill csv"
        body = "Attached is your bulk bill csv proccesed today"
        save_destination = "d:/john tillet/episode_data/sedation/backup/{}-{}-bb.csv".format(
            FILE_STR, surname
        )

    path = os.path.realpath(path)
    save_path = os.path.realpath(save_destination)
    content = [path]
    yag.send(to, subject, body, content)
    shutil.copy(path, save_path)


def sort_funds(x):
    if x == "send_bill":
        return 10
    elif x == "adf":
        return 15
    elif x == "paid":
        return 20
    elif x == "bb":
        return 30
    elif x == "va":
        return 40
    elif x == "hcf":
        return 50
    elif x == "bup":
        return 60
    elif x == "mpl":
        return 70
    elif x == "nib":
        return 80
    elif x == "ahm":
        return 90
    elif x == "ga":
        return 100
    elif x == "gu":
        return 105
    elif x == "ama":
        return 110
    elif x in {"lt", "hh", "sl"}:
        return 115
    else:
        return 150


def process_acc(grand_total, ep):
    """Do some calculations before printing account.

    Input - grand_total a float and ep an Ordered Dictionary
    """

    # get fees from module depending on fund
#    fee_package = FUND_FEES[ep["fund_code"]]
#    consult_as_float = float(fee_package[0])
#    unit = float(fee_package[1])
    consult_as_float = float(fees_config[ep["fund_code"]]["consult"])
    unit = float(fees_config[ep["fund_code"]]["unit"])

    # get time info and calculate time fee
    # the fourth digit in the time code gives the number of units
    time_length = int(ep["time"][3])
    time_fee = time_length * unit

    # calculate total_fee, initialise total_fee with consult
    total_fee = consult_as_float

    if ep["upper"] in {"Yes", "upper_Yes"}:
        total_fee += unit * 5
    if ep["upper"] in {"No", "upper_No"} and ep["lower"] in {"Yes", "lower_Yes"}:
        total_fee += unit * 4
    if ep["seventy"] in {"Yes", "age70_Yes"}:
        total_fee += unit
    if ep["asa_3"] in {"Yes", "asa3_Yes"}:
        total_fee += unit
    if ep["asa_3"] in {"asa3_Four"}:
        total_fee += unit * 2

    # add on time fees
    total_fee = total_fee + (time_length * unit)
    grand_total += total_fee

    return (grand_total, consult_as_float, unit, time_fee, total_fee)


def cleanup(datafile, masterfile, summaryfile, printfile, anaesthetist):
    """Close and delete files at end of script."""
    input("Press Enter to open accounts summary.")
    os.startfile(summaryfile)
    print()
    input("Press Enter to open accounts file.")
    os.startfile(printfile)
    time.sleep(3)
    
    print()
    while True:
        merge = """All done!

Press y to merge csv with masterfile.

Press n to just exit (current csv file will stay in place.)

Neither of these actions will affect making batch headers.
"""
        flag = input(merge)
        if flag in {"y", "n"}:
            break
    if flag == "n":
        pass

    elif flag == "y":
        with open(datafile) as csvhandle:
            with open(masterfile, "a") as filehandle:
                csvdata = csv.reader(csvhandle)
                csvwriter = csv.writer(filehandle, dialect="excel", lineterminator="\n")
                for p in csvdata:
                    csvwriter.writerow(p)
        try:
            os.remove(datafile)
        except FileNotFoundError:
            pass


# Print iterations progress
def printProgressBar(
    iteration, total, prefix="", suffix="", decimals=1, length=25, fill="█"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    # Print New Line on Complete
    if iteration == total:
        print()


def main():
    """Print accounts in batches of funds."""

    clear()
    while True:
        a = input("Enter 1 for SV or 2 for JT  ")
        if a == str(2):
            biller = "Dr J Tillett"
            omit_set = {"bb", "paid"}
            break
        elif a == str(1):
            biller = "Dr S Vuong"
            omit_set = {}
            break
        else:
            continue

    clear()
    while True:
        print("Enter a to make accounts or b to make batch headers or hit x to exit now.")
        print("")
        print("To do both - first choose a to make accounts then restart this program")
        print("and choose b to make batch headers")
        
        b = input()
        if b == "b":
            input("""Make sure to shrink the docbill screen before continuing.\n
                  Not able to print the GU header at this time - keeps crashing.\n
                  Any key to continue.""")
            
            batch_filler(biller)
            print("Emailing the headers..")
            mail_and_backup(biller, "zip")
            sys.exit()
        elif b == "a":
            break
        elif b == 'x':
            sys.exit()
        else:
            continue
            
    biller_surmame = biller.split()[-1]
    base = "D:\\JOHN TILLET\\episode_data\\sedation\\"
    summaryfile = base + "accts_summary.txt"
    printfile = base + "accts.docx"
    datafile = base + biller_surmame + ".csv"
    masterfile = base + biller_surmame + "_master.csv"
    headers_datafile = "D:\\Nobue\\headers\\batches.csv"

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
    try:
        os.remove(summaryfile)
    except IOError:
        pass
    try:
        os.remove(headers_datafile)
    except IOError:
        pass

    try:
        with open(datafile) as csvfile:
            reader = csv.DictReader(csvfile, headers)
            ep_list = list(reader)

    except IOError:
        print("No csv file found.")
        sys.exit(1)

    check_addresses(datafile)
#    go = input

    clear()
    print("Printing Dr {}'s accounts".format(biller_surmame))
    print()

    doc = docx.Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Verdana"

    # build a dictionary pat_dict where keys are fund names
    # and values are a list of episodes
    pat_dict = defaultdict(list)

    for episode in ep_list:
        if episode["fund_code"] == "ahsa":
            fund_id = episode["fund_code"] + "_" + episode["fund_name"]  # [:2]
            pat_dict[fund_id].append(episode)
        elif episode["fund_code"] not in omit_set:
            fund_id = episode["fund_code"]
            pat_dict[fund_id].append(episode)

    summary_list = []
    # for each fund in pat_dict get the list of episodes ep_list and print
    # them out in equal batches < 20
    length = 0
    for fund in pat_dict:
        length += len(pat_dict[fund])

    iteration = 0
    printProgressBar(
        iteration, length, prefix="Progress:", suffix="Complete", length=20
    )

    for fu in sorted(pat_dict.keys(), reverse=False, key=sort_funds):
        ep_list = pat_dict[fu]

        fund_len = len(ep_list)
        fund_left = fund_len
        start = 0
        if fund_len == 0:
            continue
        while True:
            grand_total = 0.0
            num_p = print_calc(fund_left)
            end = start + num_p
            for np in ep_list[start:end]:
                iteration += 1
                processed = process_acc(grand_total, np)
                grand_total, consult_as_float, unit, time_fee, total_fee = processed
                acc = print_account(
                    np, doc, unit, consult_as_float, time_fee, total_fee, biller
                )

            #            with open(summaryfile, 'a') as file:
            #                if np['fund_code'] == 'os':
            #                    file.write('Overseas -- %s\n ' % num_p)
            #                else:
            #                    file.write('%s -- %s\n ' % (fu, num_p))

            if np["fund_code"] == "send_bill":
                summary_name = "Not paid yet"
            elif np["fund_code"] == "paid":
                summary_name = "Paid at DEC"
            else:
                summary_name = np["fund_name"]

            summary_list.append(list([summary_name, str(num_p)]))

            acc = print_batch_header(doc, fu, num_p, grand_total, headers_datafile)
            fund_left -= num_p
            start += num_p

            printProgressBar(
                iteration, length, prefix="Progress:", suffix="Complete", length=20
            )
            time.sleep(0.1)
            if start >= fund_len:
                break
    with open(summaryfile, "wt") as file:
        file.write(format_fixed_width(summary_list))
    acc.save(printfile)
    print()
    print("Emailing the summary..")
    print("Please wait till the prompt reappears!")
    mail_and_backup(biller, "summary")
    print()
    print("Emailing the accounts..")
    mail_and_backup(biller, "docx")
    print()
    print("Emailing the csv file..")
    mail_and_backup(biller, "csv")
    print()
    if biller == "Dr J Tillett":
        makebb(datafile)
        print("Emailing the bb.csv file.")
        mail_and_backup(biller, "bb")
    print()
    print()

    cleanup(datafile, masterfile, summaryfile, printfile, biller)


if __name__ == "__main__":
    main()
