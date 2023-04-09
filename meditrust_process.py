'''New version of bill_process to output a csv with the info needed by Meditrust
needs name in 3 parts, address in 4 parts(only needs address for VA - according to Meditrust but I doubt this, in and out times

 
the retrn values function calls for front_scrape and address scrape will need to be changed in docbill
 '''


def postcode(postcode):
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
    logging.info(f"Data returned by front_scrape {mrn}, {print_name}, {title}, first_name {last_name}")

    return (mrn, print_name, title, first_name, last_name)


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
    state = postcode(postcode)
    logging.info(f"Data returned by address_scrape {address}, {dob}, {street}, {state}, {postcode}")
    return (address, dob, street, suburb, state, postcode)


def medtitrust_process(
    title,
    first_name,
    last_name,
    dob,
    address,
    suburb,
    state,
    postcode,
    upper,
    lower,
    asa,
    mcn,
    ref,
    in_formatted,
    out_formatted,
    insur_code,
    fund,
    fund_number,
):
    """Turn raw data into stuff ready to go into meditrust csv file."""
    phone = ""
    email = ""
    workcover_name = ""
    workcover_claim_no = ""
    veterans_no = ""
    if asa == "92515-39":
        asa3 = True
    else:
        asa3 = False

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
        address,
        suburb,
        state,
        postcode,
        phone,
        email,
        procedure,
        mcn,
        ref,
        in_fomatted,
        out_formatted,
        bill_type,
        fund,
        fund_number,
        workcover_name,
        workcover_claim_no,
        veterans_no,
)
    logging.info(f"Data returned by medtitrust_process {meditrust_csv}")
    return meditrust_csv
    # ? write to file iside this function because for paid and non BUPA not_paid we dont want to write
    # otherwise return a write  flag - wrong meditrust can send overseas accounts to funds
    # in and out times may need correcting at present prioritises day surgery not anaesthetic billing
    # need to add a leading 0 to age from blue chip -  done

if __name__ == '__main__':
    p = input('postcode:  ')
    print(postcode(p))
