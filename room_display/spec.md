## background
I have a medical billing system called docbill.py written in python (not currently in this folder but see docbill_snippets.py). It runs in two operating rooms 'room1', 'room2'. I want to display on a web page what procedures have been done in that room on the current day eg 'https:-------/room1.html
The program is run after each operation and uploads the data for that procedure to amazon S3 as either room1.csv or room2.csv
The data is like this 
headers = [
        "date",
        "mrn",
        "name",
        "out_theatre",
        "staff",
        "upper",
        "lower",
        "banding",
        "polyp",
        "rebatable",
    ]

I have a digital ocean server with Flask installed up and running with your help.
I want the server to display the S3 data on a simple web page using Jinja2 which I understand. It needs to self update.
You will see in chat_history.md a previous convo on how to do the display.
