#!/usr/bin/env Rscript
### Author:
## SNTag (SNTagore@protonmail.com)
### Description:
## Redoing my stock bot in R. R has become my main
## language, and I envision a cleaner approach to data analysis with
## it.
##
## This program will process stock-data, but differently from before.

### systems check
## config
if (!file.exists("./config")) {
    reticulate::py_run_file("config-editor.py")
} else {
    config <- yaml::read_yaml("./config.yaml")
}
## stocks
print("incomplete")                                         # INCOMPLETE
if (!file.exists("./stock.csv")) {
    cat("need the stock csv \nread the docs \n")
} else {
    stock.csv <- readr::read_csv("./stock.csv")
    tickers <- dplyr::pull(stock.csv, 1)
}
## banned list
if (file.exists("./banned-list.rds")) {
    banned.list <- readRDS("banned-list.rds")
} else {
    banned.list <- c()
}
## functions
source("./functions.R")


### loading packages
pacman::p_load(tidyverse,                   # data processing
               reticulate,                  # running python scripts
               alphavantager,               # data collection
               tidyquant                    # data collection
               )


### running the program
## manage the banned
banned.list <- reviewing_banned()
## sort stocks of interest from the banned
tickers <- sorting_stocks()


### data collection
daily.stck <- data_collection(tickers)
write.csv(daily.stck, file = "./data.csv")


### Final details to deal with
## save banned list
save_banned()
