import datetime
import shelve


def web_shelver(outtime, endoscopist, anaesthetist, patient,
                   consult, upper, colon, message, intime,
                   nurse, asa, banding, varix_lot, mrn):
    """Write episode  data to a shelf.
    Used to write short and long web pages.
    """
    today = datetime.datetime.today()
    today_str = today.strftime("%Y-%m-%d")
    with shelve.open('{}'.format(today_str)) as s:
        s[mrn] = { 
                'in_theatre': intime,
                'out_theatre': outtime,
                'anaesthetist': anaesthetist,
                'endoscopist': endoscopist,
                'name': patient,
                'asa': asa,
                'consult': consult,
                'upper': upper,
                'colon': colon,
                'banding': banding,
                'nurse': nurse,
                'varix_lot': varix_lot,
                'message': message,
                }

if __name__ == '__main__':
    web_shelver('9:05', 'Dr A Wettstein', 'Dr s Vuong', 'Mr J Smith',
        '110', '30473-00', '32084-00', 'test', '8:20', 'Jacinta',
        '3', None, 88, '1')
