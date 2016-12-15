data = read.csv('crossValidation.csv', header = TRUE)
out<-with(data, friedman(judge,trt, evaluation,alpha=0.05, group=FALSE,console=TRUE))

mymethods <- labels(out[[3]])[[1]] #list of all methods in alphabetical order
df <- data.frame(matrix(unlist(out[4]), nrow=length(mymethods)*(length(mymethods)-1)/2, byrow=F), stringsAsFactors=FALSE)
labelsM <- labels(out[[4]])[[1]] #method test labels (which two methods were tested)
labelsI <- labels(out[[4]])[[2]] #friedman information labels
colnames(df) <- labelsI
rownames(df) <- labelsM

sig <- df["sig."] #significance (stars) of each difference in nemenyi test
pvals <- df["pvalue"] #p value of each difference in nemenyi test
signs <- df["Difference"] #actual difference in nemenyi test

count <- length(mymethods)-1 #how many new entries will be in this row of the matrix (not counting NA)
start <- 1 #index in lists of results
row <- 1 #current row
colStart <- 2 #column to start at
matrix <- matrix(ncol=length(mymethods), nrow=length(mymethods)) #matrix where all data will go
while(count>0){ #while there is more data to add to table
  col <- colStart #increments through all columns in row
  for(s in start:(start+count-1)){ #index in list of results
    if(pvals[[1]][[s]]<.001 && signs[[1]][[s]]<0){ #very significant negative difference
      matrix[row,col] = -3
      matrix[col,row] = 3
    }
    else if(pvals[[1]][[s]]<.001 && signs[[1]][[s]]>0){ #very significant positive difference
      matrix[row,col] = 3
      matrix[col,row] = -3
    }
    else if(pvals[[1]][[s]]<.01 && signs[[1]][[s]]<0){ #pretty significant negative difference
      matrix[row,col] = -2
      matrix[col,row] = 2
    }
    else if(pvals[[1]][[s]]<.01 && signs[[1]][[s]]>0){ #pretty significant positive difference
      matrix[row,col] = 2
      matrix[col,row] = -2
    }
    else if(pvals[[1]][[s]]<.05 && signs[[1]][[s]]<0){ #significant negative difference
      matrix[row,col] = -1
      matrix[col,row] = 1
    }
    else if(pvals[[1]][[s]]<.05 && signs[[1]][[s]]>0){ #significant positive difference
      matrix[row,col] = 1
      matrix[col,row] = -1
    }
    else{ #difference is not significant
      matrix[row,col] = 0
      matrix[col,row] = 0
    }
    col <- col + 1 #increment column in matrix where data goes
  }
  start = start + count
  count = count - 1
  colStart = colStart + 1
  row = row + 1
}

tableData <- data.frame(matrix)
colnames(tableData) <- mymethods
rownames(tableData) <- mymethods
#print(tableData)

write.table(tableData, file = "rdata.csv", sep = ",")
