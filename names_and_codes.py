# names_and_codes.py
import textwrap


NURSES_DIC = {'no': 'Nobue Chashin',
              'ja': 'Jacqueline James',
              'jj': 'Jacqueline James',
              'jg': 'Jacinta Goldenberg',
              'js': 'Jacqueline Smith',
              'yi': 'Yi Lu',
              'pa': 'Parastoo Tavakoli Siahkali',
              'la': 'Larissa Berman',
              'ma': 'Mary Halter',
              'su': 'Subeia Aziz Silva',
              'be': 'Belinda Plunkett',
              'ch': 'Cheryl Guise',
              'ev': 'Eva Aliparo',
              'lo': 'Lorae Tamayo',}

ANAESTHETISTS = {'tt': 'Dr T Thompson',
                 'sv': 'Dr S Vuong',
                 'cb': 'Dr C Brown',
                 'jr': 'Dr J Riley',
                 'js': 'Dr J Stevens',
                 'db': 'Dr D Bowring',
                 'gos': "Dr G O'Sullivan",
                 'jt': 'Dr J Tester',
                 'rw': 'Dr Rebecca Wood',
                 'mm': 'Dr M Moyle',
                 'mon': "Dr Martine O'Neill",
                 'ni': 'Dr N Ignatenko',
                 'ns': 'Dr N Steele',
                 'tr': 'Dr Timothy Robertson',
                 'ms': 'Dr M Stone',
                 'fd': 'Dr Felicity Doherty',
                 'bm': 'Dr B Manasiev',
                 'eoh': "Dr E O'Hare",
                 'locum': 'locum',
                 'jrt': 'Dr J Tillett'}

REGULAR_ANAESTHETISTS = {'Dr J Tillett', "Dr G O'Sullivan",
                         'Dr S Vuong', 'Dr C Brown', 'Dr J Riley',
                         'Dr J Stevens', 'Dr D Bowring', 'Dr J Tester'}

BILLING_ANAESTHETISTS = {'Dr J Tillett', 'Dr S Vuong'}

VMOS = {'DR M Danta', 'DR R Gett', 'Prof R Lord', 'Dr G Owen', 'Dr A Meagher'}


DOC_LIST = ['Dr C Bariol', 'DR M Danta', 'Dr R Feller', 'DR R Gett',
            'Dr S Ghaly', 'Prof R Lord', 'Dr A Meagher',
            'Dr A Stoita', 'Dr C Vickers', 'Dr S Vivekanandarajah',
            'Dr A Wettstein', 'Dr D Williams']

DOC_DIC = {'cb': 'Dr C Bariol',
           'md': 'DR M Danta',
           'rf': 'Dr R Feller',
           'rg': 'DR R Gett',
           'sg': 'Dr S Ghaly',
           'rl': 'Prof R Lord',
           'am': 'Dr A Meagher',
           'as': 'Dr A Stoita',
           'cv': 'Dr C Vickers',
           'sv': 'Dr S Vivekanandarajah',
           'aw': 'Dr A Wettstein',
           'dw': 'Dr D Williams',
           'go': 'Dr G Owen',
           'wb': 'Dr W Bye',
           'bb': 'Dr W Bye',
           'vn': 'Dr V Nguyen',
           'jm': 'Dr J Mill',
           'cw': 'Dr Yang Wu',
           'ak': 'Dr A Kim',
           'ndl': 'Dr N De Luca',
           'ch': 'Dr Craig HAIFER',
           'ss': 'Dr S Sanagapalli'}

LOCUMS = {'Dr W Bye',
          'Dr V Nguyen',
          'Dr J Mill',
          'Dr Yang Wu',
          'Dr A Kim',
          'Dr Craig HAIFER',
          'Dr S Sanagapalli'}


BANDERS = {'DR R Gett', 'Dr A Meagher', 'Dr A Wettstein', 'Dr G Owen'}

CONSULTERS = {'Dr S Vivekanandarajah', 'Dr A Wettstein',
              'Dr C Vickers', 'Dr R Feller', 'Dr D Williams'}

ASA_DIC = {'0': None,
           '1': '92515-19',
           '2': '92515-29',
           '3': '92515-39',
           '4': '92515-49'}

ASA_HELP = {'0': 'No Sedation',
            '1': 'ASA 1',
            '2': 'ASA 2',
            '3': 'ASA 3',
            '4': 'ASA 4'}

UPPER_DIC = {'0': None,
             'c': None,
             '0c': None,
             'pe': '30473-00',
             'pb': '30473-01',
             'od': '30475-00',
             'pa': '30478-20',
             'ha': '30478-20',
             'ph': '30478-20',
             'pp': '30478-04',
             'pv': '30478-20',
             'br': '30490-00'}

UPPER_HELP = {'0': 'No upper procedure',
              'c': 'Endoscopy cancelled',
              'pec': 'Endoscopy cancelled',
              'pe': 'Panendoscopy - no biopsy',
              'pb': 'Panendoscopy with biopsy',
              'od': 'Panendoscopy with oesophageal diatation',
              'pa': 'Panendoscopy with APC or gold probe',
              'ha': 'Panendoscopy with HALO',
              'ph': 'Panendoscopy with HALO',
              'pp': 'Panendoscopy with polypectomy',
              'pv': 'Panendoscopy with variceal banding',
              'br': 'Panendoscopy with BRAVO'}

