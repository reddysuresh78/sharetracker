from ShareUtils import *
from SMSUtils import *
from FnOUtils import *
from InterestedStocks import *
import schedule
import json
import time
import re
from time import gmtime, strftime


from collections import deque
from pprint import pprint

#Global deque
que = deque(maxlen=10)

dayMaxPerShare = {}
bucketSMSList = []

intDF = loadInterestingStocks()

#bucketSMSList.append()

def combineResults():
    result = pd.concat(list(que))
    result.sort_values(['Stock', 'Seq'], ascending=[False, False], inplace=True)
    latestList = que[-1].sort_values(['Stock'], ascending=[True], inplace=False)

    return result, latestList['Stock']

def analyzeResults(result, latestList):
    curMax = result['Seq'].max()
    # print curMax
    scrips = []
    latestChange = []
    for scrip in latestList:
        change, isGood =  isGoodScrip(scrip, result[result['Stock'] == scrip])
        if(isGood):
            scrips.append(scrip)
            latestChange.append(change)

    df = pd.DataFrame(scrips, columns=['Stock'])
    df['Gain'] = latestChange


    df.sort_values(['Gain' ], ascending=[False], inplace=True)

    return df

def isGoodScrip(scrip, history):
    latest = history['Change'].iloc[0]
    oldest = history['Change'].iloc[-1]
    #print scrip, latest, oldest
    return  latest.lstrip('+').strip() , (float(latest.lstrip('+').strip()) - float(oldest.strip('+').strip()) >= 0)


def processResults():
    #Get all gainers df
    gainersDF = getLatestGainersDF()

    #Remove non F&O shares from it
    for scrip in gainersDF['Stock']:
        founddf = intDF.loc[intDF.FullName.str.contains(scrip) | (intDF.Symbol == scrip.upper())]
        if (founddf.empty):
            #print "Removing ", scrip
            gainersDF = gainersDF[gainersDF.Stock != scrip]

    que.append(gainersDF)
    result, latestList = combineResults()
    goodScrips = analyzeResults(result, latestList)

    goodScrips = getVolumesForGoodScrips(goodScrips)

    # print goodScrips
    prepareAndSendSMS(goodScrips)

    # goodScrips = [x.strip(" \t\n\r").encode('ascii') for x in goodScrips]
    # pprint(goodScrips)
    # print goodScrips
    return goodScrips

def prepareAndSendSMS(scrips):

    to = "9000111935"
    user = "9000111935"
    pwd = "M2924R"

    bestScrips = scrips.loc[scrips.buyIndicator == 'YES']

    text = ""
    for (idx, row) in bestScrips.iterrows():
        text = text + row.SMSSymbol + "[" + row.Gain + "] "

    okScrips = scrips.loc[scrips.buyIndicator == 'NO']

    print (  strftime("%H:%M:%S", time.localtime()) + ": " + text)

    text = ""
    for (idx, row) in okScrips.iterrows():
        text = text + row.SMSSymbol + "[" + row.Gain + "] "

    print( strftime("%H:%M:%S", time.localtime()) + ":# " +  text)
    # sendSMS(user,pwd, to, text)


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

    return totalBuyQuantity, totalSellQuantity

def getfloat(value):
  try:
    val = float(value)
    return val
  except:
    return 0.0


def getVolumesForGoodScrips(scripsDF):
    scripsDF['totalBuyQuantity'] = ""
    scripsDF['totalSellQuantity'] = ""
    scripsDF['buyIndicator'] = ""
    scripsDF['Symbol'] = ""
    scripsDF['SMSSymbol'] = ""

    for (idx, row) in scripsDF.iterrows():
        founddf = intDF.loc[intDF.FullName.str.contains(row.Stock) | (intDF.Symbol == row.Stock.upper())]
        scrip= founddf.iloc[0].Symbol
        smsScrip = founddf.iloc[0].SMSSymbol
        totalBuyQuantity, totalSellQuantity = getTotalBuySellVolumes(scrip)
        row.Symbol = scrip  #This is not assigned correctly
        row.SMSSymbol = smsScrip
        row.totalBuyQuantity = totalBuyQuantity
        row.totalSellQuantity = totalSellQuantity
        row.buyIndicator = "YES" if (totalBuyQuantity > totalSellQuantity) else "NO"

    return scripsDF

def processResultsScheduled():
    schedule.every(1).minutes.do(processResults)
    while True:
        schedule.run_pending()
        time.sleep(1)

# processResults()
processResultsScheduled()