import numpy as np
from RankingMethodsClass import ClimbingRanker
import RankingMethodsClass as rmc
import random
import copy
from itertools import permutations
import BubbleDistance as bd
import LinearProgramming as lp

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

def produceParetoEfficientResultSet(numClimbers, numProblems = 4):
    """
    Produces a set of results for use in pareto efficiency analysis
    :param numClimbers: number of climbers to use in the result
    :param numProblems: number of problems in the result set
    :return: result set (ranks matrix - rows = climbers, columns = problems)
    """
    ranks = np.zeros(shape=(numClimbers, numProblems)) #entry i,j is rank of ith climber on jth problem

    #fill up the ranks matrix with random ranks but make sure the first climber is ranked above the second climber on
    #every problem
    for col in range(0, numProblems):
        ranks[0][col] = random.randrange(1, numClimbers, 1) #generate random integer between 1 and numClimbers-1
    for col in range(0, numProblems):
        ranks[1][col] = random.randrange(ranks[0][col], numClimbers+1, 1) #generate random int below the rank of climber 1
    for row in range(2, numClimbers):
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

def bruteForceWalg(ranks, ties = True):
    """
    Brute forces the solution to the minimizing problem that is the geometric median. Returns a list of all the possible
    ranks and their sums.
    :param ranks: matrix of ranks to be aggregated (columns are complete ranks)
    :param ties: true if ties should be considered, false otherwise
    :return: list of all possible ranks and their corresponding sums
    """
    ranksAndScores = []
    if(not ties):
        for permutation in permutations([1,2,3,4,5],5):
            entry = []
            entry.append(permutation)
            entry.append(calculateGeometricMedianSum(ranks, permutation))
            ranksAndScores.append(entry)
    ranksAndScores = sorted(ranksAndScores, key=lambda x: x[1])
    return ranksAndScores

def getIndexInList(list, element):
    """
    Finds the index in the list of the sublist that has the given tuple element
    :param list: list of sublists where each sublist has two elements: a tuple and an integer
    :param element: tuple to be found in the list
    :return: index in the list of the sublist with the given tuple element
    """
    index = 0
    for sublist in list:
        if(sublist[0] == element):
            if(sublist[1] == list[0][1]): #multiple optimal solutions
                return 1
            else:
                return index
        index += 1
    return -1

def bruteForceLP(ranks, ties = True):
    """
    Brute forces the solution to the minimizing problem that the linear program solves. Returns a list of all the possible
    ranks and their sums.
    :param ranks: matrix of ranks to be aggregated (columns are complete ranks)
    :param ties: true if ties should be considered, false otherwise
    :return: list of all possible ranks and their corresponding sums
    """
    ranksAndScores = []
    if(not ties):
        for permutation in permutations([1,2,3,4,5],5):
            entry = []
            entry.append(permutation)
            entry.append(bd.linProgrammingDistance(permutation, lp.flipRankings(ranks)))
            ranksAndScores.append(entry)
    ranksAndScores = sorted(ranksAndScores, key=lambda x: x[1])
    return ranksAndScores

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
        results1 = ranker1.runMethod(methodNum)  # run specified method
        ranks2 = produceMonotonicityResultSetTwo(ranks1, numProblems, numClimbers, numProblemsChanged)
        ranker2 = ClimbingRanker("", [climbers, numProblems, ranks2, tops])
        results2 = ranker2.runMethod(methodNum) #run specified method
        sumAdd = compareMonotoneResults(results1, results2)
        if(sumAdd == 0):
            if(methodNum == 12 or methodNum == 13):
                intmin1 = calculateGeometricMedianSum(ranks1, results1)
                intmin2 = calculateGeometricMedianSum(ranks2, results2)
                intoneTo2 = calculateGeometricMedianSum(ranks1, results2)
                inttwoTo1 = calculateGeometricMedianSum(ranks2, results1)
                print(iteration)
                print("ranks1: ", ranks1)
                print("results1: ", results1)
                print("ranks2:", ranks2)
                print("results2: ", results2)
                print("intmin1: ", intmin1)
                print("intmin2: ", intmin2)
                print("intoneTo2: ", intoneTo2)
                print("inttwoTo1: ", inttwoTo1)
                accurate1 = min(bruteForceWalg(ranks1, False), key=lambda x:x[1])
                accurate2 = min(bruteForceWalg(ranks2, False), key=lambda x:x[1])
                print("minimizing rank for first set of results: ", accurate1)
                print("minimizing rank for second set of results: ", accurate2)
            #elif(methodNum == 15):
            #    bf1 = bruteForceLP(ranks1, False)
            #    bf2 = bruteForceLP(ranks2, False)
            #    indexOfOneInOne = getIndexInList(bf1, tuple(results1))
            #    indexOfOneInTwo = getIndexInList(bf2, tuple(results1))
            #    indexOfTwoInTwo = getIndexInList(bf2, tuple(results2))
            #    indexOfTwoInOne = getIndexInList(bf1, tuple(results2))
            #    if(indexOfOneInOne != 1 or indexOfTwoInTwo != 1):
            #        raise ValueError("this should not be happening")
            #    if(indexOfOneInTwo != 1 or indexOfTwoInOne != 1):
            #        print("ranks1: ", ranks1)
            #        print("results1: ", results1)
            #        print("ranks2:", ranks2)
            #        print("results2: ", results2)
            else:
                print("ranks1: ", ranks1)
                print("results1: ", results1)
                print("ranks2:", ranks2)
                print("results2: ", results2)
            # if(twoTo1>min2 and oneTo2>min1):
            #     for problem in range(0, numProblems):
            #         if(ranks1[0][problem] != ranks2[0][problem]):
            #             print(iteration)
            #             print("ranks1: ", ranks1)
            #             print("results1: " ,results1)
            #             print("ranks2:", ranks2)
            #             print("results2: ", results2)
            #             print("min1: ", min1)
            #             print("min2: ", min2)
            #             print("oneTo2: ", oneTo2)
            #             print("twoTo1: ", twoTo1)
            #         else:
            #             print("rank of first climber didn't change")
            # else:
            #     print("inaccurate geometric median calculation")
        sum += sumAdd
    return sum/iterations

