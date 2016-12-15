from RankingMethodsClass import ClimbingRanker
import LinearProgramming as lp
import numpy as np
import RankingMethodsClass as rmc
from itertools import combinations


def makeRanks(matrix):
    """
    takes list of ranks and makes them valid (i.e. maintains order of climbers but gives them ranks that make sense)
    used to make qualis ranks valid because about half of the data from each problem is cut off when doing cross validation
    with semis problems too
    :param matrix: numpy matrix where each row is a climber and each column is a problem, entries are the rank of each
    climber on each problem
    :return: numpy matrix where each column is a valid rank
    """
    matrix = lp.flipRankings(matrix)
    for row in range(len(matrix)):
        matrix[row] = lp.makeRank(matrix[row])
    return lp.flipRankings(matrix)

def chop(matrix, i):
    """
    Gets information for first i climbers in matrix
    :param matrix: matrix of information where each row corresponds to a climber (ranks, points, tops, attempts, holds...)
    :param i: number of rows of information to preserve
    :return: matrix with len(matrix)-i rows chopped off
    """
    newMatrix = np.zeros(shape = (i, len(matrix[0])))
    for row in range(0,i):
        for col in range(0,len(matrix[0])):
            newMatrix[row][col] = matrix[row][col]
    return newMatrix

def createDataSet(cat, round, allData, *args):
    """
    Creates a new ClimbingRanker for the subset of data
    :param cat: category
    :param round:  round of competition (qualis, semis, finals)
    :param allData: ClimbingRanker that corresponds to all the data
    :param args: indices of climbers we want in subset
    :return: new ClimbingRanker for the subset of the data
    """
    climbers = []
    numProblems = allData.numProblems
    ranks = []
    tops = []
    attempts = []
    attemptsPerProblem = []
    points = []
    pointsPerProblem = []
    topsPerProblem = []
    for index in args:
        climbers.append(allData.climbers[index])
        ranks.append(allData.ranks[index])
        tops.append(allData.tops[index])
        attempts.append(allData.attempts[index])
        attemptsPerProblem.append(allData.attemptsPerProblem[index])
        points.append(allData.points[index])
        pointsPerProblem.append(allData.pointsPerProblem[index])
        topsPerProblem.append(allData.topsPerProblem[index])
    #make ranks complete ranks
    ranks = lp.flipRankings(ranks)
    for i in range(0, len(ranks)):
        ranks[i] = lp.makeRank(ranks[i])
    ranks = lp.flipRankings(ranks)
    return ClimbingRanker("", [climbers, numProblems, ranks, tops, attempts, attemptsPerProblem, points, pointsPerProblem, topsPerProblem, cat, round, False])

def testIndependence2(methodNum): #randomly choose 2 climbers and see if rank is affected by introduction of third climber
    """
    Randomly chooses two climbers, ranks them according to the method, then adds a third climber and sees if the rank
    of the first two climbers is affected by the addition of the third climber
    :param methodNum: number of method to be tested
    """
    categories = ["fya", "fyb", "fyc", "fyd", "mya", "myb", "myc", "myd"]
    done = False
    for cat in categories:
        try:
            dataQualis = ClimbingRanker(cat + "BNatsQualis2016.csv")
            for i,j in combinations(range(len(dataQualis.climbers)),2): #find first 2 climbers to rank
                if(not(done)):
                    for k in range(0, len(dataQualis.climbers)): #see if including climber k changes the rank of the first two climbers
                        if(k == i or k == j):
                            continue
                        data2 = createDataSet(cat, "Qualis", dataQualis, i,j) #create ClimbingRanker for i and j
                        data3 = createDataSet(cat, "Qualis", dataQualis, i,j,k) #create ClimbingRanker for all three
                        try:
                            rank2 = data2.runMethod(methodNum)
                            rank3 = data3.runMethod(methodNum)
                            sign2 = np.sign(rank2[0]-rank2[1])
                            sign3 = np.sign(rank3[0]-rank3[1])
                            if(sign2 != 0 and sign3 != 0 and not(sign2 == sign3)): #i and j flipped order with introduction of climber k
                                print(rmc.getMethod(methodNum), " is not independent for ", cat, "qualis: ", rank2, rank3)
                                print(data2.climbers, data3.climbers)
                                print(data2.ranks, data3.ranks)
                                done=  True
                                break
                        except ZeroDivisionError as e:
                            #print(e)
                            x=1
        except ValueError as v:
            #print(v)
            x=1
        if(not(done)): #now look at semis if nothing was found in qualis
            print("testing semis")
            try:
                dataSemis = ClimbingRanker(cat + "BNatsSemis2016.csv")
                for i,j in combinations(range(len(dataSemis.climbers)),2):
                    if(not(done)):
                        for k in range(0, len(dataSemis.climbers)):
                            if(k == i or k == j):
                                continue
                            data2 = createDataSet(cat, "Semis", dataSemis, i,j)
                            data3 = createDataSet(cat, "Semis", dataSemis, i,j,k)
                            try:
                                rank2 = data2.runMethod(methodNum)
                                rank3 = data3.runMethod(methodNum)
                                sign2 = np.sign(rank2[0]-rank2[1])
                                sign3 = np.sign(rank3[0]-rank3[1])
                                if(sign2 != 0 and sign3 != 0 and sign2 != sign3):
                                    print(rmc.getMethod(methodNum), " is not independent for ", cat, "semis: ", rank2, rank3)
                                    print(data2.climbers, data3.climbers)
                                    print(data2.ranks, data3.ranks)
                                    done = True
                                    break
                            except ZeroDivisionError as e:
                                #print(e)
                                x=1
            except ValueError as v:
                #print(v)
                x=1
        if(not(done)): #look in finals if not failure to meet independence criterion has been found
            print("testing finals")
            try:
                dataFinals = ClimbingRanker(cat + "BNatsFinals2016.csv")
                for i,j in combinations(range(len(dataFinals.climbers)),2):
                    if(not(done)):
                        for k in range(0, len(dataFinals.climbers)):
                            if(k == i or k == j):
                                continue
                            data2 = createDataSet(cat, "Finals", dataFinals, i,j)
                            data3 = createDataSet(cat, "Finals", dataFinals, i,j,k)
                            try:
                                rank2 = data2.runMethod(methodNum)
                                rank3 = data3.runMethod(methodNum)
                                sign2 = np.sign(rank2[0]-rank2[1])
                                sign3 = np.sign(rank3[0]-rank3[1])
                                if(sign2 != 0 and sign3 != 0 and not(sign2 == sign3)):
                                    print(rmc.getMethod(methodNum), " is not independent for", cat, "finals: ", rank2, rank3)
                                    print(data2.climbers, data3.climbers)
                                    done = True
                                    break
                            except ZeroDivisionError as e:
                                #print(e)
                                x=1
            except ValueError as v:
                #print(v)
                x=1
    if(not(done)):
        print(rmc.getMethod(methodNum), " might be independent")


independentMethods = [8,9,10]
#14 for all methods
topsMethods = [1,2,4,7,11,12,14] #that aren't independent
#for i in topsMethods: #loop through all methods and see if independent
testIndependence2(12)
testIndependence2(11)
