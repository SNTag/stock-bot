#!/usr/bin/env python3
### Author:
## SNTag (SNTagore@protonmail.com)
### Description:
## This script handles setup of a configuration file. API source,
## keys, and notifier approached is established here.
##
## generated config follows yaml.

import sys
import pickle
import os

def edit_config():
    print("feature in development. \n manual editing required.")


def make_config():
    # prompts for your configs
    api = "alphavantage"
    api_key = str(input("enter the alpha vantage key here: "))
    # notifier_system = str(input("enter the notifier system type here: "))
    # print("which notifier system will you use? \n note: the system you choose can be modified by editing the script 'notif.sh' \n -ifttt \n -email")
    notifier_key = str(input("enter the ifttt key here: "))

    # generates a config file
    f = open( 'config', 'w' )
    f.write( 'api = ' + repr(api) + '\n' )
    f.write( 'api_key = ' + repr(api_key) + '\n' )
    f.write( 'notifier_key = ' + repr(notifier_key) + '\n' )
    f.close()



if os.path.isfile("./config"):
    edit_config()
else:
    make_config()
