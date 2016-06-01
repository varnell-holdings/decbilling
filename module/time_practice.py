#time_practice.py

from datetime import *
from dateutil.relativedelta import *
from dateutil.parser import *
timer = 23
now = datetime.now()
outtime = now+relativedelta(minutes=+3)
indelta = timer + 3
intime = now+relativedelta(minutes=-indelta)
anaesthetic_time = indelta
print now.strftime('%H' + ':' + '%M')
print outtime.strftime('%H' + ':' + '%M')
print intime.strftime('%H' + ':' + '%M')

## age calculations

bc_dob = '23/8/1945'
dob = parse(bc_dob)
print dob
age_sep = relativedelta(now, dob)
print age_sep.years