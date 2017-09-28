import urllib2
import pandas as pd
from bs4 import BeautifulSoup
import re
from SequenceUtils import *
import json

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

def getTotalBuySellVolumes(scrip):
    # print "Current scrip ", scrip

    scrip = re.sub('[&]+', '%26', scrip)

    fnoURL = "https://nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol=" + scrip

    r = urllib2.Request(fnoURL)
    r.add_header('Accept', '*/*')
    r.add_header('User-Agent', 'My scraping program <author@example.com>')
    opener = urllib2.build_opener()
    page = opener.open(r).read()

    # page = urllib2.urlopen(fnoData)
    soup = BeautifulSoup(page, "html5lib")
    val = soup.find(id="responseDiv").text

    j = json.loads(val)
    totalBuyQuantity = j['data'][0]['totalBuyQuantity']
    totalBuyQuantity = getfloat(totalBuyQuantity.replace(',', ''))

    totalSellQuantity = j['data'][0]['totalSellQuantity']
    totalSellQuantity = getfloat(totalSellQuantity.replace(',', ''))

    dayHigh = j['data'][0]['dayHigh']
    dayHigh = getfloat(dayHigh.replace(',', ''))

    return totalBuyQuantity, totalSellQuantity, dayHigh

def getfloat(value):
  try:
    val = float(value)
    return val
  except:
    return 0.0