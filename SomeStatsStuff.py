import GetTopsInfo as gti
from ReadInData import ClimbingDataFile
import numpy as np

def getAverageNumberOfHolds(youthCategory):
    """
    Calculates average number of holds on a climb for a given category in 2016 Youth Bouldering Nationals
    used to replace max number of holds on climb in ABS10 and merged methods when no climber topped the problem
    :param youthCategory: category
    :return: average number of holds
    """
    semisData = ClimbingDataFile(youthCategory + "BNatsSemis2016.csv", 0)
    qualisData = ClimbingDataFile(youthCategory + "BNatsQualis2016.csv", 0)
    finalsData = ClimbingDataFile(youthCategory + "BNatsFinals2016.csv", 0)
    tops = [finalsData.getTops(), semisData.getTops(), qualisData.getTops()]
    points = [finalsData.getPointsPerProblem(), semisData.getPointsPerProblem(), qualisData.getPointsPerProblem()]
    holdNumbers = []
    for i in range(0,len(tops)):
        try:
            topsPerProblem = gti.getTopsInfo(points[i], tops[i])
            for col in range(0, len(topsPerProblem[0])):
                for row in range(0, len(topsPerProblem)):
                    if(topsPerProblem[row][col] == 1):
                        holdNumbers.append(points[i][row][col])
                        break
        except ValueError: #couldn't determine tops data
            continue
    return np.std(holdNumbers), np.mean(holdNumbers)
