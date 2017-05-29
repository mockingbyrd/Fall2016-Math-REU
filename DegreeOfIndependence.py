import numpy as np
import random
from RankingMethodsClass import ClimbingRanker
import RankingMethodsClass as rmc
import csv
from itertools import combinations
from threading import Thread
from threading import Lock
from ResultsSetClass import ResultSet
import paretoEfficientAndMonotoneAnalysis as pema

##########################CREATES TWO RANDOM PROFILES WHERE THE RELATIVE RANKS OF TWO CLIMBERS STAY THE SAME, DETERMINES
##########################IF THE RELATIVE FINAL RANK FOR THE TWO CLIMBERS IS THE SAME
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
        results1, raw1 = ranker.runMethod(methodNum)  # run the specified method
        ranks2 = produceResultSetTwo(ranks, tops, 0, 1)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks2, tops])
        results2, raw2 = ranker.runMethod(methodNum)
        sumAdd = compareResults(results1, results2, 0, 1)
        if(sumAdd == 0):
            print("not independent")
            print("ranks1: ", ranks)
            print("raw1, results1: ", raw1, results1)
            print("ranks2: ", ranks2)
            print("raw2, results2: ", raw2, results2)
        sum += sumAdd
    return sum/iterations

numberOfClimbers = 5
print(doIndependenceAnalysis(12, 100, numberOfClimbers, [0]*numberOfClimbers)) #walg
#
# listOfMethodNumsNoTops = [0, 3, 5, 6, 8, 15] #l2, geomean, usac, borda, borda with traditional ties, linprogsplit
# methodNames = [0]*len(listOfMethodNumsNoTops)
# methodIndependencePercent = [0]*len(listOfMethodNumsNoTops)
# for index in range(0, len(listOfMethodNumsNoTops)):
#     methodNum = listOfMethodNumsNoTops[index]
#     methodNames[index] = rmc.getMethod(methodNum)
#     print(methodNames[index])
#     methodIndependencePercent[index] = doIndependenceAnalysis(methodNum, 1000, numberOfClimbers, [0]*numberOfClimbers)
#     print(methodIndependencePercent[index])
# with open('independencePercentagesFor10000IterationsAnd15Climbers.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['method', 'percentage of times independent'])
#     for index in range(0, len(methodNames)):
#         writer.writerow([methodNames[index], methodIndependencePercent[index]])


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
###################################SECOND METHOD OF INDEPENDENCE ANALYSIS##############################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

def doIndependenceAnalysisTwo(methodNum, iterations, numClimbers, numClimbersChanged, numProblemsChanged, numProblems = 4,
                              randomNumberGenerator = None, haveClimberAbilities = True):
    # make list of climbers
    climbers = [0] * numClimbers
    for i in range(0, numClimbers):
        climbers[i] = str(i)

    sum = 0
    for count in range(0, iterations):  # runs the number of times that iterations specifies (upper bound in range not hit):
        resultSet = ResultSet(numClimbers, numProblems, randomNumberGenerator, haveClimberAbilities=haveClimberAbilities)
        #ranks, pointsPerProblem, attemptsPerProblem, topsPerProblem, maxPoints = generateResultSet(numClimbers, numProblems, randomNumberGenerator)
        ranks, pointsPerProblem, attemptsPerProblem, topsPerProblem, maxPoints = resultSet.returnResultSet()
        ranker = ClimbingRanker("", [climbers, numProblems, ranks, topsPerProblem, attemptsPerProblem, pointsPerProblem, maxPoints])
        results1 = ranker.runMethod(methodNum)  # run the specified method
        #ranks2, pointsPerProblem2, attemptsPerProblem2, topsPerProblem2 = \
        #    generateResultSetTwo(numClimbers, numProblems, pointsPerProblem, attemptsPerProblem, maxPoints, numClimbersChanged, numProblemsChanged, randomNumberGenerator)
        ranks2, pointsPerProblem2, attemptsPerProblem2, topsPerProblem2 = resultSet.generateResultSetTwo(numClimbersChanged, numProblemsChanged, randomNumberGenerator)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks2, topsPerProblem2, attemptsPerProblem2, pointsPerProblem2, maxPoints])
        results2 = ranker.runMethod(methodNum)
        sumAdd = compareResultsTwo(results1, results2, numClimbersChanged)
        if(sumAdd == 0 and methodNum == 15): #linear program
            bf1 = pema.bruteForceLP(ranks, False)
            bf2 = pema.bruteForceLP(ranks2, False)
            indexOfOneInOne = pema.getIndexInList(bf1, tuple(results1))
            indexOfOneInTwo = pema.getIndexInList(bf2, tuple(results1))
            indexOfTwoInTwo = pema.getIndexInList(bf2, tuple(results2))
            indexOfTwoInOne = pema.getIndexInList(bf1, tuple(results2))
            if (indexOfOneInOne != 1 or indexOfTwoInTwo != 1):
                print("there were tops")
            elif (indexOfOneInTwo != 1 and indexOfTwoInOne != 1):
                print("ranks1: ", ranks)
                print("results1: ", results1)
                print("tops per problem 1:", topsPerProblem)
                print("ranks2:", ranks2)
                print("results2: ", results2)
                print("tops per problem 2: ", topsPerProblem2)
                print("index of two in one: ", indexOfTwoInOne, ", index of one in two: ", indexOfOneInTwo)
        sum += sumAdd
    return sum / iterations


