"""new jt analysis program using database."""


def jt_analysis():
    """Print whether on weekly target from first_date.
    Note need to set both first_date and first_date_lex
    """
    first_date = datetime.datetime(2018, 04, 1)
    first_date_lex = '20180401'
    today = datetime.datetime.today()
    today_lex = today.strftime('%Y' + '%m' + '%d')
    db_file = 'sqlite:///d:\\JOHN TILLET\\episode_data\\aneasthetics.db'
    db = dataset.connect(db_file)
    table = db['episodes']
    results = db.query('COUNT(*) FROM episodes WHERE anaesthetist = "Dr J Tillett" and today_lex > first_date_lex')

    days_diff = (today - first_date).days
    desired_weekly = 60
    desired_number = int(days_diff * desired_weekly / 7)
    excess = results - desired_number
    print('{} excess to average {} per week.'.format(excess, desired_weekly))
    input('Hit Enter to continue.')
