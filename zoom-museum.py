#!/bin/python3
from bs4 import BeautifulSoup
import requests, re, sys, argparse
from datetime import date, timedelta
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from pathlib import Path

filename = Path("zoom_museum_matches.txt")

def hitWasAlreadyMatched(match):
    if not filename.is_file():
        return False
    else:
        with open(filename,"r") as fin:
            lines = fin.readlines()
        for line in lines:
            if match in line:
                return True
            else:
                return False

parser = argparse.ArgumentParser(
                    prog='Zoom Museum Slot Finder')
parser.add_argument('-d', '--days-delta', default=10)
parser.add_argument('-a', '--adults', required=True)
parser.add_argument('-c', '--children', required=True)parser.add_argument('-D', '--day', required=True)
parser.add_argument('-H', '--hour', required=True)
parser.add_argument('-r', '--recipients', default=[], required=True, action='append')
args = parser.parse_args()

todaysDate = date.today()
endDate = todaysDate + timedelta(days=args.days_delta)adults = args.adults
children = args.children
dayWanted = args.day
hourWanted = args.hour
URL = "https://www.kindermuseum.at/jart/prj3/zoom/main.jart?reserve-mode=active&rel=en&content-id=1544632271878&do-search=yes&OrganizationStructureIdList=65ae9712-daba-4f39-9a44-31eb9d56ded0&StartDate=" + str(todaysDate) + "&EndDate=" + str(endDate) + "&anzahl-kinder=" + str(children) + "&anzahl-erwachsene=" + str(adults)

msg = MIMEText(
        "New slot open for " +
        str(adults) +
        " adult(s) and " +
        str(children) +
        " child(ren) on " +
        dayWanted +
        " at " +
        hourWanted +
        " for the Zoom Museum!\n\nBook here: " +
        URL)
msg["From"] = "me <me@me.org>"
msg['To'] = ', '.join(args.recipients)

html_document = requests.get(URL,timeout=30).text

soup = BeautifulSoup(html_document, 'html.parser')
results = soup.find_all(attrs={'class':['item']})

if len(results)>0:
    for result in results:
            if dayWanted in str(result) and hourWanted in str(result):
                dateFound = re.search(r'\w{3}, \d{2}\. \w+ \d{4}', str(result)).group(0)
                if hitWasAlreadyMatched(match = dateFound):
                        continue
                else:
                    msg["Subject"] = "Zoom Museum Ocean opening (" + str(dateFound) + ")"
                    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
                    p.communicate(msg.as_bytes())
                    with open(filename, "a") as file:
                        file.write(dateFound+"\n")