import scipy.optimize
import numpy as np
from itertools import combinations
import BubbleDistance as bd

def createEqualityMatrix(n): #creates matrix for equality constraint for rankings of n items
    """
    :param n: number of climbers being ranked
    :return: matrix for equality constraint in linear programming (xij + xji = 1)
    """
    numRows = len(list(combinations(range(n), 2)))
    matrix = np.zeros(shape=(numRows,n**2)) #n choose 2 rows, n^2 columns
    row = 0
    for i,j in combinations(range(n),2):
        matrix[row][sub2ind([n,n],i,j)] = 1
        matrix[row][sub2ind([n,n],j,i)] = 1
        row+=1
    return matrix

def sub2ind(array_shape, rows, cols): #FROM ONLINE
    """turn matrix ij reference into simple index reference if that matrix was actually a list"""
    return rows * array_shape[1] + cols


def createInequalityMatrix(n):
    """
    :param n: number of climbers being ranked
    :return: matrix for inequality constraint for linear programming
    """
    numRows = int(n*(n-1)*(n-2)/3) #always integer anyway so don't have to worry about it
    matrix = np.zeros(shape=(numRows, n**2))
    row = 0
    for i,j,k in combinations(range(n), 3):
        #(ijk)
        matrix[row][sub2ind([n,n], i, j)] = 1
        matrix[row][sub2ind([n,n], j, k)] = 1
        matrix[row][sub2ind([n,n], k, i)] = 1
        row+=1
        #(ikj)
        matrix[row][sub2ind([n,n], i, k)] = 1
        matrix[row][sub2ind([n,n], k, j)] = 1
        matrix[row][sub2ind([n,n], j, i)] = 1
        row+=1
    return matrix

def createC(rankings):
    """
    :param rankings: numpy matrix where each row corresponds to a climber and each column is a problem. each entry is
    that climber's rank on the problem
    :return: matrix where c(i,j) is (# of lists with i>j) - (# of lists with j>i) (except is is flattened to a list)
    """
    #flip rankings so each row is a complete ranking instead of each row being that climber's ranks
    ranks =[[]]
    #gets ranks set up to be correct dimensions
    for row in range(0,len(rankings[0])):
        for col in range(0,len(rankings)):
            ranks[row].append(0)
        if(row != len(rankings[0])-1):
            ranks.append([])
    #puts values in ranks
    for row in range(0, len(ranks)):
        for col in range(0, len(ranks[0])):
            ranks[row][col] = rankings[col][row]
    n = len(ranks[0]) #number of climbers being ranked
    c = [0]*(n**2)
    for i,j in combinations(range(n),2): #each pair of climbers i,j
        sum=0
        for rank in ranks:
            if(rank[i]<rank[j]): #i is ranked higher than j
                sum+=1
            elif(rank[j]<rank[i]): #j is ranked higher than i
                sum-=1
        c[sub2ind([n,n],i,j)] = -sum #would be positive in normal matrix C but negate value so python can minimize it
        c[sub2ind([n, n], j, i)] = sum  # would be negative in normal matrix C but switch value so python can minimize it
    return c

def makeMatrix(list): #makes the resultant vector x into a matrix
    """
    :param list: list to be made into a square numpy matrix
    :return: square numpy matrix that has same information as the list
    """
    matrixSize = int(len(list)**(1/2))
    matrix = np.zeros(shape = (matrixSize, matrixSize))
    index = 0
    for row in range(0,matrixSize):
        for col in range(0,matrixSize):
            matrix[row][col] = list[index]
            index += 1
    return matrix

def calculateConformity(rank, c):
    """
    :param rank: some rank that you want to calculate the conformity of (conformity = what linear programming is maximizing)
    :param c: c matrix as used in linear programming (reflects the ranks that rank is an aggregation of)
    :return: conformity as determined in linear programing
    """
    x = bd.createX(rank)
    sum = 0
    for row in range(0,len(x)):
        for col in range(0,len(x)):
            sum += x[row][col]*c[sub2ind([len(x), len(x)], row, col)]
    return sum

def getFinalRank(matrix, c):
    """
    :param matrix: matrix where matrix(i,j) = 1 if i beats j and 0 otherwise
    :param c: c matrix as used in linear programming (reflects the ranks that were aggregated)
    :return: returns final rank calculated from matrix - not yet sorted by tops
    """
    numClimbers = len(matrix)
    finalRank = [0]*len(matrix)
    for row in range(0,len(matrix)):
        sum=0
        for col in range(0,len(matrix)):
            sum+= matrix[row][col]
        finalRank[row] = int(len(matrix)-sum)
    #now see if there are other optimal ranks - if climber i finishes in mth place and climber j finishes in m+1 place,
    #if cij = cji then they could have finished in the opposite places and that would have been optimal too -
    #see if this result has better conformity
    i=1
    tie = 1
    sum = calculateConformity(finalRank, c)
    while(i+tie<=len(finalRank)):
        higher = finalRank.index(i)
        lower = finalRank.index(i+tie)
        if(c[sub2ind([numClimbers, numClimbers], higher, lower)] == c[sub2ind([numClimbers, numClimbers], lower, higher)]): #cij == cji
            testRank = finalRank.copy()
            testRank[lower] = testRank[higher]
            testSum = calculateConformity(testRank, c)
            if(testSum<sum):
                finalRank[lower] = finalRank[higher]
                tie += 1
            else:
                i+= tie
                tie = 1
        else:
            i+= tie
            tie = 1
    return finalRank

