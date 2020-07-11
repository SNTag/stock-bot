#!/bin/bash

arg=$(echo $1 | sed 's/ /%20/g')
curl -s -o /dev/null "https://maker.ifttt.com/trigger/notify/with/key/<your-key>?value1=$arg"
