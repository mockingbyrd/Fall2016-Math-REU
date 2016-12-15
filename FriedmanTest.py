import numpy as np
import scipy.stats as ss

def friedmanTest(*args):
    """
    Performs Friedman test on ratings for different measurements.
    :param args: each input is a group (ratings for one measurement)
    :return: chi square value and p-value
    """
    data = []
    for arg in args:
        data.append(arg)
    dataF = flipRankings(data)
    for i in range(0,len(dataF)):
        dataF[i] = makeRank(dataF[i])
    data = flipRankings(dataF)
    tg = 0
    for group in data:
        tg += (sumList(group))**2
    k = len(data)
    n = len(data[1])
    chisquare = 12/(n*k*(k+1))*tg - 3*n*(k+1)
    p = ss.chisqprob(chisquare, k-1)
    return chisquare, p

def sumList(list):
    sum=0
    for num in list:
        sum += num
    return sum

def flipRankings(rankings):
    """
    :param rankings: numpy matrix of rankings where each column is a complete rank
    :return: numpy matrix of rankings where each row is a complete rank
    """
    numGroups = len(rankings)
    numSubjects = len(rankings[0])
    ranks = np.zeros(shape = (numSubjects, numGroups))
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
        rank = 0
        for j in range(0,len(minIndices)):
            rank += j+i
        rank = rank/len(minIndices)
        for index in minIndices:
            listRank[index] = rank
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

