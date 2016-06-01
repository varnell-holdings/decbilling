import pyautogui, sys, datetime, colorama, pyperclip, os, python-dateutil

from bcdump import *
#colorama.init()


pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True

pe_flag = False         #use these to keep state when entering lower lines in blue chip
banding_flag = False
asa_flag = False

my_input()
bc_scrape()
jt_save()
bc_dumper()