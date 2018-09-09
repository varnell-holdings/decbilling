"""New function to_anaesth_csv which puts the data of the  anaesthetists
who are using my billing systeminto a csv file.
"""


def to_anaesth_csv(episode_data, anaesthetist):
    """Write tuple of anaesthetic billing data to csv."""
    surname = anaesthetist.split()[-1]
    csvfile = 'd:\\JOHN TILLET\\episode_data\\{}.csv'.format(surname)
    with open(csvfile, 'a') as handle:
        datawriter = csv.writer(handle, dialect='excel', lineterminator='\n')
        datawriter.writerow(episode_data)
