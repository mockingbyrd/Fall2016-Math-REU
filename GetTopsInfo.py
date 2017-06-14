from ReadInData import ClimbingDataFile
import numpy as np
from itertools import combinations
import csv

def getTopsInfo(points, tops):
    """
    takes total number of tops and points matrix and uses that information to figure out which climbers topped which
    problems (not always possible to determine)
    :param points: numpy matrix where each entry is the number of points (holds) a climber got on the specific problem
    (rows = climbers, columns = problem)
    :param tops: 1D list with total number of tops for each climber
    :return: numpy matrix where each entry is a 1 if the climber topped that problem and a 0 otherwise
    :raise: ValueError if tops data couldn't be determined
    """
    numProblems = len(points[0])
    numClimbers = len(points)
    if(tops[0] == numProblems): #someone topped every problem
        problemPoints = []
        for p in points[0]:
            problemPoints.append(p)
        return getProblemTops(problemPoints, points, numClimbers, numProblems)
    elif(tops[0] == numProblems-1): #no one climber topped every problem
        pMaxPoints = [] #find the maximum number of points obtained for each problem
        for problem in range(0, numProblems):
            pMaxPoints.append(getMaxIndices(problem, points))
        problemTopsAllProblemsTopped = getProblemTops(pMaxPoints, points, numClimbers, numProblems) #if each problem was topped
        problemTopsOneNotTopped = [] #one problem not topped, problemTops calculated for each possible problem
        for problem in range(0, numProblems):
            pPoints = pMaxPoints.copy()
            pPoints[problem] += 1
            problemTopsOneNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        validProblemTops = [] #will keep track of all possible problemTops that are valid (hopefully only one)
        if(testValidity(problemTopsAllProblemsTopped, tops, numClimbers, numProblems)):
            validProblemTops.append(problemTopsAllProblemsTopped)
        for problemTops in problemTopsOneNotTopped:
            if(testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        if(len(validProblemTops) == 1):
            return validProblemTops[0]
        else:
            raise ValueError("couldn't determine tops data") #inconclusive
    elif(tops[0] == numProblems-2): #climber with highest number of tops didn't top two problems
        pMaxPoints = []  # find the maximum number of points obtained for each problem
        for problem in range(0, numProblems):
            pMaxPoints.append(getMaxIndices(problem, points))
        problemTopsAllProblemsTopped = getProblemTops(pMaxPoints, points, numClimbers, numProblems)  # if each problem was topped
        problemTopsOneNotTopped = []  # one problem not topped, problemTops calculated for each possible problem
        for problem in range(0, numProblems):
            pPoints = pMaxPoints.copy()
            pPoints[problem] += 1
            problemTopsOneNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        problemTopsTwoNotTopped = [] #two problems not topped, problemTops calculated for each possible combination of problems
        for i,j in combinations(range(numProblems),2):
            pPoints = pMaxPoints.copy()
            pPoints[i] += 1
            pPoints[j] += 1
            problemTopsTwoNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        validProblemTops = []  # will keep track of all possible problemTops that are valid (hopefully only one)
        if (testValidity(problemTopsAllProblemsTopped, tops, numClimbers, numProblems)):
            validProblemTops.append(problemTopsAllProblemsTopped)
        for problemTops in problemTopsOneNotTopped:
            if (testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        for problemTops in problemTopsTwoNotTopped:
            if (testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        if (len(validProblemTops) == 1):
            return validProblemTops[0]
        else:
            raise ValueError("couldn't determine tops data")  # inconclusive
    elif(tops[0] == numProblems-3): #climber with highest number of tops didn't top 3 problems
        pMaxPoints = []  # find the maximum number of points obtained for each problem
        for problem in range(0, numProblems):
            pMaxPoints.append(getMaxIndices(problem, points))
        problemTopsAllProblemsTopped = getProblemTops(pMaxPoints, points, numClimbers, numProblems)  # if each problem was topped
        problemTopsOneNotTopped = []  # one problem not topped, problemTops calculated for each possible problem
        for problem in range(0, numProblems):
            pPoints = pMaxPoints.copy()
            pPoints[problem] += 1
            problemTopsOneNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        problemTopsTwoNotTopped = []  # two problems not topped, problemTops calculated for each possible combination of problems
        for i, j in combinations(range(numProblems), 2):
            pPoints = pMaxPoints.copy()
            pPoints[i] += 1
            pPoints[j] += 1
            problemTopsTwoNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        problemTopsThreeNotTopped = [] #three problems not topped, problem tops calculated for each possible combination of problems
        for i, j, k in combinations(range(numProblems), 3):
            pPoints = pMaxPoints.copy()
            pPoints[i] += 1
            pPoints[j] += 1
            pPoints[k] += 1
            problemTopsThreeNotTopped.append(getProblemTops(pPoints, points, numClimbers, numProblems))
        validProblemTops = []  # will keep track of all possible problemTops that are valid (hopefully only one)
        if (testValidity(problemTopsAllProblemsTopped, tops, numClimbers, numProblems)):
            validProblemTops.append(problemTopsAllProblemsTopped)
        for problemTops in problemTopsOneNotTopped:
            if (testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        for problemTops in problemTopsTwoNotTopped:
            if (testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        for problemTops in problemTopsThreeNotTopped:
            if (testValidity(problemTops, tops, numClimbers, numProblems)):
                validProblemTops.append(problemTops)
        if (len(validProblemTops) == 1):
            return validProblemTops[0]
        else:
            raise ValueError("couldn't determine tops data")  # inconclusive
    elif(tops[0] == 0):
        return np.zeros(shape=(numClimbers, numProblems))
    else:
        print("need more cases")

def testValidity(problemTops, tops, numClimbers, numProblems):
    """
    tests to see if giving climbers these tops per problem creates the correct total numbers of tops
    :param problemTops: numpy matrix where each entry is a 1 if the climber topped the problem and a 0 otherwise
    (rows = climbers, columns = problems)
    :param tops: lD list where each entry is total number of tops for that climber
    :param numClimbers: number of climbers in this data
    :param numProblems: number of problems in this data
    :return: True if this problemTops matrix results in each climber having the correct number of total tops, False otherwise
    """
    for climber in range(numClimbers):
        sum = 0
        for problem in range(numProblems): #add up number of tops the climber got based on the problemTops
            sum += problemTops[climber][problem]
        if(sum != tops[climber]): #if the calculated number of tops is not correct, the problemTops is incorrect
            return False
    return True

def getProblemTops(problemPoints, points, numClimbers, numProblems):
    """
    :param problemPoints: 1D list of length numProblems where each entry is the number of points required to have topped a problem
    :param points: numpy matrix where each entry is the number of points (holds) a climber got on the specific problem
    (rows = climbers, columns = problem)
    :param numClimbers: number of climbers in this data
    :param numProblems: number of problems in this data
    :return: numpy matrix where each entry is a 1 if the climber topped the problem and a 0 otherwise
    (rows = climbers, columns = problems)
    """
    problemTops = np.zeros(shape=(numClimbers, numProblems))
    for row in range(0, numClimbers):
        for col in range(0, numProblems):
            if (points[row][col] == problemPoints[col]): #climber topped the problem
                problemTops[row][col] = 1
            else: #climber didn't top the problem
                problemTops[row][col] = 0
    return problemTops

def getMaxIndices(column, points):
    """
    :param column: column where you want to find the maximum value
    :param points: numpy matrix where you want to find the maximum value in the specified column
    :return: the max value in the specified column
    """
    maxIndices = [0] #keeps track of indices with that maximum value - not used right now but could be if so desired
    max = points[0][column] #maximum value in the column of points matrix
    for i in range(1,len(points)):
        if(points[i][column] == points[maxIndices[0]][column]):
            maxIndices.append(i)
        elif(points[i][column] > points[maxIndices[0]][column]):
            maxIndices = [i]
            max = points[i][column]

    return max


def getMaxPointsInfo(pointsPerProblem, topsList):
    """
    Creates a vector of the maximum number of points possible for each problem (if it can be determined)
    :param pointsPerProblem: matrix of points per problem for each climber (rows = climbers)
    :param topsList: vector with the number of tops for each climber
    :return: max points vector, throws an error if topsPerProblem cannot be determined, and has a -1 in the vector if
    no climber topped that problem.
    """
    topsPerProblem = getTopsInfo(pointsPerProblem, topsList)
    maxPoints = [None]*len(pointsPerProblem[0])
    for problemIndex in range(0, len(pointsPerProblem[0])):
        for climberIndex in range(0, len(pointsPerProblem)):
            if(topsPerProblem[climberIndex][problemIndex] == 1):
                maxPoints[problemIndex] = pointsPerProblem[climberIndex][problemIndex]
                break
    return maxPoints

def writeToFile(files, listOfMaxPoints, fileName, numProblems):
    """
    Writes the results to a csv file
    :param files: list of the files we got max point info for
    :param listOfMaxPoints: 2D list of max point for each file
    :param fileName: name of the file to write the results to
    """
    with open(fileName, 'w') as csvfile:
        writer = csv.writer(csvfile)
        if(numProblems == 4):
            writer.writerow(['file', 'maxPointsP1', 'maxPointsP2', 'maxPointsP3', 'maxPointsP4'])
            for index in range(0, len(files)):
                writer.writerow([files[index], listOfMaxPoints[index][0], listOfMaxPoints[index][1],
                                 listOfMaxPoints[index][2], listOfMaxPoints[index][3]])
        elif(numProblems == 3):
            writer.writerow(['file', 'maxPointsP1', 'maxPointsP2', 'maxPointsP3'])
            for index in range(0, len(files)):
                writer.writerow([files[index], listOfMaxPoints[index][0], listOfMaxPoints[index][1],
                                 listOfMaxPoints[index][2]])
        else:
            raise ValueError("cannot write to file with this number of tops")

#data = ClimbingDataFile('fyaBNatsQualis2016.csv', 0)
#print("max points", getMaxPointsInfo(data.getPointsPerProblem(), data.getTops()))
#qualisfiles = ['fyaBNatsQualis2016.csv', 'fybBNatsQualis2016.csv', 'fycBNatsQualis2016.csv',
#                'fydBNatsQualis2016.csv', 'myaBNatsQualis2016.csv', 'mybBNatsQualis2016.csv',
#                 'mycBNatsQualis2016.csv', 'mydBNatsQualis2016.csv']
# semisfiles = ['fyaBNatsSemis2016.csv', 'fybBNatsSemis2016.csv', 'fycBNatsSemis2016.csv',
#                 'fydBNatsSemis2016.csv', 'myaBNatsSemis2016.csv', 'mybBNatsSemis2016.csv',
#                 'mycBNatsSemis2016.csv', 'mydBNatsSemis2016.csv']
# finalsfiles = ['fyaBNatsFinals2016.csv', 'fybBNatsFinals2016.csv', 'fycBNatsFinals2016.csv',
#                 'fydBNatsFinals2016.csv', 'myaBNatsFinals2016.csv', 'mybBNatsFinals2016.csv',
#                 'mycBNatsFinals2016.csv', 'mydBNatsFinals2016.csv']
# listOfMaxPoints = []
# for file in qualisfiles:
#     data = ClimbingDataFile(file, 0)
#     listOfMaxPoints.append(getMaxPointsInfo(data.getPointsPerProblem(), data.getTops()))
# print(listOfMaxPoints)
# writeToFile(qualisfiles, listOfMaxPoints, "qualisMaxPoints.csv", 4)
#
# listOfMaxPoints = []
# for file in semisfiles:
#     data = ClimbingDataFile(file, 0)
#     listOfMaxPoints.append(getMaxPointsInfo(data.getPointsPerProblem(), data.getTops()))
# print(listOfMaxPoints)
# writeToFile(semisfiles, listOfMaxPoints, "semisMaxPoints.csv", 3)
#
# listOfMaxPoints = []
# for file in finalsfiles:
#     data = ClimbingDataFile(file, 0)
#     listOfMaxPoints.append(getMaxPointsInfo(data.getPointsPerProblem(), data.getTops()))
# print(listOfMaxPoints)
# writeToFile(finalsfiles, listOfMaxPoints, "finalsMaxPoints.csv", 3)
#

points = [[15,20,10],[12,20,17],[11,20,5]]
tops = [2,2,1]
print(getTopsInfo(points,tops))