#################COMPARE FUNCTION##############################
def compareResultsTwo(results1, results2, numClimbersChanged):
    """
    Compares the two ranked lists of results and determines if the relative order of the last numClimbers - numClimbersChanged has changed
    :param results1: first list of results
    :param results2: second list of results
    :param numClimbersChanged: number of climbers whose score was changed
    :return: 1 if the method was "independent" for these two results (relative order of those climbers didn't change),
    0 otherwise
    """
    numClimbers = len(results1)
    #loop through every combination of two climbers in the set of climbers whose relative placement shouldn't have changed
    for i, j in combinations(range(numClimbersChanged, numClimbers), 2):
        diff1 = results1[i] - results1[j]
        diff2 = results2[i] - results2[j]
        if(np.sign(diff1) != np.sign(diff2)): #relative order of the climbers changed
            #print("not independent, 0")
            #print("results1 are ", results1)
            #print("results2 are ", results2)
            return 0
    #print("independent, 1")
    return 1

#############################METHOD THAT DEALS WITH WRITING RESULTS TO FILE##################################
def writeToFile(listOfMethodNums, results, fileName):
    """
    Writes the results to a csv file
    :param listOfMethodNums: list of the numbers of the methods we analyzed
    :param results: list of the independence indices for each method (in the order of listOfMethodNums)
    :param fileName: name of the file to write the results to
    """
    with open(fileName, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['method', 'percentage of times independent'])
        for index in range(0, len(listOfMethodNums)):
            methodName = rmc.getMethod(listOfMethodNums[index])
            writer.writerow([methodName, results[index]])


###############################METHODS TO DO MULTITHREADING OF ANALYSIS#############################################
resultLock = Lock()

def doIndependenceAnalysisMultithreaded(listOfMethodNums, numberOfClimbers, numberOfClimberChanged,
                                        numberOfProblemsChanged, iterations, seed = 1, haveClimberAbilities = True):
    results = [0] * len(listOfMethodNums)  # store the independence index for each method (each one produced on a different thread)
    threads = [0] * len(listOfMethodNums)  # store all the threads that are running
    for index in range(0, len(listOfMethodNums)):
        methodNum = listOfMethodNums[index]
        threadIndex = index
        random = np.random.RandomState() #create an instance of a random number
        random.seed(seed) #set the seed to 1
        threads[threadIndex] = Thread(target=runAnalysisOnNewThread, args=(methodNum, iterations, numberOfClimbers,
                                            numberOfClimberChanged, numberOfProblemsChanged, threadIndex, results, random,
                                                                           haveClimberAbilities))
        threads[threadIndex].start()
    for thread in threads:
        thread.join()
    return results

def runAnalysisOnNewThread(methodNum, iterations, numClimbers, numClimbersChanged, numProblemsChanged,
                           threadIndex, results, random, haveClimberAbilities):
    """
    Runs the independence analysis 2 on a new thread and stores the result in results at threadIndex
    :param methodNum: number of the method to run
    :param iterations: number of times to run the method
    :param numClimbers: number of climbers
    :param numClimbersChanged: number of climbers whose performance will change between profiles
    :param numProblemsChanged: number of problems on which those climbers' scores will change
    :param threadIndex: index of this thread (for writing into results)
    :param results: list of the independence indices
    :param random: random number generator for this thread
    """
    global resultlock
    result = doIndependenceAnalysisTwo(methodNum, iterations, numClimbers, numClimbersChanged,
                                        numProblemsChanged, randomNumberGenerator = random,
                                       haveClimberAbilities = haveClimberAbilities)
    resultLock.acquire() #not sure if this is absolutely necessary but it seems like a good idea
    results[threadIndex] = result
    resultLock.release()

########################THE "MAIN METHOD" WHERE WE ACTUALLY RUN THE INDEPENDENCE ANALYSIS############################



#print(doIndependenceAnalysisTwo(15, 10, 15, 1, 4))

#numberOfClimbers = 20
# numberOfProblemsChanged = 4
# numberOfClimbersChanged = 1
# for numberOfClimbers in range(5, 10, 5):
#     listOfMethodNums = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
#     methodNames = [0]*len(listOfMethodNums)
#     methodIndependencePercent = [0]*len(listOfMethodNums)
#     for index in range(0, len(listOfMethodNums)):
#         random.seed(1)
#         np.random.seed(1)
#         methodNum = listOfMethodNums[index]
#         methodNames[index] = rmc.getMethod(methodNum)
#         print(methodNames[index])
#         methodIndependencePercent[index] = \
#             doIndependenceAnalysisTwo(methodNum, 1000, numberOfClimbers, numberOfClimbersChanged, numberOfProblemsChanged)
#         print(methodIndependencePercent[index])
    # with open('independencePercentagesFor' + str(numberOfClimbers) +
    #                   'ClimbersAnd' + str(numberOfClimbersChanged) + 'ClimbersChangingScoreOn' +
    #                   str(numberOfProblemsChanged) + 'Problems.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(['method', 'percentage of times independent'])
    #     for index in range(0, len(methodNames)):
    #         writer.writerow([methodNames[index], methodIndependencePercent[index]])

#listOfMethodNums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
#listOfMethodNums = [15]
#random.seed(3)
#results = doIndependenceAnalysisMultithreaded(listOfMethodNums, 5, 1, 4, 1000, seed=3, haveClimberAbilities = True)
#print(results)
#writeToFile(listOfMethodNums, results, 'test.csv')

#listOfMethodNums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
#random.seed(1)
#results = doIndependenceAnalysisMultithreaded(listOfMethodNums, 5, 1, 4, 1000, seed=1, haveClimberAbilities=False)
#print(results)