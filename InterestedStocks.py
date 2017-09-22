import pandas as pd
import re


def loadInterestingStocks():

    df = pd.read_csv("E:\\shares\\fno.csv")

    df['FullName'] =  df['FullName'].apply( lambda val:  re.sub('[^A-Za-z0-9]+', '', val))

    return df





