import math
import time
from collections import defaultdict
from collections import deque
from multiprocessing.dummy import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count

import schedule

from FnOUtils import *
from InterestedStocks import *
from ShareUtils import *

#Global deque
gainersQue = deque(maxlen=10)
losersQue = deque(maxlen=10)

dayMaxPerShare = {}
bucketSMSList = {}

intDF = loadInterestingStocks()

#bucketSMSList.append()

def combineGainerResults():
    result = pd.concat(list(gainersQue))
    result.sort_values(['Stock', 'Seq'], ascending=[False, False], inplace=True)
    latestList = gainersQue[-1].sort_values(['Stock'], ascending=[True], inplace=False)

    return result, latestList['Stock']

def analyzeGainerResults(result, latestList):
    curMax = result['Seq'].max()
    # print curMax
    scrips = []
    latestChange = []
    curPrice = []
    goodChange = []
    for scrip in latestList:
        currentPrice, change, isGood =  isGoodScrip(scrip, result[result['Stock'] == scrip])
        scrips.append(scrip)
        latestChange.append(change)
        curPrice.append(currentPrice)
        goodChange.append("Y" if (isGood) else "N" )

    df = pd.DataFrame(scrips, columns=['Stock'])
    df['Gain'] = latestChange
    df['CurPrice'] = curPrice
    df['goodChange'] = goodChange

    df.sort_values(['Gain' ], ascending=[False], inplace=True)

    return df

def isGoodScrip(scrip, history):
    latest = history['Change'].iloc[0]
    oldest = history['Change'].iloc[-1]

    curPrice = history['Current'].iloc[0]
    #print scrip, latest, oldest
    return  curPrice, latest.lstrip('+').strip() , (float(latest.lstrip('+').strip()) - float(oldest.strip('+').strip()) >= 0)

def getSMSText(scrips ):
    text = ""
    smsText = ""
    smsPerBucket = defaultdict(list)
    curPos= 0
    for (idx, row) in scrips.iterrows():

        curRow = {}

        curRow['symbol'] = row.Symbol
        curRow['curPrice'] = row.CurPrice
        curRow['gain'] = row.Gain
        curRow['buyQuantity'] = row.totalBuyQuantity
        curRow['sellQuantity'] = row.totalSellQuantity
        curRow['dayHigh'] = row.dayHigh
        curRow['buyIndicator'] = "Y" if (row.buyIndicator=="YES") else "N"
        curRow['newEntrant'] = "N"
        curRow['increased'] = row.goodChange
        curRow['dayLow'] = row.dayLow
        curRow['previousClose'] = row.previousClose
        if(getfloat(row.previousClose) != 0):
            curRow['gainVal'] = round(getfloat(row.CurPrice) - getfloat(row.previousClose), 2)
        else:
            curRow['gainVal'] = "-"

        curRow['threshold'] = "Y" if (getfloat(row.threshold) <= getfloat(row.Gain) ) else "N"

        text = text + row.SMSSymbol
        if (row.buyIndicator == 'YES'):
            text = text + "*"
        text = text +  "[" + row.CurPrice + " " + row.Gain + "] "

        curBucket = int( math.ceil ((curPos +1) /5.0))
        smsText = ""
        if (row.Symbol in bucketSMSList):
            sentBuckets = bucketSMSList[row.Symbol]
            minBucket = min(sentBuckets or [5])
            #If symbol's current bucket is not yet used for SMS and this is a better bucket than earlier
            if ((not (curBucket) in sentBuckets) |  curBucket < minBucket   ):
                smsText = smsText + row.SMSSymbol
                if(row.buyIndicator == 'YES'):
                    smsText = smsText + "*"

                smsText = smsText + "[" + row.CurPrice + " " + row.Gain + "]"

                sentBuckets.append(curBucket)
                bucketSMSList[row.Symbol] = sentBuckets
                curRow['newEntrant'] = "Y"
                #print bucketSMSList[row.Symbol]
                smsPerBucket[curBucket].append(curRow)
            else:
                smsPerBucket[curBucket].append(curRow)
        else:
            bucketSMSList[row.Symbol] = [curBucket]
            smsText = smsText + row.SMSSymbol
            if (row.buyIndicator == 'YES'):
                smsText = smsText + "*"
            smsText = smsText + "[" + row.CurPrice + " " + row.Gain + "]"
            curRow['newEntrant'] = "Y"
            smsPerBucket[curBucket].append(curRow)
        curPos+=1

    return smsPerBucket, text

