ANAESTHETISTS = ['Dr D Bowring',
                 'Dr C Brown',
                 'Dr Felicity Doherty',
                 'Dr N Ignatenko',
                 'locum',
                 'Dr B Manasiev',
                 'Dr M Moyle',
                 "Dr E O'Hare",
                 "Dr Martine O'Neill",
                 "Dr G O'Sullivan",
                 'Dr J Riley',
                 'Dr Timothy Robertson',
                 'Dr N Steele',
                 'Dr J Stevens',
                 'Dr M Stone',
                 'Dr J Tester',
                 'Dr T Thompson',
                 'Dr J Tillett',
                 'Dr S Vuong',
                 'Dr Rebecca Wood']


NURSES = ['Belinda Plunkett',
          'Cheryl Guise',
          'Jacinta Goldenberg',
          'Jacqueline James',
          'Jacqueline Smith',
          'Larissa Berman',
          'Mary Halter',
          'Nobue Chashin',
          'Parastoo Tavakoli Siahkali',
          'Subeia Aziz Silva',
          'Yi Lu']

ENDOSCOPISTS = ['Dr C Bariol',
                'DR M Danta',
                'Dr R Feller',
                'DR R Gett',
                'Dr S Ghaly',
                'Prof R Lord',
                'Dr A Meagher',
                'Dr A Stoita',
                'Dr C Vickers',
                'Dr S Vivekanandarajah',
                'Dr A Wettstein',
                'Dr D Williams',
                'Dr N De Luca',
                'Dr G Owen',
                'Dr W Bye',
                'Dr A Kim',
                'Dr J Mill',
                'Dr V Nguyen',
                'Dr Yang Wu']

ASA = ['No Sedation', '1', '2', '3']

ASA_DIC = {'No Sedation': None,
           '1': '92515-19',
           '2': '92515-29',
           '3': '92515-39',
           '4': '92515-49'}

UPPERS = ['None',
          'Cancelled',
          'Pe - no bx',
          'Pe with bx',
          'Oesophageal diatation',
          'Pe with APC',
          'HALO',
          'Pe with polypectomy',
          'Pe with varix banding',
          'BRAVO']

UPPER_DIC = {'None': None,
             'Cancelled': None,
             'Pe - no bx': '30473-00',
             'Pe with bx': '30473-01',
             'Oesophageal diatation': '30475-00',
             'Pe with APC': '30478-20',
             'HALO': '30478-20',
             'Pe with polypectomy': '30478-04',
             'Pe with varix banding': '30478-20',
             'BRAVO': '30490-00'}

COLONS = ['None',
          'Long Colon - no bx',
          'Long Colon with bx',
          'Long Colon with polyp',
          'Short Colon - no bx',
          'Short Colon with bx',
          'Short Colon with polyp',
          'Cancel lower procedure',
          'Colon - Govt FOB screening',
          'Colon with polyp - Govt FOB screening']

COLON_DIC = {'None': None,
             'Cancel lower procedure': None,
             'Long Colon - no bx': '32090-00',
             'Colon - Govt FOB screening': '32090-00',
             'Long Colon with bx': '32090-01',
             'Long Colon with polyp': '32093-00',
             'Colon with polyp - Govt FOB screening': '32093-00',
             'Short Colon - no bx': '32084-00',
             'Short Colon with bx': '32084-01',
             'Short Colon with polyp': '32087-00'}

BANDING = ['None',
           'Banding of haemorrhoids',
           'Anal dilatation']

BANDING_DIC = {'None': None,
               'Banding of haemorrhoids': '32135-00',
               'Anal dilatation': '32153-00'}


CONSULT_LIST = ['None', 'Long - 110', 'Short - 117']

CONSULT_DIC = {'None': None,
               'Long - 110': '110',
               'Short - 117': '117'}

FUNDS = ['HCF',
            'Medibank Private',
            'BUPA',
            'NIB',
            "The Doctor's Fund",
            'Australian Health Management',
            'Pensioner',
            'Uninsured',
            'Veterans Affairs',
            'Overseas',
            'Garrison Health',
            'Teachers Federation Health',
            'Westfund',
            'Australian Unity Health',
            'CBHS Health',
            'Defence Health',
            'CUA',
            'Frank Health',
            'GMHBA',
            'Peoplecare Health',
            'Railway & Transport Health',
            'Grand United Corporate Health',
            'health.com.au',
            'Health Insurance Fund',
            'HBF',
            'Naval Health Benefits',
            'Reserve Bank']
