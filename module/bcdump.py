import pyautogui



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

def asa_chooser():
    if asa == '0':
        pass
    elif asa == '1'or asa == '':
        pyautogui.typewrite('92515-19\n')
        pyautogui.press('enter')
    elif asa == '2':
        pyautogui.typewrite('92515-29\n')
        pyautogui.press('enter')
    elif asa == '3':
        pyautogui.typewrite('92515-39\n')
        pyautogui.press('enter')
    return True

def bcdumper():
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
    else:
        asa_flag = asa_chooser(asa)

    if asa_flag == True and close != 'o':
        pyautogui.hotkey('alt','f4')
        return
    elif asa_flag == True:
        return
    else:
        pyautogui.typewrite(['tab'] * 2, interval=0.1)

    if banding == 'b'and banding_flag == False:
        banding_flag = True
        pyautogui.typewrite('32135-00\n')
        pyautogui.press('enter')
    else:
        asa_flag = asa_chooser(asa)

    if asa_flag == True and close != 'o':
        pyautogui.hotkey('alt','f4')
        return
    elif asa_flag == True:
        return
    else:
        pyautogui.typewrite(['tab'] * 2, interval=0.1)

    asa_flag = asa_chooser(asa)

    if asa_flag == True and close != 'o':
        pyautogui.hotkey('alt','f4')
        return
    elif asa_flag == True:
        return