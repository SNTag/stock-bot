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
    echo "which notification system should I use?"
    echo "- 'IFTTT'"
    echo "- 'slack'"
    approach = str(input("choose one of the above (HAS TO BE EXACT): "))

    if [ approach == 'ifttt' ]; then
        notifier_key = str(input("enter the notifier key here: "))
    elif [ approach == 'slack' ]; then
        echo "set up a slack webhook as needed. you should get a line as such:"
        echo 'https://hooks.slack.com/services/${slack_key}'
        echo "where slack_key looks like"
        echo "afdjwe/asdfjhwe/djsfaklgrewuig"
        notifier_key = str(input("enter what goes into slack_key: "))
    else
        echo "not sure how to send the notifications"
    fi
    banned_length = str(input("how long do i keep tickers banned (in days): "))

    # generates a config file
    f = open( './input/config.yaml', 'w')
    f.write( 'api: ' + repr(api) + '\n' )
    f.write( 'api_key: ' + repr(api_key) + '\n' )
    f.write( 'banned_length: ' + repr(banned_length) + '\n' )
    f.write( 'approach: ' + repr(approach) + '\n' )
    f.write( 'notifier_key: ' + repr(notifier_key) + '\n' )
    f.close()



if os.path.isfile("./input/config.yaml"):
    edit_config()
else:
    make_config()
