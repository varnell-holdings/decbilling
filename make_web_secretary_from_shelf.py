import datetime
import os
import shelve

from jinja2 import Environment, FileSystemLoader



def make_web_secretary_from_shelf():
    """Render jinja2 template
    and write to file for web page of today's patients
    """
    today = datetime.datetime.today()
    today_str = today.strftime(
        '%A' + '  ' + '%d' + '-' + '%m' + '-' + '%Y')
    today_db = today.strftime("%Y-%m-%d")
    with shelve.open('{}'.format(today_db)) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x['out_theatre'], reverse=True)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(base_path)
    path_to_template = os.path.join(base_path, 'today_sec_template.html')
    loader = FileSystemLoader(os.path.dirname(path_to_template))
    env = Environment(loader=loader)
    template_name = 'today_sec_template.html'
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open('today_new.html', 'w') as f:
        f.write(a)

if __name__ == '__main__':
    make_web_secretary_from_shelf('today_path')
