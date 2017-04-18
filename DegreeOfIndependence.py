import numpy as np
import random
from RankingMethodsClass import ClimbingRanker
import RankingMethodsClass as rmc
import csv
#need to produce list of climbers, numProblems, ranks, and tops for creating a ClimbingRanker object

#returned list has the rank of each climber at their index in the list (based on climbers list)

##steps in the process:
#1. produce a set of results. 4 problems, n climbers, 0 tops
#2. use the method on this set of results
#3. produce another set of results where the performance of two climbers remains the same
#4. use the method on this new set of results and verify that the relative rank of the two climbers remains the same

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


def produceResultSet(numClimbers, tops, numProblems = 4):
    """
    Produces a set of results for use in independence analysis
    :param numClimbers: number of climbers to use in the result
    :param tops: number of tops for each climber (vector of length numClimbers)
    :param numProblems: number of problems in the result set
    :return: result set (ranks matrix - rows = climbers, columns = problems)
    """
    ranks = np.zeros(shape=(numClimbers, numProblems)) #entry i,j is rank of ith climber on jth problem

    #fill up the ranks matrix with random ranks from 1 to numClimbers
    for row in range(0, numClimbers):
        for col in range(0, numProblems):
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

def produceResultSetTwo(ranks, tops, indexOne, indexTwo):
    """
    Produces a set of results where the performance of the climbers corresponding to indexOne and indexTwo remains the same
    :param ranks: matrix of ranks of each climber on each problem (rows = climbers)
    :param tops: vector of tops for each climber
    :param indexOne: index corresponding to the first climber whose performance can't change (indexOne<indexTwo)
    :param indexTwo: index corresponding to the second climber whose performance can't change
    :return: a new matrix of ranks to test independence
    """
    numClimbers = len(ranks)
    numProblems = len(ranks[0])

    currentRelativePositions = [0]*numProblems #vector of the current relative positions of the two climbers for each problem
    for index in range(0, len(currentRelativePositions)):
        currentRelativePositions[index] = ranks[indexOne][index] - ranks[indexTwo][index]

    #calculate a new ranks that preserves the performance of the two climbers on each problem (their relative ranks are the same)
    newRanks = np.zeros(shape=(numClimbers, numProblems))  # entry i,j is rank of ith climber on jth problem

    # fill up the ranks matrix with random ranks from 1 to numClimbers
    for row in range(0, numClimbers):
        if(row == indexOne):
            for col in range(0,numProblems):
                if(currentRelativePositions[col] < 0): #indexOne has lower (better) rank than indexTwo - can't be ranked last now
                    newRanks[row][col] = random.randrange(1, numClimbers, 1)  # generate random integer between 1 and numClimbers-1
                elif(currentRelativePositions[col] == 0): #indexOne and indexTwo tied
                    newRanks[row][col] = random.randrange(1, numClimbers+1, 1)  # generate random integer between 1 and numClimbers
                else: #indexOne has higher (worse) rank than indexTwo - can't be ranked first now
                    newRanks[row][col] = random.randrange(2, numClimbers+1, 1)  # generate random integer between 2 and numClimbers
        elif (row == indexTwo): #guaranteed to happen after row == indexOne
            for col in range(0, numProblems):
                if (currentRelativePositions[col] < 0):  # indexOne has lower (better) rank than indexTwo
                    # generate random integer below the rank of indexTwo
                    newRanks[row][col] = random.randrange(newRanks[indexOne][col]+1, numClimbers+1, 1)
                elif (currentRelativePositions[col] == 0):  # indexOne and indexTwo tied
                    newRanks[row][col] = newRanks[indexOne][col] #indexTwo must have the same rank
                else:  # indexOne has higher (worse) rank than indexTwo
                    # generate random integer above the rank of indexOne
                    newRanks[row][col] = random.randrange(1, newRanks[indexOne][col], 1)
        else:
            for col in range(0, numProblems):
                newRanks[row][col] = random.randrange(1, numClimbers+1, 1)  # generate random integer between 1 and numClimbers

    # ensure that all these columns correspond to ranks (yes this could be more efficient)
    list = [0] * numClimbers
    for col in range(0, numProblems):
        for row in range(0, numClimbers):
            list[row] = newRanks[row][col]
        makeRank(list)
        for row in range(0, numClimbers):
            newRanks[row][col] = list[row]

    #check that the relative positions of climbers corresponding to indexOne and indexTwo aren't changed
    for index in range(0, numProblems):
        if(np.sign(newRanks[indexOne][index] - newRanks[indexTwo][index]) != np.sign(currentRelativePositions[index])):
            print("ERROR: rank creation went poorly")
            print("new ranks: ", newRanks)
            print("old ranks: ", ranks)

    return newRanks


def compareResults(results1, results2, indexOne, indexTwo):
    """
    Compares to results and determines if the relative position of the climber corresponding to indexOne and the climber
    corresponding to indexTwo have changed
    :param results1: first list of results (produced from a ranking method in the ClimbingRanker class)
    :param results2: second list of results (produced from a ranking method in the ClimbingRanker class)
    :param indexOne: index corresponding to the first climber whose performance didn't change
    :param indexTwo: index corresponding to the second climber whose performance didn't change
    :return: 1 if the relative position didn't change (was independent in this case), 0 otherwise
    """
    if(np.sign(results1[indexOne] - results1[indexTwo]) == np.sign(results2[indexOne] - results2[indexTwo])):
        return 1
    else:
        return 0

def doIndependenceAnalysis(methodNum, iterations, numClimbers, tops, numProblems=4):
    """
    Runs an independence analysis on the given method.
    :param methodNum: method on which the independence tests will be run (can find number of your method in the RankingMethodsClass)
    :param iterations: number of times independence will be tested
    :param numClimbers: number of climbers in the ranks that will be tested
    :param tops: number of tops for each climber (list with tops for each climber)
    :param numProblems: number of problems in the ranks that will be tested (defaults to 4)
    :return: the percentage of times the method was independent
    """
    # make list of climbers
    climbers = [0] * numClimbers
    for i in range(0, numClimbers):
        climbers[i] = str(i)

    sum = 0
    for count in range(0, iterations):  # runs the number of times that iterations specifies (upper bound in range not hit):
        ranks = produceResultSet(numClimbers, tops, numProblems)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks, tops])
        results1 = ranker.runMethod(methodNum)  # run the specified method
        ranks2 = produceResultSetTwo(ranks, tops, 0, 1)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks2, tops])
        results2 = ranker.runMethod(methodNum)
        sum += compareResults(results1, results2, 0, 1)
    return sum/iterations

numberOfClimbers = 15
#print(doIndependenceAnalysis(8, 10, numberOfClimbers, [0]*numberOfClimbers))

listOfMethodNumsNoTops = [0, 3, 5, 6, 8] #, 15] #l2, geomean, usac, borda, borda with traditional ties, linprogsplit
methodNames = [0]*len(listOfMethodNumsNoTops)
methodIndependencePercent = [0]*len(listOfMethodNumsNoTops)
for index in range(0, len(listOfMethodNumsNoTops)):
    methodNum = listOfMethodNumsNoTops[index]
    methodNames[index] = rmc.getMethod(methodNum)
    print(methodNames[index])
    methodIndependencePercent[index] = doIndependenceAnalysis(methodNum, 10000, numberOfClimbers, [0]*numberOfClimbers)
    print(methodIndependencePercent[index])
with open('independencePercentagesFor10000IterationsAnd15Climbers.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['method', 'percentage of times independent'])
    for index in range(0, len(methodNames)):
        writer.writerow([methodNames[index], methodIndependencePercent[index]])