#!/usr/bin/env Rscript

# File: setup stock-bot
# Author: SNTagore (agenttiny@gmail.com)
# Date: Monday, February  3, 2020
# Description: Used to setup the stock bot.py
# Usage:
# in the terminal, go to the directory bot.py is in.  Type 'bash setup.sh'.#setup.sh.

pacman::p_load_gh("bnosac/cronR")

cmd <- cron_rscript(getwd())
cron_add(command = cmd, frequency = 'daily', at = "11:00" , id = 'stock_bot', description = "stock_bot")
