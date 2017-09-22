import urllib2
import pandas as pd
from bs4 import BeautifulSoup
import re
from SequenceUtils import *

def getGainersTableFromURL():
    gainers = "http://money.rediff.com/gainers/bse/daily/groupa?src=gain_lose"
    page = urllib2.urlopen(gainers)
    soup = BeautifulSoup(page, "html5lib")
    gainersTable = soup.find('table', class_='dataTable')
    return gainersTable

def getGainersDFFromTable(table):
    global counter
    # Generate lists
    scripName = []
    prevPrice = []
    curPrice = []
    change = []

    count = 0
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        if len(cells) == 5:  # Only extract table body not heading
            count = count + 1
            stock = cells[0].find("a").string
            stock = re.sub('[^A-Za-z0-9]+', '', stock)
            scripName.append(stock)
            prevPrice.append(cells[2].find(text=True))
            curPrice.append(cells[3].find(text=True))
            change.append(cells[4].find(text=True))

        if count == 500:
            break

    df = pd.DataFrame(scripName, columns=['Stock'])
    df['Prev'] = prevPrice
    df['Current'] = curPrice
    df['Change'] = change
    seqNo = next(counter)
    df['Seq'] = [seqNo] * len(scripName)
    return df


def getLatestGainersDF():
    # print "Getting Data"
    scripTable = getGainersTableFromURL()
    df = getGainersDFFromTable(scripTable)

    # print que[-1]["Stock"].iloc[0]
    return df