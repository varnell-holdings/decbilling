"""Scrapers of Data from patient page of Blue Chip."""

from dataclasses import dataclass
from pprint import pprint
import pyperclip
import time
import os

from pyisemail import is_email
import pyautogui as pya

pya.PAUSE = 0.9
pya.FAILSAFE = True


ST = 10  # bigger makes repeated scrapping slower

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
    info = pyperclip.copy("na")
    for i in range(4):
        time.sleep((i**2) / ST)
        pya.hotkey("ctrl", "c")
        info = pyperclip.paste()
        if email:
            if not is_email:
                info = ""
        if info != "na":
            break
    if info == "na":
        while True:
            info = pya.prompt(text=f"Please enter patient's {info}")
            if info:
                break
    return info


def postcode_to_state(postcode):
    post_dic = {"3": "VIC", "4": "QLD", "5": "SA", "6": "WA", "7": "TAS"}
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


def patient_id_scrape(pd):
    """Scrape names, mrn, dob, email from blue chip."""
    pya.moveTo(TITLE_POS, duration=0.3)()
    pd.title = scraper("Title")

    pya.press("tab")
    pd.first_name = scraper("First Name")

    pya.press("tab")
    pya.press("tab")
    pd.last_name = scraper("Surname")

    pya.moveTo(MRN_POS, duration=0.1)
    pd.mrn = scraper("MRN")

    pya.moveTo(DOB_POS, duration=0.1)
    pd.dob = scraper("date of birth (dd/mm/yyyy)")
    if len(pd.dob) == 9:
        pd.dob = "0" + pd.dob

    pya.press("tab", presses=16)
    pd.email = scraper("email", email=True)

    pd.full_name = pd.title + " " + pd.first_name + " " + pd.last_name

    return pd


def address_scrape(pd):
    """Scrape address from blue chip.
    Used if billing anaesthetist.
    """
    # need to work out how to click/tab here from email box
    # pya.press("tab")
    # pya.press("tab")
    pd.street = scraper("Street No. & Name")
    pd.street = pd.street.replace(",", "")

    pya.press("tab")
    pya.press("tab")
    pd.suburb = scraper("Suburb")

    pya.moveTo(POST_CODE_POS, duration=0.1)
    pd.postcode = scraper("Address")

    pd.address = pd.street + " " + pd.suburb + " " + pd.postcode
    pd.state = postcode_to_state(pd.postcode)
    return pd


def episode_get_mcn_and_ref(pd):
    """Scrape mcn from blue chip."""
    pya.press("tab", presses=5)
    pd.mcn = scraper("mcn")
    pd.mcn = pd.mcn.replace(" ", "")

    pya.press("tab", presses=2)
    pd.ref = scraper("ref")

    return pd


def episode_get_fund_number(pd):
    """Scrape fund number from blue chip."""
    pya.moveTo(FUND_NO_POS, duration=0.1)
    pd.fund_number = scraper("Fund Number")

    return pd


def close_out(anaesthetist):
    """Close patient file with mouse click and display billing details
    if a billing anaesthetist."""

    pya.moveTo(CLOSE_POS[0], CLOSE_POS[1])
    pya.click()
    # time.sleep(0.25)
    pya.hotkey("alt", "n")
    pya.moveTo(x=780, y=110)
    if anaesthetist in BILLING_ANAESTHETISTS:
        webbrowser.open(
            "d:\\john tillet\\report_{}.html".format(anaesthetist.split()[-1])
        )


if __name__ == "__main__":
    sd = ScrapedData()
    sd = patient_id_scrape(sd)
    sd = address_scrape(sd)
    sd = episode_get_mcn_and_ref(sd)
    sd = episode_get_fund_number(sd)
    pprint(sd)
