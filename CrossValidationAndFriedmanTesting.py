from RankingMethodsClass import ClimbingRanker
import RankingMethodsClass as rmc
from itertools import combinations
import numpy as np
import FriedmanTest as ft
import csv


def predictedError(rank, testRank):
    """
    calculates predicted error as described in the rating methods paper from Braxton
    :param rank: 1D list
    :param testRank: aggregated rank created by some ranking method
    :return: number corresponding to how well testRank predicted rank
    """
    sum = 0
    for i,j in combinations(range(len(testRank)), 2):
        if(rank[i]<rank[j] and testRank[i]>= testRank[j]): #i beat j in the data but the testRank has i behind or tied with j
            sum += 1
        elif(rank[i] == rank[j] and testRank[i] != testRank[j]):
            sum += 1
    return sum

def merge(climbers1, climbers2, list1, list2, outproblem):
    """
    merges data in list1 and list2 except for data for the specified problem
    :param climbers1: 1D list of climbers corresponding to data in list1 (will be the order of climbers in the output data)
    :param climbers2: 1D list of climbers corresponding to data in list2
    :param list1: numpy matrix or 2D list with data where each row corresponds to climbers1[row]
    :param list2: numpy matrix of 2D list with data where each row corresponds to climbers2[row]
    :param outproblem: problem that will not be included in the merge (number between 0 and total number of problems, if
    outproblem is larger than number of problems in list1, the correct problem from list2 will be found)
    :return: numpy matrix where rows correspond to climbers (in order of climbers1 list) and columns are each problem
    :raise ValueError: if the climbers in the two climber lists are not the same or if list1 is not a numpy matrix or 2D list
    """
    if (isinstance(list1[0], list) or isinstance(list1[0], np.ndarray)):
        numClimbers = len(list1)
        numProblems = len(list1[0]) + len(list2[0])
        endList = np.zeros(shape=(numClimbers, numProblems-1)) #will contain the merged data
        for row in range(0,numClimbers):
            removed = False  # will be true when outproblem has been removed
            for problem in range(0,len(list1[0])):
                if(not(problem == outproblem)): #problem is not the outproblem
                    if(not(removed)):
                        endList[row][problem] = list1[row][problem]
                    else: #if problem has been removed the data will have to be shifted to the left by one
                        endList[row][problem-1] = list1[row][problem]
                else:
                    removed = True
            if(not(climbers2[row] in climbers1)): #climber in climber2 not found in climber1
                raise ValueError("climber lists do not match")
            endLocation = climbers1.index(climbers2[row])
            for problem in range(0,len(list2[0])):
                if(not(problem + len(list1[0]) == outproblem)):
                    if(not(removed)):
                        endList[endLocation][problem + len(list1[0])] = list2[row][problem]
                    else:
                        endList[endLocation][problem+len(list1[0])-1] = list2[row][problem]
                else:
                    removed = True
        return endList
    else:
        raise ValueError("list1 is not a matrix")

def getIth(list1, i):
    """
    :param list1: numpy matrix or 2D array from which the ith column will be taken
    :param i: column of list1 that will be returned
    :return: 1D list that holds the data from the ith column of list1
    :raise ValueError: if list1 is not a numpy matrix of 2D list
    """
    if (isinstance(list1[0], list) or isinstance(list1[0], np.ndarray)):
        newList = []
        for row in list1:
            newList.append(row[i])
        return newList
    else:
        raise ValueError("list1 must be a matrix")

def flipRankings(rankings):
    """
    :param rankings: numpy matrix of rankings where each column is a complete rank
    :return: numpy matrix of rankings where each row is a complete rank
    """
    numClimbers = len(rankings)
    numProblems = len(rankings[0])
    ranks = np.zeros(shape = (numProblems, numClimbers))
    for row in range(0,len(ranks)):
        for col in range(0,len(ranks[0])):
            ranks[row][col] = rankings[col][row]
    return ranks

def makeRank(list):
    """
    takes a general list and makes it into a rank (accounting for ties)
    :param list: list to be made into a rank
    :return: ranking made from the list
    """
    listCopy = list.copy() #so that the list doesnt change in getMinValueInList
    i = 1 #keeps track of what rank the current climber should get
    listRank = [0]*len(list)
    while(i<=len(list)):
        minIndices = getMinValueInList(listCopy)
        for index in minIndices:
            listRank[index] = i
        i = i+len(minIndices)
    return listRank

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

