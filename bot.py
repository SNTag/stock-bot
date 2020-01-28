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
import matplotlib.pyplot as plt  # FOR FUN: Generates plots
import pandas as pd             # Used to config stocks
import sched, time              # Used similar to Cron scheduling
import datetime                 # Used to maintain banned list
import os                       # for file, plot maintenance
import configparser             # For soft-coding bot-config
# import yaml




"""Set the trigger conditions here"""
#condition1 =                    # LOOKS FOR DISCREPENCIES. will be dependent on the stocks average rate or growth
#condition2 =                    #


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
tmpTimer = 1*60*60          # time interval
mainTimer = sched.scheduler(time.time, time.sleep)
tmpBanned = {}
if os.path.isdir("./output") == False:
    os.makedirs("./output")


def main():
    """Will start the application every x seconds"""
    mainTimer.enter(tmpTimer, 1, data_processor, ())
    print("starting again")


def data_processor():
    """Will generate, process, and save csv files.  It will also determine if conditions have been triggered."""
    global tmpBanned
    companiesMain = pd.read_csv("./company-list.csv", sep = ",", header = None, index_col = 0)  # set to reload when data_processor is called, so that new items can be added without resetting the program
    dateToday = datetime.date.today()
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
                data, meta_data = ts.get_daily(symbol=tmpStock, outputsize='full')  # should I use adjusted?

                # if condition1 == False:
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'

                # if condition2 == False:
                #     tmpBanned[tmpStock] = f'{dateTwoWeeks}'

                data['4. close'].plot()
                plt.title(f'Daily Times Series for the {tmpStock} stock')
                plt.ylabel('Cost')
                plt.savefig(f'./output/{tmpStock}.png')
                plt.clf()
                plt.cla()
                plt.close()

    email_sending(tmpBanned)
    main()


def email_sending(tmpBanned):
    msg = email.message_from_string(
        'stock-bot is reported a stock decline in the following stocks \n'
        '\n'
        '{" ".join(str(s) for s in tmpBanned)} \n'
    )
    msg['From'] = botName
    msg['To'] = username
    msg['Subject'] = "Stock Decline"
    email_sending(msg)

    s = smtplib.SMTP(smtpAddress, smtpPort)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(botName, password)

    s.sendmail(botName, username, msg.as_string())

    s.quit()





"""Starting the Magic!!"""
if __name__ == '__main__':
    mainTimer.enter(tmpTimer, 1, data_processor, ())
    mainTimer.run()
