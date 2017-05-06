library(reshape2)
library(ggplot2)
setwd("~/Dropbox/Ranking_Research_with_Braxton/CODE/finalRankingCode")
currentData <- read.csv("highpointAnalysisData.csv", header = TRUE)
qualisMaxPoints <- read.csv("qualisMaxPoints.csv", header = TRUE)
semisMaxPoints <- read.csv("semisMaxPoints.csv", header = TRUE)
finalsMaxPoints <- read.csv("finalsMaxPoints.csv", header = TRUE)
qualisFiles = c("fyaBNatsQualis2016.csv", "fybBNatsQualis2016.csv", "fycBNatsQualis2016.csv",
                "fydBNatsQualis2016.csv", "myaBNatsQualis2016.csv", "mybBNatsQualis2016.csv",
                "mycBNatsQualis2016.csv", "mydBNatsQualis2016.csv")
semisFiles = c("fyaBNatsSemis2016.csv", "fybBNatsSemis2016.csv", "fycBNatsSemis2016.csv",
  "fydBNatsSemis2016.csv", "myaBNatsSemis2016.csv", "mybBNatsSemis2016.csv",
  "mycBNatsSemis2016.csv", "mydBNatsSemis2016.csv")
finalsFiles = c("fyaBNatsFinals2016.csv", "fybBNatsFinals2016.csv", "fycBNatsFinals2016.csv",
                "fydBNatsFinals2016.csv", "myaBNatsFinals2016.csv", "mybBNatsFinals2016.csv",
                "mycBNatsFinals2016.csv", "mydBNatsFinals2016.csv")
setwd("~/Dropbox/Ranking_Research_with_Braxton/CODE/finalRankingCode/csvFiles")
maxPoints = finalsMaxPoints #for ease of naming - only change one thing when switching rounds
files = finalsFiles #for ease of naming - only change one thing when switiching rounds
round = 3 #1 = qualis, 2 = semis, 3 = finals
for(index in c(1:length(files))){
  datafile = files[[index]]
  totalData <- read.csv(datafile, header = TRUE)
  if(round == 1){
    dataSetName = paste(substr(x = datafile, start = 1, stop = 3),"q", sep="")
  }
  else if(round == 2){
    dataSetName = paste(substr(x = datafile, start = 1, stop = 3),"s", sep="")
  }
  else if(round == 3){
    dataSetName = paste(substr(x = datafile, start = 1, stop = 3),"f", sep="")
  }
  else{
    print("error - round must be 1, 2, or 3")
  }
  #head(totalData)
  
  #analyze highpoint distribution
  p1MaxPoints =  maxPoints[index, 2] #max points for first problem
  p2MaxPoints = maxPoints[index, 3] #max points for second problem
  p3MaxPoints = maxPoints[index, 4] #max points for third problem
  
  if(round == 1){ #there are 4 problems (otherwise there are only 3)
    p4MaxPoints = maxPoints[index, 5] #max points for fourth problem
    highPointsData = subset(totalData, select = c(3,7,11,15))
    #normalize highPointsData
    highPointsData[,1] = highPointsData[,1]/p1MaxPoints
    highPointsData[,2] = highPointsData[,2]/p2MaxPoints
    highPointsData[,3] = highPointsData[,3]/p3MaxPoints
    highPointsData[,4] = highPointsData[,4]/p4MaxPoints
  }
  else{
    highPointsData = subset(totalData, select = c(3,7,11))
    #normalize highPointsData
    highPointsData[,1] = highPointsData[,1]/p1MaxPoints
    highPointsData[,2] = highPointsData[,2]/p2MaxPoints
    highPointsData[,3] = highPointsData[,3]/p3MaxPoints
  }
  
  #allHighPoints = melt(highPointsData, measure.vars = 1:4)
  
  # plot(ggplot(data=highPointsData, aes(highPointsData[,1])) + 
  #   geom_histogram(binwidth=.1))
  # plot(ggplot(data=highPointsData, aes(highPointsData[,2])) + 
  #   geom_histogram(binwidth=.1))
  # plot(ggplot(data=highPointsData, aes(highPointsData[,3])) + 
  #   geom_histogram(binwidth=.1))
  # plot(ggplot(data=highPointsData, aes(highPointsData[,4])) + 
  #   geom_histogram(binwidth=.1))
  # plot(ggplot(data=allHighPoints, aes(allHighPoints$value)) + 
  #   geom_histogram(binwidth=.1))
  
  #calculate data about highpoints for each problem and append to currentData
  newDataMatrix <- matrix(ncol=4, nrow=length(highPointsData[1,])*4) 
  for(problem in c(1:length(highPointsData[1,]))){
    #set up columns 1-3 (doesn't depend on knowing tops data)
    newDataMatrix[(problem-1)*4+1, 1] = dataSetName
    newDataMatrix[(problem-1)*4+1, 2] = problem
    newDataMatrix[(problem-1)*4+1, 3] = "mean"
    
    newDataMatrix[(problem-1)*4+2, 1] = dataSetName
    newDataMatrix[(problem-1)*4+2, 2] = problem
    newDataMatrix[(problem-1)*4+2, 3] = "median"
    
    newDataMatrix[(problem-1)*4+3, 1] = dataSetName
    newDataMatrix[(problem-1)*4+3, 2] = problem
    newDataMatrix[(problem-1)*4+3, 3] = "std"
    
    newDataMatrix[(problem-1)*4+4, 1] = dataSetName
    newDataMatrix[(problem-1)*4+4, 2] = problem
    newDataMatrix[(problem-1)*4+4, 3] = "topsPercent"
    
    if(is.na(maxPoints[index,problem+1])){
      newDataMatrix[(problem-1)*4+4, 4] = 0 #no one topped the problem so tops percentage is 0
      print("none")
    }
    else{
      mean = mean(highPointsData[,problem])
      newDataMatrix[(problem-1)*4+1, 4] = mean
      
      median = median(highPointsData[,problem])
      newDataMatrix[(problem-1)*4+2, 4] = median
      
      std = sd(highPointsData[,problem])
      newDataMatrix[(problem-1)*4+3, 4] = std
      
      tops = highPointsData[,problem]==1
      topsPercentage = sum(tops)/length(tops)
      newDataMatrix[(problem-1)*4+4, 4] = topsPercentage
    }
  }
  
  newData <- data.frame(newDataMatrix)
  currentData <- rbind(currentData, newDataMatrix)
}

#write currentData to csv file
setwd("~/Dropbox/Ranking_Research_with_Braxton/CODE/finalRankingCode")
write.table(currentData, file="highpointAnalysisData.csv", sep=",")

#get the max points for each climb and put them somewhere useful
#get these numbers for qualis semis and finals
#calculate these stats for self-produced data too and work on making them match