def getFinalClimberRank(finalRank, climbers):
    """
    :param finalRank: aggregated rank as calculated in linear programming (1D list)
    :param climbers: 1D list of climbers
    :return: climbers in order of their rank (CANNOT BE TIES)
    """
    finalClimberRank = [0]*len(climbers)
    for i in range(1,len(finalRank)+1):
        finalClimberRank[i-1] = climbers[finalRank.index(i)]
    return finalClimberRank

def sortByTops(finalRank, climbers, tops):
    """
    sorts ranking so that a climber with more tops is not behind a climber with fewer tops
    :param finalRank: rank to be sorted (1D list)
    :param climbers: 1D list of climbers
    :param tops: 1D list of total number of tops for each climber
    :return: finalRank sorted by number of tops and a list of climbers in order of rank (does account for ties)
    """
    rankAndTops = [] #list of lists, first index in inner list is rank, second is tops, third is climber (this way you can sort and still know who is who
    for i in range(0, len(finalRank)):
        subList = []
        subList.append(finalRank[i])
        subList.append(tops[i])
        subList.append(climbers[i])
        rankAndTops.append(subList)
    rankAndTops.sort(key=lambda x: x[0]) #sort on rank
    rankAndTops.sort(key=lambda x: x[1], reverse=True) #reverse sort on number of tops
    topRank = [0] * len(finalRank)
    climberRank = [""] * len(finalRank)
    topRank[climbers.index(rankAndTops[0][2])] = 1  # lowest number is first
    climberRank[0] = rankAndTops[0][2]
    current = 0
    for i in range(1,len(rankAndTops)):
        if(rankAndTops[i][0] == rankAndTops[i-1][0] and rankAndTops[i][1] == rankAndTops[i-1][1]): #tie
            topRank[climbers.index(rankAndTops[i][2])] = topRank[climbers.index(rankAndTops[i-1][2])] #set rank of next climber to rank of previous climber
            climberRank[current] += ", " + rankAndTops[i][2]
        else:
            current = i
            topRank[climbers.index(rankAndTops[i][2])] = i+1 #set rank of climber to next available rank
            climberRank[current] = rankAndTops[i][2]
    return topRank, climberRank

def getClimberIndex(rankAndTops, climber): #gets index of climber in rankAndTops
    """
    :param rankAndTops: #list of lists, first index in inner list is rank, second is tops, third is climber
    :param climber: climber whose index is desired
    :return: index of climber in rankAndTops (index of list that contains that climber)
    """
    for i in range(0,len(rankAndTops)):
        if(rankAndTops[i][2] == climber):
            return i

def splitProblemByTops(ranks, tops, climbers):
    """
    :param ranks: numpy matrix where each column is the complete ranking of climbers on that problem
    :param tops: 1D list where each entry is total number of tops for the climber
    :param climbers: 1D list of climbers
    :return: list of lists of ranks where each element in ranksList is the ranks of climbers with a specific number
    of tops, nCount (how many climbers are in each top set), and climberList (list of climbers in each top set)
    """
    #turn ranks from numpy matrix into 2d list
    ranksL = []
    temp = []
    for row in range(0,len(ranks)):
        for col in range(0,len(ranks[0])):
            temp.append(ranks[row][col])
        ranksL.append(temp)
        temp = []
    ranksList = [] #each entry in list will be the ranks for climbers with x tops
    nList = [] #keeps track of how many climbers are being ranked for each rank in ranksList
    climberList = [] #keeps track of climbers getting ranked for each rank in ranksList
    previousNum = tops[0] #so you know if we are onto a new set of tops
    rank = [] #keeps track of ranks for each set of tops, then appended to ranksList
    climberTemp = [] #keeps track of climbers for each set of tops, then appended to climberList
    nCount = 0 #keeps track of number of climbers for each set of tops, then appended to nList
    for i in range(0,len(tops)):
        if(tops[i] == previousNum): #still on the same set of tops
            rank.append(ranksL[i])
            climberTemp.append(climbers[i])
            nCount += 1
        else: #new set of tops
            #append rank, climberTemp, and nCount
            ranksList.append(rank)
            nList.append(nCount)
            climberList.append(climberTemp)
            #set them all back to normal
            rank = []
            nCount = 1
            climberTemp = []
            #and append stuff for current i
            previousNum = tops[i]
            rank.append(ranksL[i])
            climberTemp.append(climbers[i])
    #append rank, climberTemp, and nCount for this last set of tops
    ranksList.append(rank)
    ranksList = fixRankList(ranksList)
    nList.append(nCount)
    climberList.append(climberTemp)
    return ranksList, nList, climberList

