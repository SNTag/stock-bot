#!/usr/bin/env bash

# File: setup stock-bot
# Author: SNTagore (agenttiny@gmail.com)
# Date: Monday, February  3, 2020
# Description: Used to setup the stock bot.py
# Usage:
# in the terminal, go to the directory bot.py is in.  Type 'bash setup.sh'.#setup.sh.


#----------|self-referencing|----------#
# will find itself wherever the script is run from
# See https://stackoverflow.com/a/246128/3561275
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"


#----------|edit stock-bot to become self-referencing|----------#
sed 's,\#\#\# THIS LINE WILL BE REPLACED,setwd\('"$DIR"'\),' "$DIR/stock-bot.R"


#----------|where is Rscript?|----------#
tmpVar="$(which Rscript)"


#----------|adding to crontab|----------#
## https://www.golinuxcloud.com/get-script-name-get-script-path-shell-script/
script_path_with_name="${tmpVar} '${DIR}/stock-bot.R'  >> '/home/sntag/Documents/stock-bot/stock-bot.log' 2>&1"
echo $script_path_with_name

## https://stackoverflow.com/questions/14450866/search-for-a-cronjob-with-crontab-l/14451184#14451184
## https://stackoverflow.com/questions/4880290/how-do-i-create-a-crontab-through-a-script#9625233
crontab -l | grep -q "${script_path_with_name}"  && echo 'entry exists' || (crontab -l 2>/dev/null; echo "0 11 * * * ${script_path_with_name}") | crontab -
