import pyautogui as pya
import pyperclip

DOB_POS = ""


def dob_scrape():
    dob = pyperclip.copy("na")
    pya.moveTo(DOB_POS, duration=0.1)

    pya.doubleClick()
    pya.hotkey("ctrl", "c")
    dob = pyperclip.paste()
    if dob == "na":
        dob = pya.prompt(
            text="Please enter patient date of birth (dd/mm/yyyy)",
            title="DOB",
            default="",
        )
    if len(dob) == 9:
        dob = "0" + dob

    return dob


"""  need to delete above code from addres_scrape. and delete return dob also from it
These return into main scope so no problems
line 1778 insert the following """

dob = dob_scrape()

""" and delete the returned dob from the following line"""
