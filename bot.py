#!/usr/bin/env python3
# File: stock-bot
# Author: SNTag (SNTagore@protonmail.com)
# Date: 25/01/2020
# Description:
# Usage:
# Version: 0.0.9


import email                    # for emailing
import smtplib                  # For emailing
from alpha_vantage.timeseries import TimeSeries  # For Data Collection
import matplotlib               # loaded to set matplotlib backend
import matplotlib.pyplot as plt # FOR FUN: Generates plots
import pandas as pd             # Used to config stocks
import time                     # Time tracking
import datetime as dt           # Used to maintain banned list
import os                       # For file/plot
import configparser             # For soft-coding bot-config
import subprocess               # For some quick quality checking
import json                     # For reading/saving to json
import sys                      # needed






"""For setting the Bot-configs"""
config = configparser.ConfigParser()
config.read("/etc/bot-login.cnf")              # Config location
username = config.get('bot-email', 'username') # address the bot will talk with
botName = config.get('bot-email', 'botName')   # bot email address
botPass = config.get('bot-email', 'botPass')   # bot email password
smtpAddress = config.get('bot-email', 'smtpAddress') # bot email SMTP address
smtpPort = config.get('bot-email', 'smtpPort') # bot email SMTP port
filestamp = time.strftime('%Y-%m-%d')          # isn't this unnecessary
apiKey = config.get('AV', 'apiKey')            # Alpha Vantage API key
outputDailyTimeSeries = config.get('Data', 'stock-bot-daily-timeseries') # to set up custom output folders
outputGraphs = config.get('Data', 'stock-bot-graphs') # to set up custom output folders
inputSummary = config.get('Data', 'portfolio-summary') # to set up custom output folders

"""Background details"""
matplotlib.use('AGG')           # Used to set matplotlib backend
newBanned = []                  # stocks that are just discovered to be ban-nable
newDividend = []                # stocks that are paying a dividend today

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# if os.path.isdir("./output") == False:
#     os.makedirs("./output")
#     if os.path.isdir("./output/graph") == False:
#         os.makedirs("./output/graph")
#     if os.path.isdir("./output/data") == False:
#         os.makedirs("./output/data")
# if os.path.isdir("./input") == False:
#     os.makedirs("./input")


"""Loading json file (contains lists,dicts,variables of interest)"""
if os.path.isfile("./input/status.json"):
    with open('./input/status.json') as jsonIn:
        dataStatus = json.load(jsonIn)
else:
    oldBanned = {}
    repeatCounter = 0
    dataStatus = {}
    dataStatus["oldBanned"] = oldBanned
    dataStatus["repeatCounter"] = repeatCounter



"""Sets the time variables"""
dateToday = dt.date.today()
dateTodayNYC = dt.date.today() - dt.timedelta(hours=8)  # TODO:[B] add timezone.dt support
dateYesterdayNYC = dt.date.today() - dt.timedelta(hours=24)  # TODO:[B] add timezone.dt support
dateTwoWeeks = dateToday - dt.timedelta(14)








def main():
    """Will generate, process, and save csv files.  It will also determine if conditions have been triggered."""
    ##### Adding a short section for basic quality control checking (simple way of counting # of runs)
    global dataStatus
    dataStatus["repeatCounter"] += 1

    ##### Loads companies of interest
    companiesMain = pd.read_csv(inputSummary, sep = ",")
    newBanned = []

    ##### pulls stock data and checks for conditions
    for row in range(companiesMain.shape[0]):      # for each portfolio