def makeRanks(matrix):
    """
    takes list of ranks and makes them valid (i.e. maintains order of climbers but gives them ranks that make sense)
    used to make qualis ranks valid because about half of the data from each problem is cut off when doing cross validation
    with semis problems too
    :param matrix: numpy matrix where each row is a climber and each column is a problem, entries are the rank of each
    climber on each problem
    :return: numpy matrix where each column is a valid rank
    """
    matrix = flipRankings(matrix)
    for row in range(len(matrix)):
        matrix[row] = makeRank(matrix[row])
    return flipRankings(matrix)

def getTotal(blankPerProblem):
    """
    :param blankPerProblem: numpy matrix of topsPerProblem or pointsPerProblem or attemptsPerProblem
    :return: the total number of tops or points or attempts for each climber in a 1D list
    """
    total = []
    for problem in blankPerProblem:
        sum = 0
        for x in problem:
            sum += x
        total.append(sum)
    return total

def getCrossValidationScore(num):
    """
    performs cross validation using 7 problems from each of 8 age groups. 6 problems are used to create the aggregated
    rank, and then that rank is used to predict the ranking on the final problem. in total, 56 predictions are done
    (7 for each age group with 8 age groups)
    :param method: method used to create aggregated rank
    :return: cross validation score for the given method
    """
    categories = ["fya", "fyb", "fyc","fyd","mya","myb","myc","myd"]
    predictiveErrorSum = 0
    predictiveErrors = []
    for cat in categories:
        semis = ClimbingRanker(cat + "BNatsSemis2016.csv")
        qualis = ClimbingRanker(cat + "BNatsQualis2016.csv", len(semis.climbers)) #get data from those who made semis
        pESum = 0
        for i in range(0,7):
            ranks = merge(semis.climbers, qualis.climbers, semis.ranks, qualis.ranks, i)
            topsPerProblem = merge(semis.climbers, qualis.climbers, semis.topsPerProblem, qualis.topsPerProblem, i)
            pointsPerProblem = merge(semis.climbers, qualis.climbers, semis.pointsPerProblem, qualis.pointsPerProblem, i)
            attemptsPerProblem = merge(semis.climbers, qualis.climbers, semis.attemptsPerProblem, qualis.attemptsPerProblem, i)
            points = getTotal(pointsPerProblem)
            tops = getTotal(topsPerProblem)
            attempts = getTotal(attemptsPerProblem)
            climbers = semis.climbers
            if(i<len(semis.ranks[0])):
                ranksi = getIth(semis.ranks, i)
            else:
                ranksi = getIth(qualis.ranks, i-len(semis.ranks[0]))
            ranker = ClimbingRanker(cat, [climbers, 6, ranks, tops, attempts, attemptsPerProblem, points, pointsPerProblem, topsPerProblem, cat, "", True])
            rank = ranker.runMethod(num)
            predictiveErrorSum += predictedError(ranksi, rank) #test how well problem i is predicted with other problems
            pESum += predictedError(ranksi, rank)
        predictiveErrors.append(pESum/7)
    return predictiveErrorSum/(len(categories)*7), predictiveErrors

def writeCSVFile(methods, scores):
    """
    writes results of cross validation to CSV file so I can run the Friedman test on them in R
    :param methods: list of method names that correspond with scores
    :param scores: 2D list where each sublist is the 8 crossvaidation scores of a given method
    """
    with open('crossValidation.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['judge', 'trt', 'evaluation'])
        for method in range(0,len(methods)):
            for judge in range(0,len(scores[method])):
                writer.writerow([judge+1, methods[method], scores[method][judge]])

results = []
methods = []
#15 for just methods, 30 for methods and local kemenization of methods
#13 is walg no tops - worse than other walgs
#0 and 1 are l2 norm methods - not using anymore because they are dumb
topsMethods = [2,4,7,9,10,11,12,13,15] #10 is abs10 method - doesn't use tops but does use flash bonus
oldMethods = [9,10,11]
usacMethods = [4,8,9,10]
allMethods = [2,3,4,5,6,7,9,10,11,12,13,14,15]
for num in allMethods:
    methods.append(rmc.getMethod(num))
    results.append(getCrossValidationScore(num)[1])
writeCSVFile(methods, results)

for result in results:
    print(result)

print(ft.friedmanTest(*results))