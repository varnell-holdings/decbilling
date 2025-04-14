"""Scrapers of Data from patient page of Blue Chip."""

from dataclasses import dataclass
from pprint import pprint
import pyperclip
import time
import os
import tkinter as tk
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


class BillingException(Exception):
    pass


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
        self.destroy()

    def cancel(self):
        # Set result to None and destroy the window
        self.result = None
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
    if not dialog:
        raise BillingException
    else:
        return dialog.result


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
        result = get_manual_data(
            root, title="Manual Entry", prompt="Please enter the {info}:"
        )
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
    pya.keyDown("shift")
    pya.press("tab", presses=8)
    pya.keyUp("shift")
    sd.street = scraper("Street No. & Name")
    sd.street = sd.street.replace(",", "")

    pya.press("tab")
    pya.press("tab")
    sd.suburb = scraper("Suburb")

    pya.moveTo(POST_CODE_POS, duration=0.1)
    pya.doubleClick()
    sd.postcode = scraper("Postcode")

    sd.state = postcode_to_state(sd)
    sd.full_address = sd.street + " " + sd.suburb + " " + sd.state + " " + sd.postcode

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
            f"d:\\john tillet\\episode_data\\sedation\\{anaes_surname}.html".format(
                anaesthetist.split()[-1]
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    sd = ScrapedData()
    input()
    patient_id_scrape(sd)
    sd = address_scrape(sd)
    sd = episode_get_mcn_and_ref(sd)
    sd = episode_get_fund_number(sd)
    pprint(sd)
