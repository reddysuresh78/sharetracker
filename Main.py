from ShareUtils import *
from SMSUtils import *
from FnOUtils import *
from InterestedStocks import *
from collections import defaultdict
import schedule
import math

import time
import re
from time import gmtime, strftime

from collections import deque
from pprint import pprint

#Global deque
que = deque(maxlen=10)

dayMaxPerShare = {}
bucketSMSList = {}

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

def prepareAndSendSMS(scrips):

    to = "9000111935"
    user = "9000111935"
    pwd = "M2924R"

    # bestScrips = scrips.loc[scrips.buyIndicator == 'YES']

    bucketSMSList, text = getSMSText(scrips )

    return bucketSMSList, text


    # okScrips = scrips.loc[scrips.buyIndicator == 'NO']
    #
    # bucketSMSList, text = getSMSText(okScrips, True)

    # for key, value in bucketSMSList.items():
    #     print str(key) + " " + str(value)

    # print( strftime("%H:%M:%S", time.localtime()) + ":# " +  text)
    # sendSMS(user,pwd, to, text)


def getVolumesForGoodScrips(scripsDF):
    scripsDF['totalBuyQuantity'] = ""
    scripsDF['totalSellQuantity'] = ""
    scripsDF['buyIndicator'] = ""
    scripsDF['Symbol'] = ""
    scripsDF['SMSSymbol'] = ""
    scripsDF['dayHigh'] = ""

    curIndex = 0
    for (idx, row) in scripsDF.iterrows():
        totalBuyQuantity, totalSellQuantity = 0,0
        founddf = intDF.loc[intDF.FullName.str.contains(row.Stock) | (intDF.Symbol == row.Stock.upper())]
        scrip= founddf.iloc[0].Symbol
        smsScrip = founddf.iloc[0].SMSSymbol
        #Get buy/sell quantity only for top 20 shares.
        if (curIndex <= 20):
            totalBuyQuantity, totalSellQuantity, dayHigh = getTotalBuySellVolumes(scrip)

        row.Symbol = scrip  #This is not assigned correctly
        row.SMSSymbol = smsScrip
        row.totalBuyQuantity = totalBuyQuantity
        row.totalSellQuantity = totalSellQuantity
        row.dayHigh= dayHigh
        row.buyIndicator = "YES" if (totalBuyQuantity > totalSellQuantity) else "NO"
        curIndex += 1


    return scripsDF

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
    bucketSMSList, text = prepareAndSendSMS(goodScrips)
    #
    # for key, value in bucketSMSList.items():
    #     print "SMS: "  + str(key) + " " + (" ".join(value))
    #
    # print (strftime("%H:%M:%S", time.localtime()) + ": " + text)

    # goodScrips = [x.strip(" \t\n\r").encode('ascii') for x in goodScrips]
    # pprint(goodScrips)
    # print goodScrips
    return bucketSMSList, text

def processResultsScheduled():
    schedule.every(1).minutes.do(processResults)
    while True:
        schedule.run_pending()
        time.sleep(1)

# processResults()
# processResultsScheduled()