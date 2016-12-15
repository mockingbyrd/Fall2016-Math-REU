from ReadInData import ClimbingDataFile
import numpy as np
from itertools import combinations

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


