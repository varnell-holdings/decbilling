def anaesthetic_scrape(sd):
    """Scrape address from blue chip.
    Used if billing anaesthetist.
    """
    pya.keyDown("shift")
    pya.press("tab", presses=8)
    pya.keyUp("shift")
    sd.street = scraper()
    sd.street = sd.street.replace(",", "")

    pya.press("tab")
    pya.press("tab")
    sd.suburb = scraper()

    pya.moveTo(POST_CODE_POS, duration=0.1)
    x1, y1 = POST_CODE_POS
    pya.doubleClick()
    sd.postcode = scraper()

    sd.state = postcode_to_state(sd)

    if "na" in {
        proc_data.street,
        proc_data.suburb,
        proc_data.postcode,
    }:
        raise ScrapingException
    proc_data.full_address = (
        proc_data.street
        + " "
        + proc_data.suburb
        + " "
        + proc_data.state
        + " "
        + proc_data.postcode
    )

    if proc_data.insur_code in {"adf", "bill_given"}:
        proc_data.mcn = ""
    elif proc_data.insur_code in {"bb", "va"}:
        proc_data.fund_number = ""
        proc_data = scrape_mcn_and_ref(proc_data)
    elif proc_data.insur_code in {"send_bill"}:
        proc_data.mcn = ""
        proc_data = scrape_fund_number(proc_data)
    else:
        proc_data = scrape_mcn_and_ref(proc_data)
        proc_data = scrape_fund_number(proc_data)

    if proc_data.mcn == "na":
        proc_data.mcn = get_manual_data(
            root, title="Manual Entry", prompt="Please enter the MCN."
        )

    if proc_data.ref == "na":
        proc_data.ref = get_manual_data(
            root, title="Manual Entry", prompt="Please enter the REF."
        )

    if (
        proc_data.insur_code not in {"send_bill", "bill_given", "va", "adf"}
        and len(proc_data.ref) != 1
    ):
        raise BillingException

    if proc_data.fund_number == "na":
        proc_data.fund_number = get_manual_data(
            root,
            title="Manual Entry",
            prompt="Please enter the Fund Number.",
        )
    return sd


def double_check(proc_data):
    if (
        proc_data.mrn in double_set
        and not (proc_data.upper and proc_data.colon)
        and "cancelled" not in proc_data.message
    ):
        pya.alert(
            text="Patient booked for Double. Choose either a procedure or cancelled for both.",
            title="",
            button="OK",
        )
        raise BillingException

call -> double_check(proc_data)
