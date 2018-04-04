""" new version to include lexicographic date to go to database for  new analysis function
and invoices now prefixed with DEC and are assigned to all anaesthetics - not just JT.
"""


def bill_process(dob, upper, lower, asa, mcn, insur_code, op_time,
                 patient, address, ref, fund,
                 fund_number, endoscopist, anaesthetist, message):
    """Turn raw data into stuff ready to go into my account.

    Generates and stores an incremented invoice number.
    First returned tuple is for csv, second is for database
    """
    now = datetime.datetime.now()
    today_for_invoice = now.strftime('%d' + '-' + '%m' + '-' + '%Y')
    today_lex = now.strftime('%Y' + '%m' + '%d')
    age_diff = get_age_difference(dob)
    age_seventy = upper_done = lower_done = asa_three = age_seventy = 'No'
    upper_code = lower_code = asa_code = seventy_code = ''

    if upper:
        upper_done = 'Yes'  # this goes to jrt csv file
        upper_code = '20740'  # this goes to anaesthetic database
    if lower:
        lower_done = 'Yes'
        lower_code = '20810'
    if asa[-2] == '3':
        asa_three = 'Yes'
        asa_code = '25000'
    if asa[-2] == '4':
        asa_three = 'Yes'
        asa_code = '25005'
    if age_diff >= 70:
        age_seventy = 'Yes'
        seventy_code = '25015'
    if insur_code == 'os':  # get rid of mcn in reciprocal mc patients
        mcn = ''
    if insur_code == 'u' or insur_code == 'p' and anaesthetist == 'Dr J Tillett':
        insur_code = 'bb'
        message += ' JT will bulk bill'
    # if insur_code == 'os' and fund != 'Overseas':  # os - in fund
    #     message += ' JT will bill {}.'.format(fund)

    time_code = get_time_code(op_time)

    invoice = get_invoice_number()
    invoice = 'DEC' + str(invoice)

    # db has direct aneasthetic codes under first and second
    # now used for anaesthetic day reports and jt analysis
    Anaes_ep = namedtuple(
        'Anaes_ep', 'today_for_invoice, patient, address, dob,'
        'mcn, ref, fund, fund_number, insur_code, endoscopist,'
        'anaesthetist, upper_code, lower_code, seventy_code,'
        'asa_code, time_code, invoice, today_lex')

    anaesthetic_data = Anaes_ep(
        today_for_invoice, patient, address, dob, mcn, ref,
        fund, fund_number, insur_code, endoscopist, anaesthetist,
        upper_code, lower_code, seventy_code,
        asa_code, time_code, invoice, today_lex)

    anaesthetic_data_dict = anaesthetic_data._asdict()  # for dataset

    # csv has fields with yes and no under upper_done etc
    # for my account printing program
    Aneas_ep_csv = namedtuple(
        'Aneas_ep_csv', 'today_for_invoice, patient, address, dob, mcn,'
        'ref, fund, fund_number, insur_code, endoscopist, upper_done,'
        'lower_done, age_seventy, asa_three, time_code, invoice')

    ae_csv = Aneas_ep_csv(
        today_for_invoice, patient, address, dob, mcn, ref,
        fund, fund_number, insur_code, endoscopist, upper_done,
        lower_done, age_seventy, asa_three, time_code, invoice)

    return ae_csv, anaesthetic_data_dict, message
