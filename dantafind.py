# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 13:49:34 2018

@author: John2
"""

#! /usr/bin/python
import csv
import colorama
from fuzzyfinder import fuzzyfinder

colorama.init(autoreset=True)

def clear():
    print('\033[2J')  # clear screen
    print('\033[1;1H')  # move to top left


def dantafind():
    """Search for patients in Danta study."""
    file = 'D:\\JOHN TILLET\\episode_data\\dantapolypdata.csv'
    with open(file, 'r') as h:
        reader =csv.reader(h, delimiter=',')
        pat_list = [p[0].lower() for p in reader]
    clear()           
    while True:
        print()
        query_string = input('Name in lower case, q to quit:  ')
        if query_string == 'q':
            break     
        if query_string == '':
            clear()
            continue
        try:
            suggestions = fuzzyfinder(query_string, pat_list)
            suggestions = sorted(
                        list(suggestions), key= lambda x: x.split()[-1])
            clear()
            if not suggestions:
                print('No one here.')
            else:
                for p in suggestions:
                    print(p)
        except UnicodeDecodeError:
            print('Try another list of letters!')
            continue

if __name__ == '__main__':
    dantafind()
