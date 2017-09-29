import urllib2
import csv
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count
import re
from SequenceUtils import *
import json
from InterestedStocks import *



def getfloat(value):
  try:
    val = float(value)
    return val
  except:
    return 0.0

def crawlToCSV(scrip):

    print "Getting for " + scrip
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

    return (totalBuyQuantity, totalSellQuantity, dayHigh)

if __name__ == "__main__":
    intDF = loadInterestingStocks()

    print cpu_count()

    pool = Pool(cpu_count() * 2)  # Creates a Pool with cpu_count * 2 threads.

    #for (idx, row) in intDF.iterrows():
    results = pool.map(crawlToCSV, intDF["Symbol"])  # results is a list of all the placeHolder lists returned from each call to crawlToCSV

    for result in results:
        print result