COLON_DIC = {'0': None,
             'c': None,
             'co': '32090-00',
             'cs': '32090-00',
             'cb': '32090-01',
             'cp': '32093-00',
             'cd': '32094-00',
             'csp': '32093-00',
             'sc': '32084-00',
             'sb': '32084-01',
             'sp': '32087-00'}

COLON_HELP = {'0': 'No lower procedure',
              'c': 'Cancel lower procedure',
              'co': 'Long Colonoscopy - no biopsy',
              'cb': 'Long Colonoscopy with biopsy',
              'cs': 'Colonoscopy - FOB screening',
              'cp': 'Long Colonoscopy with polypectomy',
              'cd': 'Colonic dilatation',
              'csp': 'Long Colonoscopy with polypectomy - FOB screening',
              'sc': 'Short Colonoscopy no biopsy',
              'sb': 'Short Colonoscopy with biopsy',
              'sp': 'Short Colonoscopy with polypectomy'}

BANDING_DIC = {'0': None,
               'b': '32135-00',
               'a': '32153-00'}

BANDING_HELP = {'0': 'No anal procedure',
                'b': 'Banding of haemorrhoids',
                'a': 'Anal dilatation'}

FUND_ABREVIATION = {'h': 'hcf',
                    'b': 'bup',
                    'm': 'mpl',
                    'n': 'nib',
                    'a': 'ahsa',
                    'd': 'ama',
                    't': 'ahm',
                    'u': 'u',
                    'p': 'p',
                    'v': 'va',
                    'o': 'os',
                    'g': 'ga'}

fund_string = 'hcf bup mpl nib ahsa ama ahm u p va os ga'

FUND_DIC = {'hcf': 'HCF',
            'mpl': 'Medibank Private',
            'bup': 'BUPA',
            'nib': 'NIB',
            'ama': "The Doctor's Fund",
            'ahm': 'Australian Health Management',
            'p': 'Pensioner',
            'u': 'Uninsured',
            'va': 'Veterans Affairs',
            'os': 'Overseas',
            'ga': 'Garrison Health',
            'ahsa': 'AHSA'}

AHSA_DIC = {'te': 'Teachers Federation Health',
            'tu': 'Teachers Union Health',
            'we': 'Westfund',
            'au': 'Australian Unity Health',
            'cb': 'CBHS Health',
            'ce': 'Cessnock District Health',
            'cr': 'Credicare',
            'de': 'Defence Health',
            'cu': 'CUA',
            'fr': 'Frank Health',
            'gm': 'GMHBA',
            'pe': 'Peoplecare Health',
            'rt': 'Railway & Transport Health',
            'gu': 'Grand United Corporate Health',
            'he': 'health.com.au',
            'hi': 'Health Insurance Fund',
            'hp': 'Health Partners',
            'hb': 'HBF',
            'na': 'Naval Health Benefits',
            're': 'Reserve Bank',
            'ph': 'Pheonix Health',
            'o': 'other'}


FILLED_TEXT = textwrap.dedent("""\
          There was data in the file opened.
          Either you have opened the wrong patient
          or the server made an error.
          Try to resend this patient
          If it fails again send a message
          to the seretaries by pressing
          m in the next screen.
          """)

CHOICE_STRING = textwrap.dedent("""\
        Continue            enter
        Change team         c
        Anaes roster/fees   r
        old records         ctrl + w
        message             m
        """)

CHOICE_STRING_BILLER = textwrap.dedent( """\
        Continue            enter
        Change team         c
        Anaes roster/fees   r
        web page            w
        old records         ctrl + w
        Spyder              s
        start watcher       sw
        dantafind           df
        update              u
        message             m
        receipt             rec
        print accs          p
        """)

# value is a list of  two numbers - the consult fee and the unit fee

FUND_FEES = {'hcf': [91.65, 34.70], 'bup': [74.40, 33.60],
             'mpl': [71.05, 32.70], 'ahsa': [69.00, 35.00],
             'ahm': [71.05, 32.70], 'nib': [72.15, 32.65],
             'ama': [150.00, 84.00], 'ga': [82.60, 45.00],
             'va': [69.45, 32.70], 'bb': [32.25, 14.85], 'os': [70.00, 30.00],
             'u': [69.45, 32.70], 'p': [32.25, 14.85]}



BILLER = {'Dr J Tillett':
            {'name': 'Dr John Tillett',
            'address': '7 Henry Lawson Drive, Villawood NSW 2163',
            'provider': '0307195H',
            'abn': '66 781 021 178',
            'contact': 'Phone: 8382 6622 Email: john@endoscopy.stvincents.com.au'},
        'Dr S Vuong':
             {'name': 'Dr Sabine Vuong',
              'address': 'PO Box 169 Dulwich Hill 2203',
              'provider': '2349492F',
              'abn': '80 757 898 6622',
              'contact': '8382 3200'}
            }
