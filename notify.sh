#!/bin/bash

arg1=$(echo $1 | sed 's/ /%20/g')
arg2=$(echo $2 | sed 's/ /%20/g')

curl -s -o /dev/null "https://maker.ifttt.com/trigger/notify/with/key/${arg2}?value1=$arg1"
