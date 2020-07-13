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
if (!file.exists("./config.yaml")) {
    reticulate::py_run_file("config-editor.py")
} else {
    config <- yaml::read_yaml("./config.yaml")
}
## stocks
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
## alerts
## if (file.exists("./alerts.yaml")) {
##     alerts <- yaml::read_yaml("./alerts.yaml")
## } else {
##     print("working without any alerts or notifications")
## }
if (file.exists("./alerts.R")) {
    source("./alerts.R")
} else {
    print("working without any alerts or notifications")
}


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
alphavantager::av_api_key(config$api_key)
data <- new.env()
if (length(tickers) > 5) {
    for (i in tickers) {
    quantmod::getSymbols(i, src = 'av', api.key = config$api_key, env = data)
    print(i)
    }
} else {
    for (i in tickers) {
        Sys.sleep(12.5)
        quantmod::getSymbols(i, src = 'av', api.key = config$api_key, env = data)
        print(i)
    }
}
#write.csv(daily.stck, file = "./data.csv")
#saveRDS("data", "data.rds")
#save.image(file = "data.RData", env = "data")

### assessing conditions
## for (i in alerts) {
##     if (eval(parse(text = i)) == TRUE) notify_me()
## }
#tmpDaily1 <- xts::xts(tmpDaily[,-1], order.by = tmpDaily$timestamp)

#tmpVar <- periodReturn(daily.stck, period = 'daily', subset = NULL, type = 'arithmetic', leading = TRUE)

#tmpDat <- daily.stck %>% tbl2xts::tbl_xts(., cols_to_xts = daily.stck)

conditions <- setting_alerts()
stck.msgs <- c()
for (i in tickers) {
    tmpDat <- get(i, env = data) %>% quantmod::dailyReturn()
    if (tmpDat[1,1] < -0.04) {
        notify_me(msg = paste(i, "_is_decreasing", sep = ""))
        print(paste0("weird", i))
    }
                                        #        stck.msgs <- c(stck.msgs, checking_alerts(tmpDat, stck = i, conditions = conditions))

    if (tmpDat[1,1] > 0.04) {
        notify_me(msg = paste(i, "_is_increasing", sep = ""))
        print(paste0("weird", i))
    }
}

### sending out alerts
## for (i in 1:length(stck.msgs)) {
##     print(stck.msgs[i])
##     tmpVar1 <- stck.msgs[i]
##     print(names(stck.msgs)[i])
##     tmpVar2 <- names(stck.msgs)[i]
##     tmpVar3 <- paste("stck: ", tmpVar1, ". issue: ", tmpVar2, sep = "")
##     notify_me()
## }

### saving banned list
save_banned()