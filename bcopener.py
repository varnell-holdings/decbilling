import pyautogui, sys, datetime, colorama, pyperclip, os

#colorama.init()


pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True


def gastro_chooser(in_str):
    if in_str == 'pe':
        pyautogui.typewrite('30473-00\n')
        pyautogui.press('enter')
    elif in_str == 'pb':
        pyautogui.typewrite('30473-01\n')
        pyautogui.press('enter')
    elif in_str == 'pp':
        pyautogui.typewrite('30478-04\n')
        pyautogui.press('enter')
    elif in_str == 'ph':
        pe_flag = True
        pyautogui.typewrite('30490-00\n')
        pyautogui.press('enter')
    elif in_str == 'pv':
        pyautogui.typewrite('30476-02\n')
        pyautogui.press('enter')
    elif in_str == 'od':
        pyautogui.typewrite('41819-00\n')
        pyautogui.press('enter')
    elif in_str == 'pa':
        pyautogui.typewrite('30478-20\n')
        pyautogui.press('enter')
    return True

# collect patient name onto clipboard
def get_name():
    pyautogui.hotkey('alt','d')
    pyautogui.typewrite(['tab'] * 2, interval=0.1)
    pyautogui.hotkey('ctrl','c')
    first_name = pyperclip.paste()
    pyautogui.typewrite(['tab'] * 2, interval=0.1)
    pyautogui.hotkey('ctrl','c')
    last_name = pyperclip.paste()
    output_name = last_name + '   ' + first_name
    pyperclip.copy(output_name)
    pyautogui.hotkey('alt','p')
    sys.exit()


pe_flag = False         #use these to keep state when entering lower lines
banding_flag = False
asa_flag = False
nurse = sys.argv[1]
intime =  datetime.datetime.now().strftime("%H:%M")
# print(colorama.Fore.RED + '-----------')
os.system('cls')
print()
asa = input('ASA - 0 for no sedation:'  )
print()
print('Upper codes are pe, pb, pp, ph, pv, pa, od')
while True:
    upper = input('Upper press n for No:  ')
    if upper in ('n', 'pe', 'pb', 'pp', 'ph', 'pv', 'pa', 'od'):
        break
print()
print('Colon codes are co, cb, cp, sc, sb, sp')
while True:
    colon = input('Colon press n for No:  ')
    if colon in ('n', 'co', 'cb', 'cp', 'sc', 'sb', 'sp'):
        break
print()
banding = input('Banding? b for yes or Enter for no:   ')
print()
consult = input('Consult - 110, 116, or 0 for none:  ')
if consult == '0' or consult == '':
    consult = 'none'
print()
message = input('Message:    ')
print()
close = input('Press "o" to keep episode open.')
print()
warning = input('***ARE YOU SURE YOU HAVE THE PATIENT FILE OPEN?***')
outtime = datetime.datetime.now().strftime("%H:%M")
print(outtime)


# start clicking!!!
pyautogui.moveTo(50, 400)
pyautogui.click()
pyautogui.press('f8')
pyautogui.press('n')
pyautogui.typewrite(['down'] * 11, interval=0.1)
pyautogui.press('enter')
pyautogui.hotkey('alt','f')
pyautogui.hotkey('alt','i')
pyautogui.PAUSE = 0.1
pyautogui.typewrite(['enter'] * 4, interval=0.1)
pyautogui.typewrite(intime)
pyautogui.typewrite(['enter'] * 2, interval=0.1)
pyautogui.typewrite(outtime)
pyautogui.typewrite(['enter'] * 9, interval=0.1)
pyautogui.typewrite('Dr J Tillett\n')
pyautogui.hotkey('ctrl','c')
pyautogui.hotkey('alt','n')
pyautogui.typewrite(['down'] * 5, interval=0.1)
pyautogui.typewrite('Consultation:  ')
pyautogui.typewrite(consult)
pyautogui.press('enter')
pyautogui.press('enter')
pyautogui.typewrite('Message:  ')
pyautogui.typewrite(message)

pyautogui.hotkey('alt','n')
pyautogui.typewrite(['left'] * 2, interval=0.1)
pyautogui.moveTo(50, 155)
pyautogui.click()
pyautogui.hotkey('ctrl','v')
pyautogui.typewrite(['enter', 'e', 'enter'], interval=0.1)
pyautogui.moveTo(450, 155)
pyautogui.click()
pyautogui.typewrite(nurse)
pyautogui.typewrite(['enter', 'e', 'enter'], interval=0.1)
pyautogui.hotkey('alt','p')
if colon == 'co':
    pyautogui.typewrite('32090-00\n')
    pyautogui.press('enter')
elif colon == 'cb':
    pyautogui.typewrite('32090-01\n')
    pyautogui.press('enter')
elif colon == 'cp':
    pyautogui.typewrite('32093-00\n')
    pyautogui.press('enter')
elif colon == 'sc':
    pyautogui.typewrite('32084-00\n')
    pyautogui.press('enter')
elif colon == 'sb':
    pyautogui.typewrite('32084-01\n')
    pyautogui.press('enter')
elif colon == 'sp':
    pyautogui.typewrite('32087-00\n')
    pyautogui.press('enter')
else:
    pe_flag = gastro_chooser(upper)

pyautogui.typewrite(['tab'] * 6, interval=0.1)
if upper != 'n' and pe_flag == False:
    gastro_chooser(upper)
elif banding == 'b':
    banding_flag = True
    pyautogui.typewrite('32135-00\n')
    pyautogui.press('enter')
elif asa == '0':
    asa_flag = True
    pass
elif asa == '1'or asa == '':
    asa_flag = True
    pyautogui.typewrite('92515-19\n')
    pyautogui.press('enter')
elif asa == '2':
    asa_flag = True
    pyautogui.typewrite('92515-29\n')
    pyautogui.press('enter')
elif asa == '3':
    asa_flag = True
    pyautogui.typewrite('92515-39\n')
    pyautogui.press('enter')
if asa_flag == True:
    get_name()
else:
    pyautogui.typewrite(['tab'] * 2, interval=0.1)

if banding == 'b'and banding_flag == False:
    banding_flag = True
    pyautogui.typewrite('32135-00\n')
    pyautogui.press('enter')
elif asa == '0':
    asa_flag = True
    pass
elif asa == '1' or asa == '':
    asa_flag = True
    pyautogui.typewrite('92515-19\n')
    pyautogui.press('enter')
elif asa == '2':
    asa_flag = True
    pyautogui.typewrite('92515-29\n')
    pyautogui.press('enter')
elif asa == '3':
    asa_flag = True
    pyautogui.typewrite('92515-39\n')
    pyautogui.press('enter')

if asa_flag == True:
    get_name()
else:
    pyautogui.typewrite(['tab'] * 2, interval=0.1)
if asa == '0':
    asa_flag = True
    pass
elif asa == '1'or asa == '':
    asa_flag = True
    pyautogui.typewrite('92515-19\n')
    pyautogui.press('enter')
elif asa == '2':
    asa_flag = True
    pyautogui.typewrite('92515-29\n')
    pyautogui.press('enter')
elif asa == '3':
    asa_flag = True
    pyautogui.typewrite('92515-39\n')
    pyautogui.press('enter')
get_name()








