#!/usr/bin/env Rscript

alerts <- new.env()

alerts$condition1 <-
    function(x) {
        x <- periodReturns(x)
        if (x[1,1] > 0.05) {return("increasing greatly")}
    }

alerts$condition2 <-
    function(x) {
        x <- periodReturns(x)
        if (x[1,1] < -0.05) {return("decreasing greatly")}
        return("failed")
    }
