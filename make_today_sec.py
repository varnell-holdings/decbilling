from jinja2 import FileSystemLoader, Environment
import os
import collections
import csv
import datetime


def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)


def make_today_sec():
    today_date = datetime.datetime.now()
    today_str = today_date.strftime(
        '%A' + '  ' + '%d' + ':' + '%m' + ':' + '%Y')
    today_data = collections.deque()
    with open('test_data.csv') as data:
        reader = csv.reader(data)
        for ep in reader:
            today_data.appendleft(ep)
    a = render_from_template(
        os.getcwd(),
        'today_sec_template.html',
        today_data=today_data, today_date=today_str)
    with open('test.html', 'w') as f:
        f.write(a)


if __name__ == '__main__':
    make_today_sec()
