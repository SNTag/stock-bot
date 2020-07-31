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
    saveRDS(banned.list, "./input/banned-list.rds")
}


### Data collection
# deprecated! I'm just remaking quantmode packages.
## #' collects the data from alphavantage, using R
## #' quantmode::getSymbols. Will place data in enviroment 'data' by
## #' default.
## #'
## #' @param tckr takes a vector of tickers to pull from alpha vantage.
## #' @return data
## data_collection <- function(tckr, usr.envir = ".GlobalEnv") {
##     alphavantager::av_api_key(config$api_key)

##     for (i in tickers) {
##         quantmod::getSymbols(i, src = 'av', api.key = config$api_key, env = usr.envir)
##         print(i)
##     }
## }


### notifications

#' will run the notifications.sh script
#' @param msg what message to say in the notification.
notify_me <- function(msg) {
    system(paste("./notify.sh", msg, config$notifier_key, config$approach, sep = " "))
}


### Alerts

#' Will read the file "./alerts.yaml". Alert conditions are decided for each stock. notifications will be sent out if appropiate
setting_alerts <- function() {
    x <- (ls(alerts) %>% length)
    p <- c()
    for (i in 1:x) {
        p <- c(p, paste("condition", i, sep = ""))
    }

    return(p)
}


#' Will read the file "./alerts.yaml". Alert conditions are decided for each stock. notifications will be sent out if appropiate
checking_alerts <- function(x, stck, conditions = conditions) {
    tmpVar <- c()
    for (i in 1:length(conditions)) {
        tmpVar <- c(tmpVar, as.character(get(conditions[i], env = alerts)(x)))
                                        #eval(parse(text = i))
        print(stck)
        print(tmpVar)
        names(tmpVar)[i] <- stck %>% as.character
    }
}
