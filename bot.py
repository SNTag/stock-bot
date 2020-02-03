#!/usr/bin/env python3
# File: stock-bot
# Author: SNTag (SNTagore@protonmail.com)
# Date: 25/01/2020
# Description:
# Usage:
# Version: 0.0.7

# TODOLIST
# - [C] Add option to analyze similar companies relative to the stock of Interest.
# - [A] check at specific time (instead of just every x hours), so as to minimize read/write to SD card and limit data inaccuracy.  NOTE: do this through crontab
# - [B] Add R graph processing instead of matplotlib
# - [B] Add on-the-fly updating of conditions of interest (PROBABLY REQUIRES MAJOR REORGANIZATION)
# - [C] Improve processing capabilities on current stock situations (such as through bta-lib)
# - [A] Add 'progress' saving (lists saved to text files for example)
# - [A] Improve internal data to hopefully limit wasted read/write (don't overwrite data, meta-data every time)
# NOTE: TODEL are items that will probably be removed when a novel time record system is added.


import email                    # for emailing
import smtplib                  # For emailing
from alpha_vantage.timeseries import TimeSeries  # For Data Collection
import matplotlib               # loaded to set matplotlib backend
import matplotlib.pyplot as plt # FOR FUN: Generates plots
import pandas as pd             # Used to config stocks
import time                     # Time tracking
import schedule                 # TODEL: will be deprecated later
import datetime as dt           # Used to maintain banned list
import os                       # For file/plot
import configparser             # For soft-coding bot-config
import subprocess               # For some quick quality checking
import json                     # For reading/saving to json
import sys                      # needed
from threading import Timer, Event  # TODEL: will be deprecated later
from dateutil.tz import gettz   # TODEL: will be deprecated later






"""For setting the Bot-configs"""
config = configparser.ConfigParser()
config.read("/etc/bot-login.cnf")
username = config.get('bot-email', 'username')  # address the bot will talk with
botName = config.get('bot-email', 'botName')    # bot email address
botPass = config.get('bot-email', 'botPass')    # bot email password
smtpAddress = config.get('bot-email', 'smtpAddress')    # bot email SMTP address
smtpPort = config.get('bot-email', 'smtpPort')    # bot email SMTP port
filestamp = time.strftime('%Y-%m-%d')
apiKey = config.get('AV', 'apiKey')    # Alpha Vantage API key


"""Background details"""
matplotlib.use('AGG')           # Used to set matplotlib backend
mainTimer = 11*60*60              # TODEL# as using adjusted daily, just need to check twice everyday.  Counted in seconds
tmpBanned = {}                    # holds for long term banning
newBanned = []                    # stocks that are just discovered to be bannable
repeatCounter = 0                 # minor quality check
newDividend = []                  # stocks that are paying a dividend today

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

if os.path.isdir("./output") == False:
    os.makedirs("./output")
if os.path.isdir("./data") == False:
    os.makedirs("./data")


"""Sets the time variables"""
##### needs to be the same as in data_processor()
dateToday = dt.date.today()
dateTodayNYC = dt.date.today() - dt.timedelta(hours=8)
dateYesterdayNYC = dt.date.today() - dt.timedelta(hours=24)
dateTwoWeeks = dateToday+dt.timedelta(14)






def main():
    """Will start the application every x seconds"""
    ##### Adding a short section for basic quality control checking (simple way of counting # of runs)
    global repeatCounter
    repeatCounter += 1
    subprocess.call(f"echo '{repeatCounter}' > $HOME/file.txt", shell=True)
    Timer(mainTimer, data_processor).start()  # TODEL#Will start dataprocessing (replacing with Sched and UTC -5 (NYC) detection)


def data_processor():
    """Will generate, process, and save csv files.  It will also determine if conditions have been triggered."""
    ##### Loads companies of interest
    global tmpBanned
    companiesMain = pd.read_csv("./company-list.csv", sep = ",", header = None, index_col = 0)  # set to reload when data_processor is called, so that new items can be added without resetting the program
    newBanned = []

    ##### Resets the time variables
    dateToday = dt.date.today()
    dateTodayNYC = dt.date.today() - dt.timedelta(hours=8)
    dateYesterdayNYC = dt.date.today() - dt.timedelta(hours=24)
    dateTwoWeeks = dateToday+dt.timedelta(14)


    ##### pulls stock data and checks for conditions
    for row in range(companiesMain.shape[0]):      # for each portfolio
        for column in range(companiesMain.shape[1]):  # for each stock
            print(f"analyzing {tmpStock}")
            tmpStock = str(companiesMain.iloc[row,column])

            for y in range(len(tmpBanned)):  # checks if it should unban stocks
                if tmpBanned[tmpStock] <= dateToday:
                    tmpBanned.pop(tmpStock, None)

            if tmpStock not in tmpBanned.keys():  # retrieves stock data
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
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'
                #     newBanned += tmpStock

                # if condition2 == False:
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'

                ##### plotting
                plotMaker(data, meta_data, tmpStock)

                ##### Save data (for further possible processing)


            time.sleep(12.5)                            # introduced to handle the limitations of AV calls per minute

    ##### Send email(s) if conditions were met
    if len(newDividend) > 0:
        email_sending(msgDividendPay, newBanned, username, botName, botPass)
    if len(newBanned) > 0:
        email_sending(msgDecline, username, botName, botPass)
    main()


def email_sending(msg, username, botName, botPass):
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
    plt.savefig(f'./output/{tmpStock}.png')
    plt.clf()
    plt.cla()
    plt.close()






"""Email templates here"""
##### General templates
# msg = email.message_from_string(
#     'stock-bot is reported a stock decline in the following stocks \n'
#     '\n'
#     '{" ".join(str(s) for s in tmpBanned)} \n'
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
