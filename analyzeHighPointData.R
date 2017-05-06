setwd("~/Dropbox/Ranking_Research_with_Braxton/CODE/finalRankingCode")
library(ggplot2)
highPointData = read.csv("highpointAnalysisData.csv", header = TRUE)
colnames(highPointData) <- c("cat", "problem", "stat", "value")

percentOfTopsInfo <- highPointData[highPointData$stat == "topsPercent",]

percentOfTopsInfoQualis <- percentOfTopsInfo[substr(x = percentOfTopsInfo$cat, start = 4, stop = 4)=="q", ]
p <- ggplot(percentOfTopsInfoQualis, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("percentage of tops") +
  ggtitle("percentage of tops for each problem for each category in qualis") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)

percentOfTopsInfoSemis <- percentOfTopsInfo[substr(x = percentOfTopsInfo$cat, start = 4, stop = 4)=="s", ]
p <- ggplot(percentOfTopsInfoSemis, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("percentage of tops") +
  ggtitle("percentage of tops for each problem for each category in semis") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)

percentOfTopsInfoFinals <- percentOfTopsInfo[substr(x = percentOfTopsInfo$cat, start = 4, stop = 4)=="f", ]
p <- ggplot(percentOfTopsInfoFinals, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("percentage of tops") +
  ggtitle("percentage of tops for each problem for each category in finals") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)


meanHighPoint <- highPointData[highPointData$stat == "mean",]

meanHighPointQualis <- meanHighPoint[substr(x = meanHighPoint$cat, start = 4, stop = 4)=="q", ]
p <- ggplot(meanHighPointQualis, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("mean high point") +
  ggtitle("mean high point for each problem for each category in qualis") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)

meanHighPointSemis <- meanHighPoint[substr(x = meanHighPoint$cat, start = 4, stop = 4)=="s", ]
p <- ggplot(meanHighPointSemis, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("mean high point") +
  ggtitle("mean high point for each problem for each category in semis") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)

meanHighPointFinals <- meanHighPoint[substr(x = meanHighPoint$cat, start = 4, stop = 4)=="f", ]
p <- ggplot(meanHighPointFinals, aes(x = cat, y = value, colour = factor(problem)))+ 
  geom_point() + xlab("category") + ylab("mean high point") +
  ggtitle("mean high point for each problem for each category in finals") +
  guides(fill=guide_legend(title="CATEGORIES")) +
  theme(legend.title = element_blank())
print(p)