def doParetoEfficiencyAnalysis(numClimbers, numProblems, iterations, methodNum):
    """
    Creates a profile where climber 1 is ranked higher than climber 2 on every problem. Determines if climber 2 can
    win the competition (if they can the method is not pareto efficient).
    Repeated the number of times specified and returns a "pareto efficiency score"
    :param numClimbers: number of climbers in the profiles to be created
    :param numProblems: number of problems in the profiles to be created
    :param iterations: number of iterations
    :param methodNum: number of the method we are testing
    :return: pareto efficiency score, or the percentage of the time the method was pareto efficient
    """
    # make list of climber names
    climbers = [0] * numClimbers
    for i in range(0, numClimbers):
        climbers[i] = str(i)

    tops = [0] * numClimbers

    sum = 0
    for iteration in range(0, iterations):
        ranks = produceParetoEfficientResultSet(numClimbers, numProblems)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks, tops])
        results = ranker.runMethod(methodNum)  # run specified method
        if(results[0]<=results[1]): #climber one is ranked higher
            sumAdd = 1
        else:
            sumAdd = 0
            print("NO")
        sum += sumAdd
    return sum/iterations


# methods = [0,1,2,3,4,5,6,7,8,12,13,14,15,16]
# for methodNum in methods:
#    random.seed(6)
#    print(rmc.getMethod(methodNum))
#    print(doParetoEfficiencyAnalysis(5, 4, 10000, methodNum))

random.seed(11)
print(doParetoEfficiencyAnalysis(20, 4, 100, 15))
###it would appear that the linear program is monotone, however our implementation is ALMOST monotone (99% of the time)
###but fails to provide monotone results occasionaly because there are multiple optimal solutions and we have no way to
###know which one to choose

###all of the methods are pareto efficient

#12 = walg integer
#13 = walg optimal integer
#15 = lin prog


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

def findPercentOfTimeThatResultEqualsBruteForceResult(iterations, numClimbers, numProblems, methodNum):
    """
    Generates a random result set and calculates the aggregated rank using weiszfeld's algorithm or the linear program.
    Then calculates the rank that minimizes the sum (that you minimize when you find the geometric median or the linear
    program solution) using brute force. Sees how many times these two ranks are equal and also returns the average
    placement of the produced rank in the list of brute forced ranks (is it usually first or second best... etc)
    :param iterations: number of times this will be calculated and results will be averaged
    :param numClimbers: number of climbers in the results set (number of alternatives in each ranked list)
    :param numProblems: number of problems in the results set (number of ranked lists being aggregated)
    :return: percent of time that the given algorithm returns the same rank as the brute force algorithm, average
    placement of the given algorithm's result in the list produced by the brute force method
    """
    tops = [0]*numClimbers
    climbers = [""]*numClimbers

    sum = 0
    averagePlacement = 0
    for iteration in range(0, iterations):
        ranks = produceResultSet(numClimbers, tops, numProblems)
        ranker = ClimbingRanker("", [climbers, numProblems, ranks, tops])
        if(methodNum == 12): #walg integer
            result = ranker.wAlgorithmInteger()
            bfResult = bruteForceWalg(ranks,False)
        elif(methodNum == 15): #linear program
            result = ranker.linearProgrammingOptimalSplit()
            bfResult = bruteForceLP(ranks, False)
        else:
            bfResult = [[]]
            result = []
        minBFResult = bfResult[0][0]
        same = True
        for climber in range(0, numClimbers):
            if(result[climber] != minBFResult[climber]):
                same = False
                #print(result, minBFResult)
                #print(bfResult)
                break
        if(same):
            sum += 1
            averagePlacement += 1
        else:
            index = getIndexInList(bfResult, tuple(result))
            if(bfResult[index][1] == bfResult[0][1]): #multiple optimal ranks
                averagePlacement += 1
                sum += 1
            else:
                averagePlacement += index
    return sum/iterations, averagePlacement/iterations


####################CHECKING VALIDITY OF VARIOUS APPROXIMATING METHODS################
#random.seed(3)
#print(findPercentOfTimeThatResultEqualsBruteForceResult(10000, 5, 4, 15))
#for walg: equal about 50% of the time, average placement of produced result in sorted list of all possible results is 1.7
#for linear program: equal every time (although sometimes there are multiple minimizing solutions)


##########CHECKING COUNTEREXAMPLES FOR LINEAR PROGRAM#########################
#ranks1 = [[2,3,4,3],[1,2,5,4],[4,1,1,4],[4,3,1,1],[2,3,1,1]]
#results1 = [3,5,4,2,1]
#bf1 = bruteForceLP(ranks1, False)
#print(bf1)

#ranks2 = [[1,3,4,3],[1,2,5,4],[4,1,1,4],[4,3,1,1],[3,3,1,1]]
#results2 = [4,5,2,3,1]
#bf2 = bruteForceLP(ranks2, False)
#print(bf2)

#print("index of results1: ", getIndexInList(bf1, tuple(results1)))
#print("index of results1 in bf2: ", getIndexInList(bf2, tuple(results1)))
#print("index of results2: ", getIndexInList(bf2, tuple(results2)))
#print("index of results2 in bf1: ", getIndexInList(bf1, tuple(results2)))



