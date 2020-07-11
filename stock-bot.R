#!/usr/bin/env Rscript
### Author:
## SNTag (SNTagore@protonmail.com)
### Description:
## Redoing my stock bot in R. R has become my main
## language, and I envision a cleaner approach to data analysis with
## it.
##
## This program will process stock-data, but differently from before.

## systems check
if (!file.exists("./config")) {
    reticulate::py_run_file("config-editor.py")
} else {
    usr.config <- yaml::read_yaml("./config")
}
if (!file.exists("./stock.csv")) {
    cat("need the stock csv \nread the docs \n")
} else {
    stock.csv <- readr::read_csv("./stock.csv")
}

pacman::p_load(tidyverse,
               reticulate,
               alphavantager)