def fixRankList(ranksList):
    """
    fixes ranksList generated by splitProblemByTops so each set of ranks in the list is complete
    :param ranksList: list of lists of ranks generated by splitProblemByTops
    :return: complete list of lists of ranks
    """
    goodRanksList = []
    for rankSet in ranksList:
        rankSetF = flipRankings(rankSet)
        rankSetFinal = []
        for row in rankSetF:
            rankSetFinal.append(makeRank(row))
        goodRanksList.append(flipRankings(rankSetFinal).tolist())
    return goodRanksList

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

def getIndicesOfNum(finalRank, i):
    """
    :param finalRank: rank where indices of i will be found
    :param i: number whose indices in finalRank will be found
    :return: list of all the indices i appears at in finalRank
    """
    indices = []
    for j in range(0,len(finalRank)):
        if(finalRank[j] == i):
            indices.append(j)
    return indices

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

def smash(smashedRanks, finalRank, i, nList):
    """
    used for split linear programming - get the result and then add it to the list of ranks (smash it on the end)
    :param smashedRanks: 1D list of rank for each climber
    :param finalRank: rank that will be added on to the end of smashedRanks
    :param i: set of climbers you are on
    :param nList: list of number of climbers in each set of tops
    """
    add = 0
    for j in range(0,i):
        add += nList[j]
    shiftedRanks = []
    for rank in finalRank:
        shiftedRanks.append(rank + add)
    smashedRanks += shiftedRanks


def optimize(ranks, climbers, tops): #does not do the spliced list
    """
    uses scipy's linear program solver to determine optimal rank
    trying to maximize cij * xij, where cij is the number of lists with
    i ranked ahead of j, and xij is 1 if i is ranked ahead of j, -1 if
    i is ranked below j, and 0 if i and j are tied.
    basically trying to minimize pairwise disagreements between final rank
    and each ranking (but not the same as minimizing the bubble distance between final rank and each ranking)
    :param ranks: numpy matrix with each column representing a complete ranking of climbers on the given problem
    :param climbers: 1D list of climbers
    :param tops: 1D list of total tops for each climber
    :return: optimal rank that maximizes conformity
    """
    n = len(climbers)
    bub = [2]*int((n*(n-1)*(n-2)/3))
    beq = [1]*int((n*(n-1)/2))
    c = createC(ranks)
    lp = scipy.optimize.linprog(c, A_ub = createInequalityMatrix(n), b_ub = bub, A_eq = createEqualityMatrix(n), b_eq = beq)
    matrix = makeMatrix(lp.get("x"))
    finalrank = getFinalRank(matrix, c)
    return sortByTops(finalrank, climbers, tops)

def optimizeSplit(ranks, climbers, tops):
    """
    splits problem up by number of tops, so find optimal rank for each set of climbers
    with the same number of tops
    uses scipy's linear program solver to determine optimal rank
    trying to maximize cij * xij, where cij is the number of lists with
    i ranked ahead of j, and xij is 1 if i is ranked ahead of j, -1 if
    i is ranked below j, and 0 if i and j are tied.
    basically trying to minimize pairwise disagreements between final rank
    and each ranking (but not the same as minimizing the bubble distance between final rank and each ranking)
    :param ranks: numpy matrix with each column representing a complete ranking of climbers on the given problem
    :param climbers: 1D list of climbers
    :param tops: 1D list of total tops for each climber
    :return: optimal rank that maximizes conformity
    """
    ranksList, nList, climberList = splitProblemByTops(ranks, tops, climbers)
    smashedRanks = []
    smashedClimbers = []
    for i in range(0,len(ranksList)):
        n = nList[i]
        bub = [2] * int((n * (n - 1) * (n - 2) / 3))
        beq = [1] * int((n * (n - 1) / 2))
        c = createC(ranksList[i])
        lp = scipy.optimize.linprog(c, A_ub = createInequalityMatrix(n), b_ub = bub, A_eq = createEqualityMatrix(n), b_eq = beq)
        finalRank = getFinalRank(makeMatrix(lp.get("x")), c)
        #finalClimberRank = getFinalClimberRank(finalRank, climberList[i])
        smash(smashedRanks, finalRank, i, nList)
        #smashedClimbers += finalClimberRank
    rank, climberRank = sortByTops(smashedRanks, climbers, tops)
    return rank, climberRank