#        for column in range(companiesMain.shape[1]):  # for each stock
        if not pd.isnull(companiesMain.iloc[row,0]):
            tmpStock = str(companiesMain.iloc[row,0])
            print(f"formatting data for {tmpStock}")

            if tmpStock in dataStatus["oldBanned"]:
                dateTmp = dt.datetime.strptime(dataStatus["oldBanned"][tmpStock], '%Y-%m-%d').date()  # converts banned-date to datetime object for comparisons
                if dateTmp < dateTwoWeeks:
                    dataStatus["oldBanned"].pop(tmpStock, None)

            if tmpStock not in dataStatus["oldBanned"].keys():  # retrieves stock data
                # NOT banned (yet)
                # If conditon(s) failed, will trigger email and be added to banned list
                ts = TimeSeries(key=apiKey, output_format='pandas')
                data, meta_data = ts.get_daily_adjusted(symbol=tmpStock, outputsize='full')  # using adjusted to determine dividend yields

                ##### CONDITION1: dividend checker
                if (data["7. dividend amount"][0] > 0) and (dateToday > dateTodayNYC):
                    newDividend.append(tmpStock)

                ##### CONDITION2: Determine if there was a stock decline
                condition2 = (data["5. adjusted close"][0])/(data["5. adjusted close"][1])
                if (0.9 < (1-condition2) < 1.1):
                    dataStatus["oldBanned"][tmpStock] = f'{dateTwoWeeks}'
                    newBanned.append(tmpStock)

                # if condition2 == False:
                #     dataStatus["oldBanned"][tmpStock] = f'{dateTwoWeeks}'

                ##### Save data as CSV for processing as desired
                tmpStr = str(outputDailyTimeSeries + f"{tmpStock}-{dateToday}.csv")
                data.to_csv(tmpStr, index = True, )

                ##### plotting
                plotMaker(data, meta_data, tmpStock)

            oldDataDateFile = tmpStock+"-"+str(dateYesterdayNYC)+'.csv'
            oldDataDateFilePath = str(outputDailyTimeSeries+oldDataDateFile)
            newDataDateFile = tmpStock+"-"+str(dateTodayNYC)+'.csv'
            newDataDateFilePath = str(outputDailyTimeSeries+newDataDateFile)
            if os.path.isfile(oldDataDateFilePath):
                print("True")
                list_1 = pd.read_csv(newDataDateFilePath, sep = ",", header = None)
                list_2 = pd.read_csv(oldDataDateFilePath, sep = ",", header = None)
                list_2_nodups = list_2.drop_duplicates()
                total_pd = pd.merge(list_1 , list_2_nodups, on=[0])
                tmpStr = outputDailyTimeSeries + tmpStock + "-Sum.csv"
                total_pd.to_csv(tmpStr, sep= ",", header = None)
                tmpStr = "rm " + oldDataDateFilePath  # TODO:[C] should replace with something safer
                subprocess.call(tmpStr, shell=True)


            time.sleep(12.1)                            # makes script compatible with AV calls per minute limit

    # ##### Send email(s) if conditions were met
    # if len(newDividend) > 0:
    #     email_sending(msgDividendPay, newBanned, username, botName, botPass)

    # if len(newBanned) > 0:
    #     email_sending(msgDecline, username, botName, botPass)

    ##### Save status in json file (see ./input/status.json)
    with open('./input/status.json', 'w') as jsonOut:
        json.dump(dataStatus, jsonOut, indent=4)


def email_sending(msg, username, botName, botPass):
    """Will send relevant messages"""
    s = smtplib.SMTP(smtpAddress, smtpPort)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(botName, botPass)

    s.sendmail(botName, username, msg.as_string())

    s.quit()


def plotMaker(data, meta_data, tmpStock):
    print(f"Making graphs for {tmpStock}")
    data['4. close'].plot()
    plt.title(f'Daily Times Series for the {tmpStock} stock')
    plt.ylabel('Cost')
    plt.savefig(f'{outputGraphs}{tmpStock}-daily-timeseries.png')
    plt.clf()
    plt.cla()
    plt.close()






"""Email templates here"""
##### General templates
# msg = email.message_from_string(
#     'stock-bot is reported a stock decline in the following stocks \n'
#     '\n'
#     '{" ".join(str(s) for s in dataStatus["oldBanned"])} \n'
# )
# msg['From'] = botName
# msg['To'] = username
# msg['Subject'] = "Stock Decline"

##### decline - condition1
msgDecline = email.message_from_string(
    'stock-bot is reported a stock decline in the following stocks \n'
    '\n'
    f'{" ".join(str(s) for s in newBanned)} \n'
)
msgDecline['From'] = botName
msgDecline['To'] = username
msgDecline['Subject'] = "Stock Decline"

##### dividend payout - condition2
msgDividendPay = email.message_from_string(
    'stock-bot is reporting a dividend payout in the following stocks \n'
    '\n'
    f'{" ".join(str(s) for s in newDividend)} \n'
)
msgDividendPay['From'] = botName
msgDividendPay['To'] = username
msgDividendPay['Subject'] = "Dividend payout"






"""Starting the Magic!!"""
if __name__ == '__main__':
    main()



# for row in range(companiesMain.shape[0]):      # for each portfolio
#     for column in range(companiesMain.shape[1]):  # for each stock
#         if not pd.isnull(companiesMain.iloc[row,column]):  # if not null, continue
#             tmpStock = str(companiesMain.iloc[row,column])
#             print(f"{tmpStock}")
