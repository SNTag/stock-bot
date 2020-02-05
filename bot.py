#!/usr/bin/env python3
# File: stock-bot
# Author: SNTag (SNTagore@protonmail.com)
# Date: 25/01/2020
# Description:
# Usage:
# Version: 0.0.8


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


"""Background details"""
matplotlib.use('AGG')           # Used to set matplotlib backend
newBanned = []                  # stocks that are just discovered to be ban-nable
newDividend = []                # stocks that are paying a dividend today

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

if os.path.isdir("./output") == False:
    os.makedirs("./output")
    if os.path.isdir("./output/graph") == False:
        os.makedirs("./output/graph")
    if os.path.isdir("./output/data") == False:
        os.makedirs("./output/data")
if os.path.isdir("./input") == False:
    os.makedirs("./input")


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
dateTodayNYC = dt.date.today() - dt.timedelta(hours=8)
dateYesterdayNYC = dt.date.today() - dt.timedelta(hours=24)
dateTwoWeeks = dateToday+dt.timedelta(14)








def main():
    """Will generate, process, and save csv files.  It will also determine if conditions have been triggered."""
    ##### Adding a short section for basic quality control checking (simple way of counting # of runs)
    global dataStatus
    dataStatus["repeatCounter"] += 1

    ##### Loads companies of interest
    companiesMain = pd.read_csv("./input/company-list.csv", sep = ",", header = None, index_col = 0)  # set to reload when data_processor is called, so that new items can be added without resetting the program
    newBanned = []

    ##### pulls stock data and checks for conditions
    for row in range(companiesMain.shape[0]):      # for each portfolio
        for column in range(companiesMain.shape[1]):  # for each stock
            tmpStock = str(companiesMain.iloc[row,column])
            print(f"analyzing {tmpStock}")

            for y in range(len(dataStatus["oldBanned"])):  # checks if it should unban stocks
                dateTmp = datetime.strptime(dataStatus["oldBanned"][tmpStock], '%Y-%m-%d').date()  # converts banned-date to datetime object for comparisons
                if dateTmp < dateTwoWeeks:
                    dataStatus["oldBanned"].pop(tmpStock, None)

            if tmpStock not in dataStatus["oldBanned"].keys():  # retrieves stock data
                # NOT banned (yet)
                # If conditon(s) failed, will trigger email and be added to banned list
                ts = TimeSeries(key=apiKey, output_format='pandas')
                data, meta_data = ts.get_daily_adjusted(symbol=tmpStock, outputsize='full')  # using adjusted to determine dividend yields

                ##### CONDITION1: determining if dividend was sent today
                if (data["7. dividend amount"][0] > 0) and (dateToday > dateTodayNYC):
                    newDividend.append(tmpStock)

                # condition1 = (data["4. adjusted close"][dateTodayNYC])/(data["4. adjusted close"][dateYesterdayNYC])
                # ##### CONDITION2: Determine if there was a stock decline
                # if (((1-condition1)*100) >= 10) or (((1-condition1)*100) <= 10):
                #     dataStatus["oldBanned"][tmpStock] = f'{dateTwoWeeks}'
                #     newBanned += tmpStock

                # if condition2 == False:
                #     dataStatus["oldBanned"][tmpStock] = f'{dateTwoWeeks}'

                ##### Save data as CSV for processing as desired
                data.to_csv(f"./output/data/{tmpStock}-{dateToday}.csv", index = True, )

                ##### plotting
                plotMaker(data, meta_data, tmpStock)

            time.sleep(12.5)                            # makes script compatible with AV calls per minute limit

    ##### Send email(s) if conditions were met
    if len(newDividend) > 0:
        email_sending(msgDividendPay, newBanned, username, botName, botPass)
    if len(newBanned) > 0:
        email_sending(msgDecline, username, botName, botPass)

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
    plt.savefig(f'./output/graphs/{tmpStock}.png')
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
