import sys
from flask import Flask, request, jsonify
import pandas as pd
from Main import *

app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
    return app.send_static_file('shares.html')

@app.route('/myfunctions.js')
def js():
    return app.send_static_file('myfunctions.js')

@app.route('/refreshGainers', methods=['GET'])
def refreshGainers():

    print "Getting it now"
    bucketSMSList, text = getGainers()

    sms = ""
    # for key, value in bucketSMSList.items():
    #     sms = sms + str(key) + " " + (" ".join(value)) + "\n"

    for key, value in bucketSMSList.items():
        sms = sms + str(key) + " " +  str(value) + "\n"

    # print (strftime("%H:%M:%S", time.localtime()) + ": " + text)

    print "Done"

    print bucketSMSList[1]

    data = {
        'status': 'OK',
        'sms': text,
        'gainers': sms
    }

    print text

    # return jsonify({'prediction': str(strftime("%H:%M:%S", time.localtime()) + ": " + text)})

    return jsonify(bucketSMSList)


print "Listening"
app.run(host='localhost', port='8020')