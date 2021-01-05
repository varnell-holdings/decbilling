#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 15:11:29 2020

@author: jtair
"""

import datetime as dt
from dateutil import relativedelta
import time
last_out = True
now1 = dt.datetime.now()
print(now1)
time.sleep(5)
now2 = dt.datetime.now()
print(now2)

print(now2 > now1)


if (last_out) and (now2 > now1):
    now2 = now1 + relativedelta.relativedelta(minutes=3)
    print(now2)
    last_out = now2
last_out = now1