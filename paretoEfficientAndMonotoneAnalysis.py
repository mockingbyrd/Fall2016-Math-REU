import numpy as np
from RankingMethodsClass import ClimbingRanker
import RankingMethodsClass as rmc
import random
import copy
from itertools import combinations

def makeRank(list):
    """
    takes a general list and makes it into a rank (accounting for ties)
    :param list: list to be made into a rank
    :return: ranking made from the list
    """
    listCopy = list.copy() #so that the list doesnt change in getMinValueInList
    i = 1 #keeps track of what rank the current climber should get
    while(i<=len(list)):
        minIndices = getMinValueInList(listCopy)
        for index in minIndices:
            list[index] = i
        i = i+len(minIndices)

def getMinValueInList(list):
    """
    finds the minimum value in a list, sets that minimum value to 1000 so the next min value can be found
    :param list: list where minimum value is to be found
    :return: minimum value in the list
    """
    minIndices = [0]
    for index in range(1,len(list)):
        if(list[index]<list[minIndices[0]]):
            minIndices = [index]
        elif(list[index]==list[minIndices[0]]):
            minIndices.append(index)
    for index in minIndices:
        list[index] = 1000
    return minIndices


def produceMonotonicityResultSet(numClimbers, numProblems = 4):
    """
    Produces a set of results for use in monotonicity analysis
    :param numClimbers: number of climbers to use in the result
    :param numProblems: number of problems in the result set
    :return: result set (ranks matrix - rows = climbers, columns = problems)
    """
    ranks = np.zeros(shape=(numClimbers, numProblems)) #entry i,j is rank of ith climber on jth problem

    #fill up the ranks matrix with random ranks but allow the first climber to be able to move up in the ranks
    for col in range(0, numProblems):
        ranks[0][col] = random.randrange(2, numClimbers+1, 1) #generate random integer between 2 and numClimbers
    for problem in range(0, numProblems): #so that someone always beats the climber who's rank will improve
        ranks[problem+1][problem] = 1
    for row in range(0, numClimbers):
        for col in range(0, numProblems):
            if(ranks[row][col] == 0):
                ranks[row][col] = random.randrange(1, numClimbers+1, 1) #generate random integer between 1 and numClimbers

    #ensure that all these columns correspond to ranks
    list = [0]*numClimbers
    for col in range(0, numProblems):
        for row in range(0, numClimbers):
            list[row] = ranks[row][col]
        makeRank(list)
        for row in range(0, numClimbers):
            ranks[row][col] = list[row]
    return ranks

def produceMonotonicityResultSetTwo(ranks, numProblems, numClimbers, numProblemsChanged):
    """
    Generates a second result set where the placement of the first climber has increased
    :param ranks: numpy matrix of ranks where the rows correspond to the climbers and the columns correspond to the problems
    :return: the new matrix of ranks
    """
    ranksCopy = copy.deepcopy(ranks)
    list = [0]*numClimbers
    for col in range(0, numProblemsChanged):
        ranksCopy[0][col] = random.randrange(1, ranksCopy[0][col], 1)
        for row in range(0, numClimbers):
            list[row] = ranksCopy[row][col]
        makeRank(list)
        for row in range(0, numClimbers):
            ranksCopy[row][col] = list[row]
    return ranksCopy

def compareMonotoneResults(rank1, rank2):
    """
    Returns 0 if moving the climber up in the rank on one problem caused them to move down in the rankings overall
    :param rank1:
    :param rank2:
    :return:
    """
    if(rank1[0]-rank2[0]<0):
        return 0
    else:
        return 1

def calculateGeometricMedianSum(ranks, finalRank):
    """
    Calculates the value of the sum that is being minimized when using Weizsfeld's algorithm.
    :param ranks: ranks in the sum
    :param finalRank: final ranked list of climbers being ranked
    :return: the sum
    """
    numProblems = len(ranks[0])
    numClimbers = len(finalRank)

    sum = 0
    for column in range(0, numProblems):
        sumOfSquares = 0
        for climber in range(0, numClimbers):
            sumOfSquares += (ranks[climber][column]-finalRank[climber])**2
        sumOfSquares = sumOfSquares ** (1/2)
        sum += sumOfSquares
    return sum


def doMonotonicityAnalysis(numClimbers, numProblems, iterations, numProblemsChanged, methodNum):
    """
    Creates two profiles where one climber's performance has been improved on numProblemsChanged problems and then verifies
    that the climber has not fallen in ranking. Repeated the number of times specified and returns a "monotonicity score"
    :param numClimbers: number of climbers in the profiles to be created
    :param numProblems: number of problems in the profiles to be created
    :param iterations: number of iterations
    :param numProblemsChanged: number of problems where the climber's rank will be improved (first climber only)
    :param methodNum: number of the method we are testing
    :return: monotonicity score, or the percentage of the time the method was monotone
    """

    #make list of climber names
    climbers = [0] * numClimbers
    for i in range(0, numClimbers):
        climbers[i] = str(i)

    tops = [0] * numClimbers

    sum = 0

    for iteration in range(0, iterations):
        ranks1 = produceMonotonicityResultSet(numClimbers, numProblems)
        ranker1 = ClimbingRanker("", [climbers, numProblems, ranks1, tops])
        results1 = ranker1.runMethod(methodNum) #run specified method
        ranks2 = produceMonotonicityResultSetTwo(ranks1, numProblems, numClimbers, numProblemsChanged)
        ranker2 = ClimbingRanker("", [climbers, numProblems, ranks2, tops])
        results2 = ranker2.runMethod(methodNum) #run specified method
        sumAdd = compareMonotoneResults(results1, results2)
        if(sumAdd == 0):
            min1 = calculateGeometricMedianSum(ranks1, results1)
            min2 = calculateGeometricMedianSum(ranks2, results2)
            oneTo2 = calculateGeometricMedianSum(ranks1, results2)
            twoTo1 = calculateGeometricMedianSum(ranks2, results1)
            if(twoTo1>min2 and oneTo2>min1):
                print(iteration)
                print("ranks1: ", ranks1)
                print("results1: " ,results1)
                print("ranks2:", ranks2)
                print("results2: ", results2)
                print("min1: ", min1)
                print("min2: ", min2)
                print("oneTo2: ", oneTo2)
                print("twoTo1: ", twoTo1)
            else:
                print("inaccurate geometric median calculation")
        sum += sumAdd
    return sum/iterations


#random.seed(1)
#methods = [0,1,2,3,4,5,6,7,8,12,13,14,15,16]
#for methodNum in methods:
#    random.seed(1)
#    print(rmc.getMethod(methodNum))
#    print(doMonotonicityAnalysis(5, 4, 10000, 1, methodNum))

random.seed(2)
print(doMonotonicityAnalysis(5, 4, 10000, 1, 12))

#12 = walg integer
#13 = walg optimal integer

def bruteForceWalg(ties = True):
    ranksAndScores = []
    if(not ties):
