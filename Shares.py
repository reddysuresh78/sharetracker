import sys
from flask import Flask, request, jsonify, g
import pandas as pd
from Main import *
from SharesInfo import *



app = Flask(__name__, static_url_path='')

def get_gainers_object():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    gainers = getattr(g, 'gainers', None)
    if gainers is None:
        print "Creating new object"
        gainers = g.gainers = SharesInfo("Gainers", 10, "http://money.rediff.com/gainers/bse/daily/groupa?src=gain_lose")
    return gainers

@app.route('/gainers')
def gainers():
    return app.send_static_file('gainers.html')

@app.route('/losers')
def losers():
    return app.send_static_file('losers.html')


@app.route('/myfunctions.js')
def js():
    return app.send_static_file('myfunctions.js')

@app.route('/refreshGainers', methods=['GET'])
def refreshGainers():

    print "Getting Gainers now"

    gainers_object = get_gainers_object()

    bucketSMSList, text =   gainers_object.getLatestShareList()

    print "Done"

    return jsonify(bucketSMSList)

@app.route('/refreshGainers1', methods=['GET'])
def refreshGainers1():

    print "Getting Gainers now"
    bucketSMSList, text = getGainers()

    # sms = ""
    # # for key, value in bucketSMSList.items():
    # #     sms = sms + str(key) + " " + (" ".join(value)) + "\n"
    #
    # for key, value in bucketSMSList.items():
    #     sms = sms + str(key) + " " +  str(value) + "\n"

    # print (strftime("%H:%M:%S", time.localtime()) + ": " + text)

    print "Done"

    # print text

    # return jsonify({'prediction': str(strftime("%H:%M:%S", time.localtime()) + ": " + text)})

    return jsonify(bucketSMSList)

@app.route('/refreshLosers', methods=['GET'])
def refreshLosers():

    print "Getting Losers now"

    losers = SharesInfo("Losers", 10, "http://money.rediff.com/losers/bse/daily/groupa?src=gain_lose")

    bucketSMSList, text = losers.getLatestShareList()

    print "Done"

    return jsonify(bucketSMSList)

print "Listening"
app.run(host='localhost', port='8020')