#!/bin/bash

if [ $3 == 'ifttt' ]; then
    arg1=$(echo $1 | sed 's/ /%20/g')
    arg2=$(echo $2 | sed 's/ /%20/g')
    curl -s -o /dev/null "https://maker.ifttt.com/trigger/notify/with/key/${arg2}?value1=$arg1"
elif [ $3 == 'slack' ]; then
    curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}' https://hooks.slack.com/services/${notifier_key}
else
    echo "not sure how to send the notifications"
fi
