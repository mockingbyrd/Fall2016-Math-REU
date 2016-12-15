#Code uses distance method from "Preference Rankings - An Axiomatic Approach"
import numpy as np
from itertools import combinations

def createMatrixWithTies(rank): #input list of ranks (like "rank" column in USAClimbing score sheets)
    """
    Creates matrix from a rank where m_{ij} is 1 if climber i is better than climber j and -1 if climber i is worse than
    climber j. entry is 0 if the two climbers tie
    :param rank: rank to turn into matrix
    :return: matrix created from rank
    """
    matrix = np.zeros(shape = (len(rank), len(rank)))
    for i,j in combinations(range(len(rank)),2): #for each pair of climbers
        if(rank[i]<rank[j]): #climber i is better than climber j
            matrix[i][j] = 1
            matrix[j][i] = -1
        elif(rank[i]>rank[j]): #climber j is better than climber i
            matrix[i][j] = -1
            matrix[j][i] = 1
        else: #tie
            matrix[i][j] = 0
            matrix[j][i] = 0
    return matrix

def d(rankA, rankB):
    """
    #calculates number of pairwise disagreements between 2 ranks (A>B vs B>A is 2, A>B vs A=B is 1)
    :param rankA: first rank
    :param rankB: second rank
    :return: number of pairwise disagreements between the two ranks
    """
    matrixA = createMatrixWithTies(rankA)
    matrixB = createMatrixWithTies(rankB)
    numCandidates = len(rankA)
    distance = 0
    for i, j in combinations(range(numCandidates), 2):
        distance += abs(matrixA[i][j]-matrixB[i][j])
    return distance

def createC(ranks):
    """
    Creates matrix C as used in linear program for list of ranks (c_{ij} = {# of lists with i above j} -
    {# of lists with i below j})
    :param ranks: list of ranks of climbers on different problems
    :return: matrix C
    """
    n = len(ranks[0])
    c = np.zeros(shape=(n, n))
    for i,j in combinations(range(n),2): #each pair of climbers i,j
        sum=0
        for rank in ranks:
            if(rank[i]<rank[j]): #i is ranked higher than j
                sum+=1
            elif(rank[j]<rank[i]): #j is ranked higher than i
                sum-=1
        c[i,j] = -sum #made negative so we can minimize conformity
        c[j,i] = sum #made positive so we can minimize conformity
    return c

def createX(finalRank):
    """
    Creates matrix X as used in linear program for final rank: x_{ij} = 1 if i beat j and 0 otherwise
    :param finalRank: rank that X will be calculated from
    :return: matrix X
    """
    matrix = np.zeros(shape = (len(finalRank), len(finalRank)))
    for i,j in combinations(range(len(finalRank)), 2):
        if(finalRank[i]<finalRank[j]): #i better than j
            matrix[i][j] = 1
    return matrix


def linProgrammingDistance(finalRank, ranks):
    """
    calculates the value of what is being maximized in linear programming model from Who's #1 book,
    except we negate the matrix C and thus minimize it (calling it "conformity")
    :param finalRank: final rank - we calculate the distance from it to each rank in ranks
    :param ranks: list of ranks we want the distance to
    :return: \sum\sum(x_{ij}c_{ij})
    """
    c = createC(ranks)
    x = createX(finalRank)
    sum=0
    for i,j in combinations(range(len(finalRank)),2):
        sum += c[i][j]*x[i][j]
    return sum

def euclideanDistance(rankA, rankB):
    """
    calculates distance between rankA and rankB (treat them as vectors in R^M) using l2 (euclidean) norm
    :param rankA: first rank
    :param rankB: second rank
    :return: distance between rankA and rankB with l2 norm
    """
    distance = 0
    for i in range(0,len(rankA)):
        distance += (rankA[i]-rankB[i])**2
    return distance**(1/2)

def l1normDistance(rankA, rankB):
    """
    calculates distance between rankA and rankB (treat them as vectors in R^M) using l1 norm
    :param rankA: first rank
    :param rankB: second rank
    :return: distance between rankA and rankB with l1 norm
    """
    distance = 0
    for i in range(0,len(rankA)):
        distance += abs(rankA[i] - rankB[i])
    return distance
