import urllib2
import pandas as pd
import schedule
from bs4 import BeautifulSoup
from collections import deque
from itertools import count
from pprint import pprint
import json
import re

def getFnOVolsFromURL(scrip):
    # print "Current scrip ", scrip

    scrip = re.sub('[&]+', '%26', scrip)

    fnoURL = "https://nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + scrip

    r = urllib2.Request(fnoURL)
    r.add_header('Accept', '*/*')
    r.add_header('User-Agent', 'My scraping program <author@example.com>')
    opener = urllib2.build_opener()
    page = opener.open(r).read()

    # page = urllib2.urlopen(fnoData)
    soup = BeautifulSoup(page, "html5lib")
    fnoTable = soup.find(id="octable")

    return fnoTable


def getFnOVolFromTable(table):
    finalRow = table.findAll("tr")[-1]

    cells = finalRow.findAll('td')
    if len(cells) > 1:
        stock = cells[3].get_text()
        return stock
        # print stock


def getRecentQuoteValue(scrip):
    # print "Current scrip ", scrip

    fnoURL = "https://nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol=" + scrip

    r = urllib2.Request(fnoURL)
    r.add_header('Accept', '*/*')
    r.add_header('User-Agent', 'My scraping program <author@example.com>')
    opener = urllib2.build_opener()
    page = opener.open(r).read()

    # page = urllib2.urlopen(fnoData)
    soup = BeautifulSoup(page, "html5lib")
    val = soup.find('div', class_='content_big')
    val = val.find('table').find('span').find('b').text
    val = float(val.split()[-1])

    return val


def getCurValue(scrip):
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
    data = j['data'][0]['totalTradedVolume']
    data = float(data.replace(',', ''))

    lastPrice = j['data'][0]['lastPrice']
    lastPrice = float(lastPrice.replace(',', ''))

    print  scrip, "|", data, "|", lastPrice

    return ""


def getFnOScripsFromURL():
    fnoURL = "https://nseindia.com/products/content/derivatives/equities/fo_underlyinglist.htm"

    r = urllib2.Request(fnoURL)
    r.add_header('Accept', '*/*')
    r.add_header('User-Agent', 'My scraping program <author@example.com>')
    opener = urllib2.build_opener()
    page = opener.open(r).read()

    # page = urllib2.urlopen(fnoData)
    soup = BeautifulSoup(page, "html5lib")
    fnoTable = soup.find('table')

    return fnoTable


def getFnODataFrameFromTable(table):
    # Generate lists
    scripName = []

    count = 0
    for row in table.findAll("tr"):
        cells = row.findAll('td')
        if len(cells) > 1:
            stock = cells[1].find("a").string
            scrip = cells[2].find("a").string

            stock = re.sub('[^A-Za-z0-9]+', '', stock)
            # scrip = re.sub('[^A-Za-z0-9]+', '', scrip)

            # stock = ''.join(e for e in stock if e.isalnum())

            # scripName.append(stock)
            scripName.append(scrip)

    df = pd.DataFrame(scripName, columns=['Stock'])

    return df


def getFnOData():
    # print "Getting Data"
    scripTable = getFnOScripsFromURL()
    df = getFnODataFrameFromTable(scripTable)
    # print df
    return df


def extractFnOData():
    df = getFnOData()
    for (idx, row) in df.iterrows():
        if (idx > 10):
            table = getFnOVolsFromURL(row.Stock)
            value = getFnOVolFromTable(table)
            # recent = getCurValue(row.Stock)

            print row.Stock, "|", value

