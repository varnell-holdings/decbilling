def id_scrape_check(proc_data):
    if "na" in {
        proc_data.title,
        proc_data.first_name,
        proc_data.last_name,
        proc_data.dob,
        proc_data.mrn,
        proc_data.email,
    }:
        return False
    if proc_data.first_name == proc_data.last_name:
        # resp = pmb.confirm(text=f'Patient first name and second name are the same - {
        #                    proc_data.first_name} ? error', title='', buttons=['Continue', 'Go Back'])
        # if resp == "Go Back":
        #     raise BillingException
        return False
    if proc_data.title == proc_data.first_name:
        return False

    if not proc_data.mrn.isdigit():
        return False
    try:
        parse(proc_data.dob, dayfirst=True)
    except Exception:
        return False
    return True


def patient_id_scrape(sd):
    """Scrape names, mrn, dob, email from blue chip."""
    for idex in range(3):
        pya.moveTo(TITLE_POS)
        pyperclip.copy("")
        pya.doubleClick()
        sd.title = scraper()

        pya.press("tab")
        sd.first_name = scraper()

        pya.press("tab")
        pya.press("tab")
        time.sleep(1)
        sd.last_name = scraper()

        pya.moveTo(MRN_POS)
        pya.doubleClick()
        sd.mrn = scraper()

        pya.moveTo(DOB_POS)
        pya.doubleClick()
        sd.dob = scraper()

        pya.press("tab", presses=10)
        sd.email = scraper(email=True)

        sd.full_name = sd.title + " " + sd.first_name + " " + sd.last_name

        if id_scrape_check(sd):
            continue
        if idex == 2:
            raise ScrapingException

    return sd
