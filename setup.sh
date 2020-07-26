# File: setup stock-bot
# Author: SNTagore (agenttiny@gmail.com)
# Date: Monday, February  3, 2020
# Description: Used to setup the stock bot.py
# Usage:
# in the terminal, go to the directory bot.py is in.  Type 'bash setup.sh'.#setup.sh.

script_name1="stock-bot.sh"
script_path1=$(dirname $(readlink -f $0))
script_path_with_name="$script_path1/$script_name1"
echo $script_path_with_name
crontab -l | grep -q "${script_path_with_name}"  && echo 'entry exists' || (crontab -l 2>/dev/null; echo "0 11 * * * ${script_path_with_name}") | crontab -
