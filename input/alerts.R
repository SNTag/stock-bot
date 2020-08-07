#!/usr/bin/env Rscript

alerts <- new.env()

alerts$condition1 <-
    function(x, stck) {
        x <- quantmod::periodReturn(x)
        tmpList <- setNames("increasing_greatly", stck[1])
        if (x[1,1] > 0.05) {return(tmpList)}
    }

alerts$condition2 <-
    function(x, stck) {
        x <- quantmod::periodReturn(x)
        tmpList <- setNames("decreasing_greatly", stck[1])
        if (x[1,1] < -0.05) {return(tmpList)}
        return("failed")
    }
