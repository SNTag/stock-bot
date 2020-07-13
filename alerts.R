#!/usr/bin/env Rscript

alerts <- new.env()

alerts$condition1 <-
    function(x) {
        if (x[1,1] > 0) return("Success")
    }

alerts$condition2 <-
    function(x) {
        if (x[1,1] > 0) {print("NOOOOO")} else {print("YESSSS")}
        return("failed")
    }
