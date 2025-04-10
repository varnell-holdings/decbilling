"""Scrapers of Data from patient page of Blue Chip."""

from dataclasses import dataclass
from pprint import pprint
import pyperclip
import time
import os
import webbrowser

from pyisemail import is_email
import pyautogui as pya

pya.PAUSE = 0.1
# pya.FAILSAFE = True


ST = 10  # bigger makes repeated scrapping faster

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

@dataclass
class ScrapedData:
    title: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    mrn: str = ""
    dob: str = ""
    email: str = ""
    fund_number: str = ""
    mcn: str = ""
    ref: str = ""
    street: str = ""
    suburb: str = ""
    state: str = ""
    postcode: str = ""
    full_address: str = ""


def scraper(info, email=False):
    """Takes a string for the piece of data to be scraped.
    st changes the speed of retries"""
    result = pyperclip.copy("na")
    
    for i in range(3):
        time.sleep((i**2) / ST)
        pya.hotkey("ctrl", "c")
        result = pyperclip.paste()
        if email:
            result = result.split()[0]
            if not is_email:
                result = ""
        if result != "na":
            break
    if result == "na":
        while True:
            result = pya.prompt(text=f"Please enter patient's {info}")
            if result:
                break
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
    pya.doubleClick()
    sd.title = scraper("Title")

    pya.press("tab")
    sd.first_name = scraper("First Name")

    pya.press("tab")
    pya.press("tab")
    sd.last_name = scraper("Surname")

    pya.moveTo(MRN_POS)
    pya.doubleClick()
    sd.mrn = scraper("MRN")

    pya.moveTo(DOB_POS)
    pya.doubleClick()
    sd.dob = scraper("date of birth (dd/mm/yyyy)")
    if len(sd.dob) == 9:
        sd.dob = "0" + sd.dob

    pya.press("tab", presses=10)
    sd.email = scraper("email", email=True)

    sd.full_name = sd.title + " " + sd.first_name + " " + sd.last_name
    
    return sd


def address_scrape(sd):
    """Scrape address from blue chip.
    Used if billing anaesthetist.
    """
    # need to work out how to click/tab here from email box
    pya.keyDown('shift')
    pya.press('tab', presses=8)
    pya.keyUp('shift')
    sd.street = scraper("Street No. & Name")
    sd.street = sd.street.replace(",", "")

    pya.press("tab")
    pya.press("tab")
    sd.suburb = scraper("Suburb")

    pya.moveTo(POST_CODE_POS, duration=0.1)
    pya.doubleClick()
    sd.postcode = scraper("Postcode")

    sd.state = postcode_to_state(sd)
    sd.full_address = sd.street + " " + sd.suburb + " " + sd.state  + " " + sd.postcode
    
    return sd


def scrape_mcn_and_ref(sd):
    """Scrape mcn from blue chip."""
    pya.press("tab", presses=11)
    sd.mcn = scraper("mcn")
    sd.mcn = sd.mcn.replace(" ", "")

    pya.press("tab", presses=2)
    sd.ref = scraper("ref")

    return sd


def scrape_fund_number(sd):
    """Scrape fund number from blue chip."""
    pya.moveTo(FUND_NO_POS, duration=0.1)
    pya.doubleClick()
    sd.fund_number = scraper("Fund Number")

    return sd


def close_out(anaesthetist):
    """Close patient file with mouse click and display billing details
    if a billing anaesthetist."""

    pya.moveTo(CLOSE_POS[0], CLOSE_POS[1])
    pya.click()
    # time.sleep(0.25)
    pya.hotkey("alt", "n")
    pya.moveTo(x=780, y=110)
    if anaesthetist in BILLING_ANAESTHETISTS:
        anaes_surname = anaesthetist.split()[-1]
        webbrowser.open(
            f"d:\\john tillet\\episode_data\\sedation\\{anaes_surname}.html".format(anaesthetist.split()[-1])
        )


if __name__ == "__main__":
    sd = ScrapedData()
    input()
    patient_id_scrape(sd)
    sd = address_scrape(sd)
    sd = episode_get_mcn_and_ref(sd)
    sd = episode_get_fund_number(sd)
    pprint(sd)
