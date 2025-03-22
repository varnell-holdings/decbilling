"""Needs testing with Blue Chip."""
import pyperclip, time, pymsgbox
import pyautogui as pya
from pyisemail import is_email

# sets scraping repeat speed
ST = 10


def scraper(datum, email=False):
    """Takes a string to display info requested in alert box"""
    pya.doubleClick()
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
            info = pymsgbox.prompt(text=f"Please enter patient {datum}")
            if info:
                break
    return info


if __name__ == "__main__":
    test_field = "??????"
    print(scraper(test_field))