#Not used now
def prepareAndSendSMS(scrips):

    to = "9000111935"
    user = "9000111935"
    pwd = "M2924R"

    bucketSMSList, text = getSMSText(scrips )

    return bucketSMSList, text
    # sendSMS(user,pwd, to, text)


def getVolumesForGoodScrips(scripsDF):
    scripsDF['totalBuyQuantity'] = ""
    scripsDF['totalSellQuantity'] = ""
    scripsDF['buyIndicator'] = ""
    scripsDF['Symbol'] = ""
    scripsDF['SMSSymbol'] = ""
    scripsDF['dayHigh'] = ""
    scripsDF['threshold'] = ""
    scripsDF['dayLow'] = ""
    scripsDF['previousClose'] = ""

    topTwenty = []

    curIndex = 0
    for (idx, row) in scripsDF.iterrows():
        totalBuyQuantity, totalSellQuantity, dayHigh = 0,0,0
        founddf = intDF.loc[intDF.FullName.str.contains(row.Stock) | (intDF.Symbol == row.Stock.upper())]
        scrip= founddf.iloc[0].Symbol
        smsScrip = founddf.iloc[0].SMSSymbol
        threshold = founddf.iloc[0].threshold
        row.Symbol = scrip  #This is not assigned correctly
        row.SMSSymbol = smsScrip
        row.threshold = threshold
        if (curIndex <= 20):
            topTwenty.append(scrip)
        curIndex += 1

    volumesInfo = getVolumesInfo(topTwenty)
    curIndex = 0
    for (idx, row) in scripsDF.iterrows():
        if (curIndex <= 20):
            totalBuyQuantity, totalSellQuantity, dayHigh, dayLow, previousClose, latestPrice, pctChange, change = volumesInfo[curIndex]
            row.totalBuyQuantity = totalBuyQuantity
            row.totalSellQuantity = totalSellQuantity
            row.dayHigh= dayHigh
            row.dayLow = dayLow
            row.previousClose = previousClose
            row.curPrice = latestPrice
            row.gain = pctChange
            row.buyIndicator = "YES" if (totalBuyQuantity > totalSellQuantity) else "NO"
        else:
            break
        curIndex += 1
        #  #Get buy/sell quantity only for top 20 shares.
        # if (curIndex <= 20):
        #     totalBuyQuantity, totalSellQuantity, dayHigh = getTotalBuySellVolumes(scrip)

    return scripsDF

def getVolumesInfo(scrips):
    pool = Pool(cpu_count() * 10)  # Creates a Pool with cpu_count * 2 threads.

    #for (idx, row) in intDF.iterrows():
    results = pool.map(getTotalBuySellVolumes, scrips)  # results is a list of all the placeHolder lists returned from each call to crawlToCSV

    return results

def processResultsScheduled():
    schedule.every(1).minutes.do(getGainers)
    while True:
        schedule.run_pending()
        time.sleep(1)
# processResults()
# processResultsScheduled()

def getGainers():
    #Get all gainers df
    gainersDF = getLatestGainersDF()

    #Remove non F&O shares from it
    for scrip in gainersDF['Stock']:
        founddf = intDF.loc[intDF.FullName.str.contains(scrip) | (intDF.Symbol == scrip.upper())]
        if (founddf.empty):
            #print "Removing ", scrip
            gainersDF = gainersDF[gainersDF.Stock != scrip]

    gainersQue.append(gainersDF)
    result, latestList = combineGainerResults()
    goodScrips = analyzeGainerResults(result, latestList)

    goodScrips = getVolumesForGoodScrips(goodScrips)

    # print goodScrips
    bucketSMSList, text = getSMSText(goodScrips )

    return bucketSMSList, text


def getLosers():
    #Get all gainers df
    losersDF = getLatestLosersDF()

    #Remove non F&O shares from it
    for scrip in losersDF['Stock']:
        founddf = intDF.loc[intDF.FullName.str.contains(scrip) | (intDF.Symbol == scrip.upper())]
        if (founddf.empty):
            #print "Removing ", scrip
            losersDF = losersDF[losersDF.Stock != scrip]

    losersQue.append(losersDF)
    result, latestList = combineLoserResults()
    goodScrips = analyzeLoserResults(result, latestList)

    goodScrips = getVolumesForGoodScrips(goodScrips)

    # print goodScrips
    bucketSMSList, text = getSMSText(goodScrips )

    return bucketSMSList, text




