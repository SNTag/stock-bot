#!/usr/bin/env Rscript
### Author:
## SNTag (SNTagore@protonmail.com)
### Description:
## Holds the functions that enable the stock-bot to work.

### everything to do with banned list
## TESTING PARAMETERS FOR FUNCTIONS BELOW
banned.list <- c("AAPL" = as.Date("2020-07-20",
                                  tryFormats = c("%Y-%m-%d")),
                 "MSFT" = as.Date("2020-07-20",
                                  tryFormats = c("%Y-%m-%d")),
                 "GOOG" = as.Date("2020-07-10",
                                  tryFormats = c("%Y-%m-%d")))

#' ensure all elements in the banned list belong there. Removes
#' elements if date-to-remove has passed.
#'
#' @return modified banned.list
reviewing_banned <- function() {
    for (i in 1:length(banned.list)) {
        if (isTRUE(Sys.Date() > banned.list[i])) {
            banned.list <- banned.list[-i]
        }
    }

    return(banned.list)
}

#' read the banned list and remove them from the stocks to consider.
#'
#' @return modified banned.list
sorting_stocks <- function() {
    for (k in 1:length(tickers)) {
        for (i in tickers) {
            if (i %in% names(banned.list)) {
                tickers <- tickers[-k]
            }
        }
    }

    return(tickers)
}

#' when a stock has crossed my restrictions, add it to the banned list
#'
#' @param tckr takes a  ticker and adds it to the banned list
#' @return modified banned.list
adding_banned <- function(tckr) {
    banned.list <- c(banned.list, tckr = Sys.Date()+config$banned_length)

    return(banned.list)
}

#' save banned list for future runs
save_banned <- function() {
    saveRDS(banned.list, "banned-list.rds")
}


### Data collection

#' collects the data from alphavantage
#'
#' @param tckr takes a vector of tickers to pull from alpha vantage.
#' @return data
data_collection <- function(tckr) {
    alphavantager::av_api_key(config$api_key)

    data.today <-
        tickers %>%
        tidyquant::tq_get(
                       get = "alphavantage",
                       av_fun = "TIME_SERIES_INTRADAY",
                       interval = "5min"
                   )
    return(data.today)
}


### notifications

#' will run the notifications.sh script
#' @param msg what message to say in the notification.
notify_me <- function(msg) {
    system(paste("./notify.sh", msg, config$notifier_key, sep = " "))
}


### Alerts

#' Will read the file "./alerts.yaml". Alert conditions are decided for each stock. notifications will be sent out if appropiate
