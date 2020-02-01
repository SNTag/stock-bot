#!/usr/bin/env python3
# File: stock-bot
# Author: SNTag (SNTagore@protonmail.com)
# Date: 25/01/2020
# Description:
# Usage:
# Version: 0.0.5

# TODOLIST
# - [C] Add network disconnection solutions
# - [C] error handling
# - [A] A way to stop reporting on a stock once it triggers a condition for two weeks

##### FOR BANNED LIST
# Need to figure out how to schedule events around a dict (key:value)


import email                                    # for emailing
import smtplib                                  # For emailing
from alpha_vantage.timeseries import TimeSeries  # For Data Collection
import matplotlib
import matplotlib.pyplot as plt  # FOR FUN: Generates plots
import pandas as pd             # Used to config stocks
import sched, time              # Used similar to Cron scheduling
import datetime                 # Used to maintain banned list
import os                       # for file, plot maintenance
import configparser             # For soft-coding bot-config
import subprocess
from threading import Timer, Event




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

matplotlib.use('AGG')



"""Background details"""
tmpTimer = 5*60              # as using adjusted daily, just need to check twice everyday.  Counted in seconds
mainTimer = sched.scheduler(time.time, time.sleep)
tmpBanned = {}
newBanned = []
repeatCounter = 0

##### Resets the time variables
dateToday = datetime.date.today()
dateTodayNYC = datetime.date.today() - datetime.timedelta(hours=8)
dateYesterdayNYC = datetime.date.today() - datetime.timedelta(hours=24)
dateTwoWeeks = dateToday+datetime.timedelta(14)

if os.path.isdir("./output") == False:
    os.makedirs("./output")


def main():
    """Will start the application every x seconds"""
    ##### Adding a short section for some quality control checking
    global repeatCounter
    repeatCounter += 1
    print("Starting again")
    subprocess.call(f"echo '{repeatCounter}' > $HOME/file.txt", shell=True)
    print("starting again2")
    Timer(5.0, data_processor).start()


def data_processor():
    """Will generate, process, and save csv files.  It will also determine if conditions have been triggered."""
    print("starting data processing")

    ##### Loads data
    global tmpBanned
    companiesMain = pd.read_csv("./company-list.csv", sep = ",", header = None, index_col = 0)  # set to reload when data_processor is called, so that new items can be added without resetting the program
    newBanned = []

    ##### Resets the time variables
    dateToday = datetime.date.today()
    dateTodayNYC = datetime.date.today() - datetime.timedelta(hours=8)
    dateYesterdayNYC = datetime.date.today() - datetime.timedelta(hours=24)
    dateTwoWeeks = dateToday+datetime.timedelta(14)

    for row in range(companiesMain.shape[0]):      # for each portfolio
        for column in range(companiesMain.shape[1]):  # for each stock
            tmpStock = str(companiesMain.iloc[row,column])

            # checks if it should unban stocks
            for y in range(len(tmpBanned)):
                if tmpBanned[tmpStock] <= dateToday:
                    tmpBanned.pop(tmpStock, None)

            # retrieves stock data
            if tmpStock not in tmpBanned.keys():
                # NOT banned (yet)
                # If conditon(s) failed, will trigger email and be added to banned list
                ts = TimeSeries(key=apiKey, output_format='pandas')
                data, meta_data = ts.get_daily_adjusted(symbol=tmpStock, outputsize='full')  # using adjusted to determine dividend yields

                ##### determining if dividend was sent today
                if (data["7. dividend amount"][0] > 0) and (dateToday > dateTodayNYC):
                    email_sending(msgDividendPay, newBanned, username, botName, botPass)

                # condition1 = (data["4. adjusted close"][dateTodayNYC])/(data["4. adjusted close"][dateYesterdayNYC])
                # ##### Determine if there was a stock decline
                # if (((1-condition1)*100) >= 10) or (((1-condition1)*100) <= 10):
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'
                #     newBanned += tmpStock

                # if condition2 == False:
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'

                ##### plotting
                plotMaker(data, meta_data, tmpStock)

    ##### Send email if there is a decline
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
    'stock-bot is reported a stock decline in the following stocks \n'
    '\n'
    '{" ".join(str(s) for s in tmpBanned)} \n'
)
msgDividendPay['From'] = botName
msgDividendPay['To'] = username
msgDividendPay['Subject'] = "Stock Decline"





"""Starting the Magic!!"""
if __name__ == '__main__':
    main()
